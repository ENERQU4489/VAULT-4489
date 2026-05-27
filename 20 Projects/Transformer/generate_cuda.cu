#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <cuda_runtime.h>
#include <cublas_v2.h>

#define BLOCK_SIZE 64    
#define N_EMBD 512       
#define N_LAYER 6        
#define VOCAB_SIZE 4096  
#define EPSILON 1e-5f

#define CHECK_CUDA(call) { \
    cudaError_t err = call; \
    if (err != cudaSuccess) { printf("CUDA Error: %s at line %d\n", cudaGetErrorString(err), __LINE__); exit(1); } \
}

typedef struct { float *data; int rows, cols; } Tensor;
typedef struct { Tensor wte, wpe, head; Tensor *ln1_g, *ln1_b, *qkv_w; } GPT;

char** vocab;

void load_vocab(const char* path) {
    FILE* f = fopen(path, "rb");
    int count; fread(&count, 4, 1, f);
    vocab = (char**)malloc(count * sizeof(char*));
    for (int i = 0; i < count; i++) {
        int len; fread(&len, 4, 1, f);
        vocab[i] = (char*)malloc(len + 1);
        fread(vocab[i], 1, len, f);
        vocab[i][len] = '\0';
    }
    fclose(f);
}

void gemm(cublasHandle_t h, bool tA, bool tB, int m, int n, int k, float alpha, float* A, float* B, float beta, float* C) {
    cublasOperation_t opA = tA ? CUBLAS_OP_T : CUBLAS_OP_N;
    cublasOperation_t opB = tB ? CUBLAS_OP_T : CUBLAS_OP_N;
    cublasSgemm(h, opA, opB, m, n, k, &alpha, A, tA ? k : m, B, tB ? n : k, &beta, C, m);
}

// Kernels... (uproszczone do forward)
__global__ void embedding_forward_kernel(float* out, int* input, float* wte, float* wpe, int n_embd, int b_size) {
    int pos = blockIdx.x; int tid = threadIdx.x;
    if (pos < b_size && tid < n_embd) {
        int token = input[pos];
        out[pos * n_embd + tid] = wte[token * n_embd + tid] + wpe[pos * n_embd + tid];
    }
}

__global__ void layernorm_forward_kernel(float* out, float* in, float* g, float* b, int n) {
    int row_idx = blockIdx.x;
    float* x = in + row_idx * n; float* y = out + row_idx * n;
    float mean = 0; for (int i = 0; i < n; i++) mean += x[i]; mean /= n;
    float var = 0; for (int i = 0; i < n; i++) var += (x[i] - mean) * (x[i] - mean); var /= n;
    float inv_std = 1.0f / sqrtf(var + EPSILON);
    int t = threadIdx.x;
    if (t < n) y[t] = (x[t] - mean) * inv_std * g[t] + b[t];
}

__global__ void softmax_causal_kernel(float* scores, int b_size) {
    int row = blockIdx.x;
    float* r = scores + row * b_size;
    float max_val = -1e20; for (int i = 0; i <= row; i++) if (r[i] > max_val) max_val = r[i];
    float sum = 0; for (int i = 0; i <= row; i++) { r[i] = expf(r[i] - max_val); sum += r[i]; }
    for (int i = 0; i < b_size; i++) r[i] = (i <= row) ? (r[i] / (sum + 1e-10f)) : 0;
}

void load_tensor(FILE* f, Tensor t) {
    float* h = (float*)malloc(t.rows * t.cols * 4);
    fread(h, 4, t.rows * t.cols, f);
    cudaMemcpy(t.data, h, t.rows * t.cols * 4, cudaMemcpyHostToDevice);
    free(h);
}

