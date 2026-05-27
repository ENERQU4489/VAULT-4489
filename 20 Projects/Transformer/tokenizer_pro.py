import json
import collections
import re
import os

def create_pro_tokenizer(input_path, vocab_json_path, vocab_bin_path, data_out_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Tokenizer: słowa, znaki specjalne, liczby
    tokens = re.findall(r"\[INST\]|\[/INST\]|\w+|[^\w\s]", text)
    
    # Budowa słownika (zwiększamy do 4096 dla bogatszego języka)
    counts = collections.Counter(tokens)
    vocab = {token: i for i, (token, _) in enumerate(counts.most_common(4096))}
    
    # Zapis JSON (dla nas)
    with open(vocab_json_path, 'w', encoding='utf-8') as f:
        json.dump(vocab, f)
    
    # Zapis BIN (dla C - format: [int count][len1][string1][len2][string2]...)
    with open(vocab_bin_path, 'wb') as f:
        f.write(len(vocab).to_bytes(4, 'little'))
        for token in vocab:
            encoded_token = token.encode('utf-8')
            f.write(len(encoded_token).to_bytes(4, 'little'))
            f.write(encoded_token)
    
    # Kodowanie danych
    encoded = [vocab[t] for token in tokens if (t := token) in vocab]
    with open(data_out_path, 'wb') as f:
        for val in encoded:
            f.write(val.to_bytes(4, 'little'))
            
    print(f"Vocab size: {len(vocab)}")
    print(f"Encoded tokens: {len(encoded)}")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    # Łączymy wszystko co mamy
    files = ["huge_data.txt", "input.txt", "instruct.txt", "instruct_big.txt", "instruct_ready.txt"]
    with open(os.path.join(base_dir, "enormous_data.txt"), "w", encoding="utf-8") as outfile:
        for fname in files:
            p = os.path.join(base_dir, fname)
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as infile:
                    outfile.write(infile.read() + "\n")
    
    create_pro_tokenizer(os.path.join(base_dir, "enormous_data.txt"), 
                         os.path.join(base_dir, "vocab.json"), 
                         os.path.join(base_dir, "vocab.bin"),
                         os.path.join(base_dir, "data.bin"))
