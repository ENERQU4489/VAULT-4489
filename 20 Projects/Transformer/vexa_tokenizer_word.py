import os
import json
import re
import collections

class VexaWordTokenizer:
    def __init__(self, special_tokens=None):
        # ID 0 zarezerwowane dla [UNK]
        self.vocab = {"[UNK]": 0}
        self.inv_vocab = {0: "[UNK]"}
        if special_tokens:
            for i, token in enumerate(special_tokens, 1):
                self.vocab[token] = i
                self.inv_vocab[i] = token

    def build_vocab(self, text, max_size=8192):
        print("Building Word-Level Vocabulary...")
        # Regex: słowa, liczby, znaki specjalne, oraz nasze tagi [INST]
        pattern = r"\[INST\]|\[/INST\]|\w+|[^\w\s]"
        tokens = re.findall(pattern, text)
        
        counts = collections.Counter(tokens)
        # Sortujemy od najczęstszych, pomijając te już w vocab
        for word, count in counts.most_common():
            if word not in self.vocab:
                new_id = len(self.vocab)
                self.vocab[word] = new_id
                self.inv_vocab[new_id] = word
            if len(self.vocab) >= max_size:
                break
        
        print(f"Vocab built. Size: {len(self.vocab)}")

    def encode(self, text):
        pattern = r"\[INST\]|\[/INST\]|\w+|[^\w\s]"
        tokens = re.findall(pattern, text)
        return [self.vocab.get(t, 0) for t in tokens]

    def save_binary(self, vocab_path, data_path, encoded_data):
        # 1. Zapis słownika dla C: [int count][len1][str1][len2][str2]...
        with open(vocab_path, 'wb') as f:
            f.write(len(self.vocab).to_bytes(4, 'little'))
            # Sortujemy po ID, żeby w C dostęp był przez indeks tablicy
            for i in range(len(self.vocab)):
                word = self.inv_vocab[i]
                b = word.encode('utf-8')
                f.write(len(b).to_bytes(4, 'little'))
                f.write(b)
        
        # 2. Zapis danych: [uint32 token1][uint32 token2]...
        with open(data_path, 'wb') as f:
            for val in encoded_data:
                f.write(val.to_bytes(4, 'little'))
        
        print(f"Binary export complete: {vocab_path}, {data_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    input_file = os.path.join(base_dir, "enormous_data.txt")
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
    else:
        with open(input_file, 'r', encoding='utf-8') as f:
            full_text = f.read()
        
        # Tokenizujemy wszystko
        tokenizer = VexaWordTokenizer(special_tokens=["[INST]", "[/INST]", "EOS"])
        tokenizer.build_vocab(full_text, max_size=8192)
        
        encoded = tokenizer.encode(full_text)
        tokenizer.save_binary(os.path.join(base_dir, "vocab.bin"), 
                              os.path.join(base_dir, "data.bin"), 
                              encoded)
        
        # Zapisujemy rozmiar słownika do pliku tekstowego dla C
        with open(os.path.join(base_dir, "vocab_size.h"), "w") as f:
            f.write(f"#define VOCAB_SIZE {len(tokenizer.vocab)}\n")
            f.write(f"#define NUM_TOKENS {len(encoded)}\n")
