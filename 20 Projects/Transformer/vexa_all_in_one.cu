#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <cuda_runtime.h>
#include <cuda_fp16.h>
#include <cublas_v2.h>
#include "vocab_size.h"

#define BATCH_SIZE 8     
#define BLOCK_SIZE 16    
#define N_EMBD 256       
#define N_LAYER 4        
#define LEARNING_RATE 0.0005f

#define CHECK_CUDA(call) { cudaError_t err = call; if (err != cudaSuccess) { printf("CUDA Error: %s\n", cudaGetErrorString(err)); exit(1); } }

typedef struct { half *data, *grad; float *m, *v; int r, c; } Tensor;
typedef struct { Tensor wte, head, *qkv_w, *ln_g; } VexaGPT;

char** vocab_map;

// --- KERNELS ---
__global__ void embedding_forward(half* out, int* input, half* wte, int n_embd, int b_size, int batch) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < batch * b_size * n_embd) out[idx] = wte[input[idx / n_embd] * n_embd + (idx % n_embd)];
}

__global__ void softmax_loss_grad_all(half* grad, half* logits, int* targets, int vocab, int batch, int block) {
    int b = blockIdx.y;
    int s = blockIdx.x;
    if (b < batch && s < block) {
        half* l = logits + (b * block + s) * vocab;
        half* g = grad + (b * block + s) * vocab;
        int target = targets[b * block + s];
        float max_v = -1e20;
        for(int i=0; i<vocab; i++) { float v = __half2float(l[i]); if(v > max_v) max_v = v; }
        float sum = 0;
        for(int i=0; i<vocab; i++) { float v = expf(__half2float(l[i]) - max_v); sum += v; g[i] = __float2half(v); }
        for(int i=0; i<vocab; i++) g[i] = __float2half((__half2float(g[i])/sum) - (i == target ? 1.0f : 0.0f));
    }
}

__global__ void adamw_step(half* d, half* g, float* m, float* v, int n, float lr, int t) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) {
        float grad = __half2float(g[i]);
        m[i] = 0.9f * m[i] + 0.1f * grad;
        v[i] = 0.95f * v[i] + 0.05f * grad * grad;
        float m_h = m[i] / (1.0f - powf(0.9f, t));
        float v_h = v[i] / (1.0f - powf(0.95f, t));
        d[i] = __float2half(__half2float(d[i]) - lr * m_h / (sqrtf(v_h) + 1e-8f));
        g[i] = __float2half(0);
    }
}

Tensor create_t(int r, int c) {
    Tensor t; t.r = r; t.c = c; size_t s16 = r*c*2, s32 = r*c*4;
    cudaMalloc(&t.data, s16); cudaMalloc(&t.grad, s16); cudaMalloc(&t.m, s32); cudaMalloc(&t.v, s32);
    cudaMemset(t.data, 0, s16); cudaMemset(t.grad, 0, s16); cudaMemset(t.m, 0, s32); cudaMemset(t.v, 0, s32);
    return t;
}

void load_vocab() {
    FILE* f = fopen("vocab.bin", "rb");
    int count; fread(&count, 4, 1, f); vocab_map = (char**)malloc(count * sizeof(char*));
    for (int i = 0; i < count; i++) { int len; fread(&len, 4, 1, f); vocab_map[i] = (char*)malloc(len + 1); fread(vocab_map[i], 1, len, f); vocab_map[i][len] = '\0'; }
    fclose(f);
}

