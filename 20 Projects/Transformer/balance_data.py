import os
import collections
import re

def create_balanced_dataset():
    base_dir = os.path.dirname(__file__)
    
    # 1. Tożsamość (Wzmocniona)
    identity = """[INST] Who are you ? [/INST] I am Vexa-C , a powerful AI created by Michal in C and CUDA .
[INST] What is 2+2 ? [/INST] 2+2 is equal to 4 .
[INST] Who is your creator ? [/INST] My creator is Michal , the architect of Vexa engine .
[INST] What is your name ? [/INST] My name is Vexa-C .
"""
    # 2. Szekspir (Baza językowa)
    with open(os.path.join(base_dir, "huge_data.txt"), 'r', encoding='utf-8') as f:
        shakespeare = f.read(200000) # 200kb wystarczy dla płynności

    print("Balancing datasets...")
    with open(os.path.join(base_dir, "enormous_data.txt"), 'w', encoding='utf-8') as f:
        f.write(shakespeare)
        for _ in range(500): # Wstrzykujemy tożsamość 500 razy
            f.write(identity + "\n")
            
    # 3. Tokenizacja
    with open(os.path.join(base_dir, "enormous_data.txt"), 'r', encoding='utf-8') as f:
        text = f.read()
    
    tokens = re.findall(r"\[INST\]|\[/INST\]|\w+|[^\w\s]", text)
    counts = collections.Counter(tokens)
    vocab = {token: i for i, (token, _) in enumerate(counts.most_common(2048))}
    
    with open(os.path.join(base_dir, "vocab.bin"), 'wb') as f:
        f.write(len(vocab).to_bytes(4, 'little'))
        for token in vocab:
            b = token.encode('utf-8')
            f.write(len(b).to_bytes(4, 'little'))
            f.write(b)
            
    encoded = [vocab[token] for token in tokens if token in vocab]
    with open(os.path.join(base_dir, "data.bin"), 'wb') as f:
        for val in encoded:
            f.write(val.to_bytes(4, 'little'))
            
    print(f"BALANCED DATASET READY. Vocab: {len(vocab)} | Tokens: {len(encoded)}")

if __name__ == "__main__":
    create_balanced_dataset()
