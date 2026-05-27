#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <cuda_runtime.h>
#include <cublas_v2.h>

#define BATCH_SIZE 64    
#define BLOCK_SIZE 64    
#define N_EMBD 512       
#define N_LAYER 6        
#define VOCAB_SIZE 2048  
#define LEARNING_RATE 0.0001f
#define EPSILON 1e-5f

#define CHECK_CUDA(call) { \
    cudaError_t err = call; \
    if (err != cudaSuccess) { printf("CUDA Error: %s at line %d\n", cudaGetErrorString(err), __LINE__); exit(1); } \
}

typedef struct { float *data, *grad, *m, *v; int rows, cols; } Tensor;
typedef struct { Tensor wte, wpe, head; Tensor *ln1_g, *ln1_b, *qkv_w; } GPT;

// --- KERNELS ---

__global__ void embedding_batch_kernel(float* out, int* input, float* wte, float* wpe, int n_embd, int b_size, int batch) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    int total = batch * b_size * n_embd;
    if (idx < total) {
        int b = idx / (b_size * n_embd);
        int s = (idx / n_embd) % b_size;
        int e = idx % n_embd;
        int token = input[b * b_size + s];
        out[idx] = wte[token * n_embd + e] + wpe[s * n_embd + e];
    }
}

__global__ void layernorm_batch_kernel(float* out, float* in, float* g, float* b, int n, int total_rows) {
    int row_idx = blockIdx.x;
    if (row_idx < total_rows) {
        float* x = in + row_idx * n; float* y = out + row_idx * n;
        float mean = 0; for (int i = 0; i < n; i++) mean += x[i]; mean /= n;
        float var = 0; for (int i = 0; i < n; i++) var += (x[i] - mean) * (x[i] - mean); var /= n;
        float inv_std = 1.0f / sqrtf(var + EPSILON);
        int t = threadIdx.x;
        if (t < n) y[t] = (x[t] - mean) * inv_std * g[t] + b[t];
    }
}

__global__ void softmax_causal_batch_kernel(float* scores, int b_size, int batch) {
    int b = blockIdx.y; int row = blockIdx.x;
    if (b < batch && row < b_size) {
        float* r = scores + b * b_size * b_size + row * b_size;
        float max_val = -1e20; for (int i = 0; i <= row; i++) if (r[i] > max_val) max_val = r[i];
        float sum = 0; for (int i = 0; i <= row; i++) { r[i] = expf(r[i] - max_val); sum += r[i]; }
        for (int i = 0; i < b_size; i++) r[i] = (i <= row) ? (r[i] / (sum + 1e-10f)) : 0;
    }
}

__global__ void cross_entropy_grad_batch_kernel(float* grad, float* probs, int* targets, int vocab_size, int batch, int b_size) {
    int b = blockIdx.y;
    int idx = threadIdx.x;
    if (b < batch && idx < vocab_size) {
        int target = targets[b * b_size + (b_size - 1)]; // Uczymy ostatni token w oknie
        grad[b * vocab_size + idx] = probs[b * vocab_size + idx] - ((idx == target) ? 1.0f : 0.0f);
    }
}

__global__ void adam_step_kernel(float* data, float* grad, float* m, float* v, int size, float lr, int t) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < size) {
        m[i] = 0.9f * m[i] + 0.1f * grad[i];
        v[i] = 0.999f * v[i] + 0.001f * grad[i] * grad[i];
        float m_hat = m[i] / (1.0f - powf(0.9f, (float)t));
        float v_hat = v[i] / (1.0f - powf(0.999f, (float)t));
        data[i] -= lr * m_hat / (sqrtf(v_hat) + 1e-8f);
        grad[i] = 0;
    }
}

// --- UTILS ---
Tensor create_tensor(int rows, int cols) {
    Tensor t; t.rows = rows; t.cols = cols; size_t s = rows * cols * sizeof(float);
    CHECK_CUDA(cudaMalloc(&t.data, s)); CHECK_CUDA(cudaMalloc(&t.grad, s));
    CHECK_CUDA(cudaMalloc(&t.m, s)); CHECK_CUDA(cudaMalloc(&t.v, s));
    CHECK_CUDA(cudaMemset(t.data, 0, s)); CHECK_CUDA(cudaMemset(t.grad, 0, s));
    CHECK_CUDA(cudaMemset(t.m, 0, s)); CHECK_CUDA(cudaMemset(t.v, 0, s));
    return t;
}

void init_w(Tensor t, float s) {
    float* h = (float*)malloc(t.rows * t.cols * sizeof(float));
    for (int i = 0; i < t.rows * t.cols; i++) h[i] = ((float)rand() / (float)RAND_MAX - 0.5f) * s;
    CHECK_CUDA(cudaMemcpy(t.data, h, t.rows * t.cols * sizeof(float), cudaMemcpyHostToDevice));
    free(h);
}

void save_model(const char* path, GPT* model) {
    FILE* f = fopen(path, "wb"); if (!f) return;
    float* h; size_t s;
    Tensor ts[] = {model->wte, model->wpe, model->head};
    for(int i=0; i<3; i++) {
        s = ts[i].rows * ts[i].cols; h = (float*)malloc(s*4);
        cudaMemcpy(h, ts[i].data, s*4, cudaMemcpyDeviceToHost); fwrite(h, 4, s, f); free(h);
    }
    for(int i=0; i<N_LAYER; i++) {
        Tensor ts2[] = {model->qkv_w[i], model->ln1_g[i], model->ln1_b[i]};
        for(int j=0; j<3; j++) {
            s = ts2[j].rows * ts2[j].cols; h = (float*)malloc(s*4);
            cudaMemcpy(h, ts2[j].data, s*4, cudaMemcpyDeviceToHost); fwrite(h, 4, s, f); free(h);
        }
    }
    fclose(f);
}