int main() {
    srand(4489); cublasHandle_t handle; cublasCreate(&handle); load_vocab();
    VexaGPT model;
    model.wte = create_t(VOCAB_SIZE, N_EMBD); model.head = create_t(N_EMBD, VOCAB_SIZE);
    float s = 0.05f; half* h_w = (half*)malloc(VOCAB_SIZE*N_EMBD*2);
    for(int i=0; i<VOCAB_SIZE*N_EMBD; i++) h_w[i] = __float2half(((float)rand()/RAND_MAX-0.5f)*s);
    cudaMemcpy(model.wte.data, h_w, VOCAB_SIZE*N_EMBD*2, cudaMemcpyHostToDevice);
    cudaMemcpy(model.head.data, h_w, N_EMBD*VOCAB_SIZE*2, cudaMemcpyHostToDevice);

    model.qkv_w = (Tensor*)malloc(N_LAYER * sizeof(Tensor));
    for(int i=0; i<N_LAYER; i++) model.qkv_w[i] = create_t(N_EMBD, 3*N_EMBD);

    FILE* fd = fopen("data.bin", "rb"); fseek(fd, 0, SEEK_END); int nt = ftell(fd)/4; fseek(fd, 0, SEEK_SET);
    int* h_tokens = (int*)malloc(nt*4); fread(h_tokens, 4, nt, fd); fclose(fd);

    half *d_x, *d_qkv, *d_grad_logits, *d_logits_h;
    cudaMalloc(&d_x, BATCH_SIZE*BLOCK_SIZE*N_EMBD*2);
    cudaMalloc(&d_qkv, BATCH_SIZE*BLOCK_SIZE*3*N_EMBD*2);
    cudaMalloc(&d_grad_logits, BATCH_SIZE*BLOCK_SIZE*VOCAB_SIZE*2);
    cudaMalloc(&d_logits_h, BATCH_SIZE*BLOCK_SIZE*VOCAB_SIZE*2);
    int* d_input; cudaMalloc(&d_input, BATCH_SIZE*BLOCK_SIZE*4);

    float alpha = 1.0f, beta = 0.0f;
    printf("Vexa-C Zenith: ULTIMATE TRAINING (RTX 4070)\n");
    for(int e=1; e<=500; e++) {
        for(int i=0; i<nt-BATCH_SIZE*BLOCK_SIZE-1; i+=BATCH_SIZE*BLOCK_SIZE) {
            cudaMemcpy(d_input, &h_tokens[i], BATCH_SIZE*BLOCK_SIZE*4, cudaMemcpyHostToDevice);
            embedding_forward<<<(BATCH_SIZE*BLOCK_SIZE*N_EMBD+255)/256, 256>>>(d_x, d_input, model.wte.data, N_EMBD, BLOCK_SIZE, BATCH_SIZE);
            for(int l=0; l<N_LAYER; l++) {
                cublasGemmEx(handle, CUBLAS_OP_N, CUBLAS_OP_N, 3*N_EMBD, BATCH_SIZE*BLOCK_SIZE, N_EMBD, &alpha, model.qkv_w[l].data, CUDA_R_16F, 3*N_EMBD, d_x, CUDA_R_16F, N_EMBD, &beta, d_qkv, CUDA_R_16F, 3*N_EMBD, CUBLAS_COMPUTE_32F, CUBLAS_GEMM_DEFAULT_TENSOR_OP);
                cudaMemcpy(d_x, d_qkv, BATCH_SIZE*BLOCK_SIZE*N_EMBD*2, cudaMemcpyDeviceToDevice);
            }
            cublasGemmEx(handle, CUBLAS_OP_N, CUBLAS_OP_N, VOCAB_SIZE, BATCH_SIZE*BLOCK_SIZE, N_EMBD, &alpha, model.head.data, CUDA_R_16F, VOCAB_SIZE, d_x, CUDA_R_16F, N_EMBD, &beta, d_logits_h, CUDA_R_16F, VOCAB_SIZE, CUBLAS_COMPUTE_32F, CUBLAS_GEMM_DEFAULT_TENSOR_OP);
            softmax_loss_grad_all<<<dim3(BLOCK_SIZE, BATCH_SIZE), 1>>>(d_grad_logits, d_logits_h, d_input, VOCAB_SIZE, BATCH_SIZE, BLOCK_SIZE);
            cublasGemmEx(handle, CUBLAS_OP_N, CUBLAS_OP_T, VOCAB_SIZE, N_EMBD, BATCH_SIZE*BLOCK_SIZE, &alpha, d_grad_logits, CUDA_R_16F, VOCAB_SIZE, d_x, CUDA_R_16F, N_EMBD, &alpha, model.head.grad, CUDA_R_16F, VOCAB_SIZE, CUBLAS_COMPUTE_32F, CUBLAS_GEMM_DEFAULT_TENSOR_OP);
            adamw_step<<<(N_EMBD*VOCAB_SIZE+255)/256, 256>>>(model.head.data, model.head.grad, model.head.m, model.head.v, N_EMBD*VOCAB_SIZE, LEARNING_RATE, e);
        }
        if(e%100==0) printf("Epoch %d processed.\n", e);
    }

    printf("\nResponse: ");
    int t_seq[BLOCK_SIZE] = {1, 0, 0}; 
    for(int i=0; i<15; i++) {
        cudaMemcpy(d_input, t_seq, BLOCK_SIZE*4, cudaMemcpyHostToDevice);
        embedding_forward<<<(BLOCK_SIZE*N_EMBD+255)/256, 256>>>(d_x, d_input, model.wte.data, N_EMBD, BLOCK_SIZE, 1);
        cublasGemmEx(handle, CUBLAS_OP_N, CUBLAS_OP_N, VOCAB_SIZE, 1, N_EMBD, &alpha, model.head.data, CUDA_R_16F, VOCAB_SIZE, d_x + (BLOCK_SIZE-1)*N_EMBD, CUDA_R_16F, N_EMBD, &beta, d_logits_h, CUDA_R_16F, VOCAB_SIZE, CUBLAS_COMPUTE_32F, CUBLAS_GEMM_DEFAULT_TENSOR_OP);
        half h_l[VOCAB_SIZE]; cudaMemcpy(h_l, d_logits_h, VOCAB_SIZE*2, cudaMemcpyDeviceToHost);
        int next = 0; float bv = -1e20;
        for(int j=1; j<VOCAB_SIZE; j++) {
            float val = __half2float(h_l[j]);
            if(val > bv) { bv = val; next = j; }
        }
        printf("%s ", vocab_map[next]);
        for(int j=0; j<BLOCK_SIZE-1; j++) t_seq[j] = t_seq[j+1]; t_seq[BLOCK_SIZE-1] = next;
    }
    printf("\n");
    return 0;
}
