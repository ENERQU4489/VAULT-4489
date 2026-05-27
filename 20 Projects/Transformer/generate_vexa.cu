#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <cuda_runtime.h>
#include <cuda_fp16.h>
#include <cublas_v2.h>

#define BLOCK_SIZE 64
#define N_EMBD 512
#define N_LAYER 6
#define N_HEAD 8
#define VOCAB_SIZE 4096

#define CHECK_CUDA(call) { cudaError_t err = call; if (err != cudaSuccess) { printf("CUDA Error: %s at %d\n", cudaGetErrorString(err), __LINE__); exit(1); } }

typedef struct { half *data; int rows, cols; } VexaTensor;
typedef struct { VexaTensor wte; VexaTensor *ln_g, *qkv_w, *mlp_w1, *mlp_w2; VexaTensor head; } VexaGPT;

char** vocab;
int vocab_count_global;

void load_vocab(const char* path) {
    FILE* f = fopen(path, "rb");
    fread(&vocab_count_global, 4, 1, f);
    vocab = (char**)malloc(vocab_count_global * sizeof(char*));
    for (int i = 0; i < vocab_count_global; i++) {
        int len; fread(&len, 4, 1, f);
        vocab[i] = (char*)malloc(len + 1);
        fread(vocab[i], 1, len, f);
        vocab[i][len] = '\0';
    }
    fclose(f);
}

void load_tensor(FILE* f, VexaTensor t) {
    int n; fread(&n, 4, 1, f);
    half* h = (half*)malloc(n * 2);
    fread(h, 2, n, f);
    cudaMemcpy(t.data, h, n * 2, cudaMemcpyHostToDevice);
    free(h);
}

int main() {
    cublasHandle_t h; cublasCreate(&h);
    load_vocab("vexa_vocab.bin");
    VexaGPT model;
    
    cudaMalloc(&model.wte.data, VOCAB_SIZE * N_EMBD * 2); model.wte.rows = VOCAB_SIZE; model.wte.cols = N_EMBD;
    cudaMalloc(&model.head.data, N_EMBD * VOCAB_SIZE * 2); model.head.rows = N_EMBD; model.head.cols = VOCAB_SIZE;
    model.qkv_w = (VexaTensor*)malloc(N_LAYER * sizeof(VexaTensor));
    model.ln_g = (VexaTensor*)malloc(N_LAYER * sizeof(VexaTensor));
    
    FILE* fw = fopen("vexa_model_final.bin", "rb");
    fseek(fw, 4, SEEK_SET);
    load_tensor(fw, model.wte); load_tensor(fw, model.head);
    for(int i=0; i<N_LAYER; i++) {
        cudaMalloc(&model.qkv_w[i].data, N_EMBD * 3 * N_EMBD * 2); model.qkv_w[i].rows = N_EMBD; model.qkv_w[i].cols = 3 * N_EMBD;
        cudaMalloc(&model.ln_g[i].data, N_EMBD * 2); model.ln_g[i].rows = 1; model.ln_g[i].cols = N_EMBD;
        load_tensor(fw, model.qkv_w[i]);
    }
    fclose(fw);

    int cur_tokens[BLOCK_SIZE] = {0};
    // Prompt: "[INST] Who are you ? [/INST]"
    int p_ids[] = {0, 4, 19, 21, 2, 1}; // Przykładowe ID, model powinien sam zaskoczyć
    for(int i=0; i<6; i++) cur_tokens[i] = p_ids[i];

    float *d_logits; half *d_x, *d_ln, *d_qkv;
    cudaMalloc(&d_x, BLOCK_SIZE * N_EMBD * 2); cudaMalloc(&d_ln, BLOCK_SIZE * N_EMBD * 2);
    cudaMalloc(&d_qkv, BLOCK_SIZE * 3 * N_EMBD * 2); cudaMalloc(&d_logits, VOCAB_SIZE * 4);
    int* d_input; cudaMalloc(&d_input, BLOCK_SIZE * 4);

    float alpha = 1.0f, beta = 0.0f;
    printf("\n--- VEXA-C IDENTITY RESPONSE ---\n");
    for (int i = 0; i < 30; i++) {
        cudaMemcpy(d_input, cur_tokens, BLOCK_SIZE * 4, cudaMemcpyHostToDevice);
        // (Kernel calls...)
        // [Zwięzła pętla inferencji]
        
        float h_l[VOCAB_SIZE]; cudaMemcpy(h_l, d_logits, VOCAB_SIZE * 4, cudaMemcpyDeviceToHost);
        int next = 0; for(int j=1; j<VOCAB_SIZE; j++) if(h_l[j] > h_l[next]) next = j;
        
        printf("%s ", vocab[next]);
        for(int j=0; j<BLOCK_SIZE-1; j++) cur_tokens[j] = cur_tokens[j+1]; cur_tokens[BLOCK_SIZE-1] = next;
    }
    printf("\n");
    return 0;
}
