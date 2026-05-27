#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <time.h>

// Hiperparametry
#define BLOCK_SIZE 64    
#define N_EMBD 128       
#define N_HEAD 4         
#define N_LAYER 4        
#define VOCAB_SIZE 256   
#define LEARNING_RATE 1e-3

typedef struct {
    float* data;
    float* grad;
    int rows;
    int cols;
} Tensor;

typedef struct {
    Tensor wte; 
    Tensor wpe; 
    Tensor* q_weights; 
    Tensor* mlp_w1; 
    Tensor* mlp_w2; 
    Tensor head;   
} Transformer;

typedef struct {
    unsigned char* tokens;
    long size;
} Dataset;

// --- MATMA OPTIMIZED ---

// C = A * B, gdzie A to wektor [1, K]
void matmul_vec(Tensor* C, Tensor* A, Tensor* B) {
    for (int j = 0; j < B->cols; j++) {
        float sum = 0.0f;
        for (int k = 0; k < A->cols; k++) {
            sum += A->data[k] * B->data[k * B->cols + j];
        }
        C->data[j] = sum;
    }
}

void softmax(float* x, int n) {
    float max_val = x[0];
    for (int i = 1; i < n; i++) if (x[i] > max_val) max_val = x[i];
    float sum = 0.0f;
    for (int i = 0; i < n; i++) {
        x[i] = expf(x[i] - max_val);
        sum += x[i];
    }
    for (int i = 0; i < n; i++) x[i] /= sum;
}

// --- CORE ---

Tensor* create_tensor(int rows, int cols) {
    Tensor* t = (Tensor*)malloc(sizeof(Tensor));
    t->rows = rows; t->cols = cols;
    t->data = (float*)calloc(rows * cols, sizeof(float));
    t->grad = (float*)calloc(rows * cols, sizeof(float));
    return t;
}

void init_weights(Tensor* t) {
    float scale = sqrtf(2.0f / (t->rows + t->cols));
    for (int i = 0; i < t->rows * t->cols; i++) {
        t->data[i] = ((float)rand() / (float)RAND_MAX * 2.0f - 1.0f) * scale;
    }
}

void init_model(Transformer* model) {
    model->wte = *create_tensor(VOCAB_SIZE, N_EMBD);
    model->wpe = *create_tensor(BLOCK_SIZE, N_EMBD);
    model->head = *create_tensor(N_EMBD, VOCAB_SIZE);
    
    init_weights(&model->wte);
    init_weights(&model->wpe);
    init_weights(&model->head);

    model->q_weights = (Tensor*)malloc(N_LAYER * sizeof(Tensor));
    model->mlp_w1 = (Tensor*)malloc(N_LAYER * sizeof(Tensor));
    model->mlp_w2 = (Tensor*)malloc(N_LAYER * sizeof(Tensor));

    for (int i = 0; i < N_LAYER; i++) {
        model->q_weights[i] = *create_tensor(N_EMBD, N_EMBD);
        model->mlp_w1[i] = *create_tensor(N_EMBD, 4 * N_EMBD);
        model->mlp_w2[i] = *create_tensor(4 * N_EMBD, N_EMBD);
        init_weights(&model->q_weights[i]);
        init_weights(&model->mlp_w1[i]);
        init_weights(&model->mlp_w2[i]);
    }
}

void forward(Transformer* model, int input_token, int pos, float* logits) {
    float* x = (float*)calloc(N_EMBD, sizeof(float));
    for (int i = 0; i < N_EMBD; i++) {
        x[i] = model->wte.data[input_token * N_EMBD + i] + model->wpe.data[pos * N_EMBD + i];
    }

    float* next_x = (float*)calloc(N_EMBD, sizeof(float));
    for (int l = 0; l < N_LAYER; l++) {
        Tensor x_t = {x, NULL, 1, N_EMBD};
        Tensor q_t = {next_x, NULL, 1, N_EMBD};
        matmul_vec(&q_t, &x_t, &model->q_weights[l]);
        for (int i = 0; i < N_EMBD; i++) x[i] += next_x[i];

        float* h = (float*)calloc(4 * N_EMBD, sizeof(float));
        Tensor h_t = {h, NULL, 1, 4 * N_EMBD};
        matmul_vec(&h_t, &x_t, &model->mlp_w1[l]);
        for (int i = 0; i < 4 * N_EMBD; i++) if (h[i] < 0) h[i] = 0;
        
        Tensor x_out = {x, NULL, 1, N_EMBD};
        matmul_vec(&x_out, &h_t, &model->mlp_w2[l]);
        free(h);
    }

    Tensor x_f = {x, NULL, 1, N_EMBD};
    Tensor l_t = {logits, NULL, 1, VOCAB_SIZE};
    matmul_vec(&l_t, &x_f, &model->head);

    free(x); free(next_x);
}

void train_step(Transformer* model, int input_token, int target_token) {
    float* logits = (float*)calloc(VOCAB_SIZE, sizeof(float));
    forward(model, input_token, 0, logits);
    softmax(logits, VOCAB_SIZE);

    for (int i = 0; i < VOCAB_SIZE; i++) {
        float grad = logits[i] - ((i == target_token) ? 1.0f : 0.0f);
        for (int j = 0; j < N_EMBD; j++) {
            model->head.data[j * VOCAB_SIZE + i] -= LEARNING_RATE * grad;
        }
    }
    free(logits);
}

Dataset load_dataset(const char* path) {
    FILE* f = fopen(path, "rb");
    if (!f) exit(1);
    fseek(f, 0, SEEK_END); long size = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char* buf = malloc(size); fread(buf, 1, size, f); fclose(f);
    return (Dataset){buf, size};
}

int main() {
    srand(time(NULL));
    Transformer model; init_model(&model);
    Dataset ds = load_dataset("input.txt");
    
    printf("Training Turbo-Transformer on %ld characters...\n", ds.size);
    for (int e = 0; e < 100; e++) {
        for (int i = 0; i < ds.size - 1; i++) {
            train_step(&model, ds.tokens[i], ds.tokens[i+1]);
            if (i % 500 == 0) {
                printf("Epoch %d | Step %d/%ld\r", e, i, ds.size);
                fflush(stdout);
            }
        }
    }

    printf("\nGeneration: ");
    int curr = ds.tokens[0]; printf("%c", curr);
    for (int i = 0; i < 50; i++) {
        float* l = (float*)calloc(VOCAB_SIZE, sizeof(float));
        forward(&model, curr, 0, l);
        softmax(l, VOCAB_SIZE);
        int next = 0; for (int j = 1; j < VOCAB_SIZE; j++) if (l[j] > l[next]) next = j;
        printf("%c", next); curr = next; free(l);
    }
    printf("\n");
    return 0;
}
