import os
import json
import collections

class VexaTokenizer:
    def __init__(self, vocab_size=32000):
        self.vocab_size = vocab_size
        self.vocab = {}
        self.merges = {}
        self.inv_vocab = {}

    def train(self, text):
        print(f"Training BPE Tokenizer (Target: {self.vocab_size} tokens)...")
        # 1. Inicjalizacja bazowa (bajty)
        tokens = [list(word.encode('utf-8')) for word in text.split()]
        self.vocab = {i: bytes([i]) for i in range(256)}
        
        current_vocab_size = 256
        num_merges = self.vocab_size - 256
        
        for i in range(num_merges):
            pairs = collections.defaultdict(int)
            for word in tokens:
                for j in range(len(word)-1):
                    pairs[(word[j], word[j+1])] += 1
            
            if not pairs: break
            best_pair = max(pairs, key=pairs.get)
            new_token = current_vocab_size
            self.merges[best_pair] = new_token
            self.vocab[new_token] = self.vocab[best_pair[0]] + self.vocab[best_pair[1]]
            
            # Update tokens
            new_tokens = []
            for word in tokens:
                new_word = []
                j = 0
                while j < len(word):
                    if j < len(word)-1 and (word[j], word[j+1]) == best_pair:
                        new_word.append(new_token)
                        j += 2
                    else:
                        new_word.append(word[j])
                        j += 1
                new_tokens.append(new_word)
            tokens = new_tokens
            current_vocab_size += 1
            if i % 100 == 0:
                print(f"BPE Merges: {i}/{num_merges}\r", end="")

        print(f"\nFinal Vocab Size: {current_vocab_size}")

    def save(self, vocab_path, merges_path):
        with open(vocab_path, 'wb') as f:
            f.write(len(self.vocab).to_bytes(4, 'little'))
            for i in range(len(self.vocab)):
                b = self.vocab[i]
                f.write(len(b).to_bytes(4, 'little'))
                f.write(b)
        print(f"Tokenizer saved to {vocab_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "enormous_data.txt")
    if os.path.exists(data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            text = f.read(1000000) # Trening na pierwszym 1MB dla szybkości dema
        tokenizer = VexaTokenizer(vocab_size=8192) # Skalujemy do 8k na start
        tokenizer.train(text)
        tokenizer.save(os.path.join(base_dir, "vexa_vocab.bin"), "")