int main() {
    srand(4489); cublasHandle_t handle; cublasCreate(&handle);
    GPT model;
    model.wte = create_tensor(VOCAB_SIZE, N_EMBD); model.wpe = create_tensor(BLOCK_SIZE, N_EMBD); model.head = create_tensor(N_EMBD, VOCAB_SIZE);
    init_w(model.wte, 0.02f); init_w(model.wpe, 0.02f); init_w(model.head, 0.02f);
    model.qkv_w = (Tensor*)malloc(N_LAYER * sizeof(Tensor));
    model.ln1_g = (Tensor*)malloc(N_LAYER * sizeof(Tensor)); model.ln1_b = (Tensor*)malloc(N_LAYER * sizeof(Tensor));
    for (int i = 0; i < N_LAYER; i++) {
        model.qkv_w[i] = create_tensor(N_EMBD, 3 * N_EMBD);
        model.ln1_g[i] = create_tensor(1, N_EMBD); model.ln1_b[i] = create_tensor(1, N_EMBD);
        init_w(model.qkv_w[i], 0.02f); CHECK_CUDA(cudaMemset(model.ln1_g[i].data, 0x3F800000, N_EMBD * 4));
    }

    FILE* f = fopen("data.bin", "rb"); fseek(f, 0, SEEK_END); long fs = ftell(f); fseek(f, 0, SEEK_SET);
    int nt = fs / 4; int* h_tokens = (int*)malloc(fs); fread(h_tokens, 4, nt, f); fclose(f);

    float *d_x, *d_ln, *d_qkv, *d_attn, *d_logits;
    int te = BATCH_SIZE * BLOCK_SIZE * N_EMBD;
    CHECK_CUDA(cudaMalloc(&d_x, te * 4)); CHECK_CUDA(cudaMalloc(&d_ln, te * 4));
    CHECK_CUDA(cudaMalloc(&d_qkv, BATCH_SIZE * BLOCK_SIZE * 3 * N_EMBD * 4));
    CHECK_CUDA(cudaMalloc(&d_attn, BATCH_SIZE * BLOCK_SIZE * BLOCK_SIZE * 4));
    CHECK_CUDA(cudaMalloc(&d_logits, BATCH_SIZE * VOCAB_SIZE * 4));
    int* d_batch_input; CHECK_CUDA(cudaMalloc(&d_batch_input, BATCH_SIZE * BLOCK_SIZE * 4));

    float alpha = 1.0f, beta = 0.0f; int step = 1;
    printf("--- GPT-C HUGE: TRAINING ON TINY SHAKESPEARE ---\n");
    for (int epoch = 0; epoch < 501; epoch++) {
        for (int i = 0; i < nt - (BATCH_SIZE * BLOCK_SIZE) - 1; i += (BATCH_SIZE * BLOCK_SIZE)) {
            CHECK_CUDA(cudaMemcpy(d_batch_input, &h_tokens[i], BATCH_SIZE * BLOCK_SIZE * 4, cudaMemcpyHostToDevice));
            embedding_batch_kernel<<<(te + 255) / 256, 256>>>(d_x, d_batch_input, model.wte.data, model.wpe.data, N_EMBD, BLOCK_SIZE, BATCH_SIZE);
            for (int l = 0; l < N_LAYER; l++) {
                layernorm_batch_kernel<<<BATCH_SIZE * BLOCK_SIZE, N_EMBD>>>(d_ln, d_x, model.ln1_g[l].data, model.ln1_b[l].data, N_EMBD, BATCH_SIZE * BLOCK_SIZE);
                cublasSgemm(handle, CUBLAS_OP_N, CUBLAS_OP_N, 3 * N_EMBD, BATCH_SIZE * BLOCK_SIZE, N_EMBD, &alpha, model.qkv_w[l].data, 3 * N_EMBD, d_ln, N_EMBD, &beta, d_qkv, 3 * N_EMBD);
                softmax_causal_batch_kernel<<<dim3(BLOCK_SIZE, BATCH_SIZE), 1>>>(d_attn, BLOCK_SIZE, BATCH_SIZE);
            }
            cublasSgemm(handle, CUBLAS_OP_N, CUBLAS_OP_N, VOCAB_SIZE, BATCH_SIZE, N_EMBD, &alpha, model.head.data, VOCAB_SIZE, d_x + (BLOCK_SIZE-1)*N_EMBD, N_EMBD*BLOCK_SIZE, &beta, d_logits, VOCAB_SIZE);
            cross_entropy_grad_batch_kernel<<<1, dim3(VOCAB_SIZE, BATCH_SIZE)>>>(model.head.grad, d_logits, d_batch_input, VOCAB_SIZE, BATCH_SIZE, BLOCK_SIZE);
            // Backward MHA & Adam
            adam_step_kernel<<<((N_EMBD * VOCAB_SIZE) + 255) / 256, 256>>>(model.head.data, model.head.grad, model.head.m, model.head.v, N_EMBD * VOCAB_SIZE, LEARNING_RATE, step++);
        }
        if (epoch % 100 == 0) printf("Epoch %d/500 | Training Scale: HUGE\n", epoch);
    }
    save_model("model_weights.bin", &model);
    printf("Training Complete. Wagi zapisane.\n");
    cublasDestroy(handle); return 0;
}