int main() {
    cublasHandle_t handle; cublasCreate(&handle);
    GPT model;
    load_vocab("vocab.bin");
    
    cudaMalloc(&model.wte.data, VOCAB_SIZE * N_EMBD * 4); model.wte.rows = VOCAB_SIZE; model.wte.cols = N_EMBD;
    cudaMalloc(&model.wpe.data, BLOCK_SIZE * N_EMBD * 4); model.wpe.rows = BLOCK_SIZE; model.wpe.cols = N_EMBD;
    cudaMalloc(&model.head.data, N_EMBD * VOCAB_SIZE * 4); model.head.rows = N_EMBD; model.head.cols = VOCAB_SIZE;
    model.qkv_w = (Tensor*)malloc(N_LAYER * sizeof(Tensor));
    model.ln1_g = (Tensor*)malloc(N_LAYER * sizeof(Tensor));
    model.ln1_b = (Tensor*)malloc(N_LAYER * sizeof(Tensor));
    for (int i = 0; i < N_LAYER; i++) {
        cudaMalloc(&model.qkv_w[i].data, N_EMBD * 3 * N_EMBD * 4); model.qkv_w[i].rows = N_EMBD; model.qkv_w[i].cols = 3 * N_EMBD;
        cudaMalloc(&model.ln1_g[i].data, N_EMBD * 4); model.ln1_g[i].rows = 1; model.ln1_g[i].cols = N_EMBD;
        cudaMalloc(&model.ln1_b[i].data, N_EMBD * 4); model.ln1_b[i].rows = 1; model.ln1_b[i].cols = N_EMBD;
    }

    FILE* fw = fopen("model_weights.bin", "rb");
    if(fw) {
        load_tensor(fw, model.wte); load_tensor(fw, model.wpe); load_tensor(fw, model.head);
        for(int i=0; i<N_LAYER; i++) { load_tensor(fw, model.qkv_w[i]); load_tensor(fw, model.ln1_g[i]); load_tensor(fw, model.ln1_b[i]); }
        fclose(fw);
    }

    float *d_x, *d_ln, *d_qkv, *d_attn, *d_logits;
    cudaMalloc(&d_x, BLOCK_SIZE * N_EMBD * 4); cudaMalloc(&d_ln, BLOCK_SIZE * N_EMBD * 4);
    cudaMalloc(&d_qkv, BLOCK_SIZE * 3 * N_EMBD * 4); cudaMalloc(&d_attn, BLOCK_SIZE * BLOCK_SIZE * 4);
    cudaMalloc(&d_logits, VOCAB_SIZE * 4);
    int* d_input; cudaMalloc(&d_input, BLOCK_SIZE * 4);

    int cur_tokens[BLOCK_SIZE] = {0}; 
    int history[100] = {0};
    float alpha = 1.0f, beta = 0.0f;

    printf("\nResponse: ");
    for (int i = 0; i < 40; i++) {
        cudaMemcpy(d_input, cur_tokens, BLOCK_SIZE * 4, cudaMemcpyHostToDevice);
        embedding_forward_kernel<<<BLOCK_SIZE, N_EMBD>>>(d_x, d_input, model.wte.data, model.wpe.data, N_EMBD, BLOCK_SIZE);
        for (int l = 0; l < N_LAYER; l++) {
            layernorm_forward_kernel<<<BLOCK_SIZE, N_EMBD>>>(d_ln, d_x, model.ln1_g[l].data, model.ln1_b[l].data, N_EMBD);
            cublasSgemm(handle, CUBLAS_OP_N, CUBLAS_OP_N, 3 * N_EMBD, BLOCK_SIZE, N_EMBD, &alpha, model.qkv_w[l].data, 3 * N_EMBD, d_ln, N_EMBD, &beta, d_qkv, 3 * N_EMBD);
            softmax_causal_kernel<<<BLOCK_SIZE, 1>>>(d_attn, BLOCK_SIZE);
            gemm(handle, false, false, N_EMBD, BLOCK_SIZE, BLOCK_SIZE, 1.0f, d_qkv+2*N_EMBD, d_attn, 1.0f, d_x);
        }
        cublasSgemm(handle, CUBLAS_OP_N, CUBLAS_OP_N, VOCAB_SIZE, 1, N_EMBD, &alpha, model.head.data, VOCAB_SIZE, d_x + (BLOCK_SIZE-1)*N_EMBD, N_EMBD, &beta, d_logits, VOCAB_SIZE);
        
        float h_l[VOCAB_SIZE]; cudaMemcpy(h_l, d_logits, VOCAB_SIZE * 4, cudaMemcpyDeviceToHost);
        
        // Repetition Penalty (Silny)
        for(int j=0; j<i && j<100; j++) h_l[history[j]] -= 5.0f;

        int next = 0;
        float temp = 0.7f;
        float sum = 0; for(int j=0; j<VOCAB_SIZE; j++) { h_l[j] = expf(h_l[j]/temp); sum += h_l[j]; }
        float r = (float)rand() / (float)RAND_MAX * sum;
        float acc = 0; for(int j=0; j<VOCAB_SIZE; j++) { acc += h_l[j]; if(acc >= r) { next = j; break; } }

        printf("%s ", vocab[next]);
        history[i % 100] = next;
        for(int j=0; j<BLOCK_SIZE-1; j++) cur_tokens[j] = cur_tokens[j+1]; cur_tokens[BLOCK_SIZE-1] = next;
    }
    printf("\n");
    cublasDestroy(handle); return 0;
}
