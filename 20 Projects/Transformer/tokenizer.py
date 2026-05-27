import json
import collections
import re

def create_simple_tokenizer(input_path, vocab_path, data_out_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Prosty tokenizer: słowa + znaki specjalne
    tokens = re.findall(r"\[INST\]|\[/INST\]|\w+|[^\w\s]", text)
    
    # Budowa słownika
    counts = collections.Counter(tokens)
    vocab = {token: i for i, (token, _) in enumerate(counts.most_common(2048))} # Top 2048 tokenów
    
    # Zapis słownika
    with open(vocab_path, 'w', encoding='utf-8') as f:
        json.dump(vocab, f)
    
    # Kodowanie danych
    encoded = [vocab[t] for token in tokens if (t := token) in vocab]
    
    with open(data_out_path, 'wb') as f:
        for val in encoded:
            f.write(val.to_bytes(4, 'little')) # 32-bit int
            
    print(f"Vocab size: {len(vocab)}")
    print(f"Encoded tokens: {len(encoded)}")

if __name__ == "__main__":
    import os
    # Używamy ścieżki względnej do pliku skryptu
    base_dir = os.path.dirname(__file__)
    create_simple_tokenizer(os.path.join(base_dir, "huge_data.txt"), 
                            os.path.join(base_dir, "vocab.json"), 
                            os.path.join(base_dir, "data.bin"))
