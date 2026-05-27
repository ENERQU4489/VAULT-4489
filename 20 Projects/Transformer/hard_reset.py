import os
import json
import collections
import re

def hard_reset_and_train():
    base_dir = os.path.dirname(__file__)
    target_path = os.path.join(base_dir, "enormous_data.txt")
    identity_path = os.path.join(base_dir, "identity_data.txt")
    
    # 1. Czysty zapis identity (1000 razy)
    with open(identity_path, 'r', encoding='utf-8') as f:
        id_text = f.read()
    
    print("Writing clean identity dataset...")
    with open(target_path, 'w', encoding='utf-8') as f:
        for _ in range(1000):
            f.write(id_text + "\n")
            
    # 2. Tokenizacja
    with open(target_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    tokens = re.findall(r"\[INST\]|\[/INST\]|\w+|[^\w\s]", text)
    counts = collections.Counter(tokens)
    vocab = {token: i for i, (token, _) in enumerate(counts.most_common(4096))}
    
    # Zapis BIN dla C
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
            
    print(f"HARD RESET SUCCESSFUL.")
    print(f"New Vocab Size: {len(vocab)}")
    print(f"New Encoded Tokens: {len(encoded)}")

if __name__ == "__main__":
    hard_reset_and_train()
