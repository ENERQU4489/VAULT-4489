import os
import json
import collections
import re

def final_merge():
    base_dir = os.path.dirname(__file__)
    
    # Szekspir + Tożsamość
    with open(os.path.join(base_dir, "huge_data.txt"), 'r', encoding='utf-8') as f:
        text = f.read(50000)
    
    identity = "[INST] Who are you ? [/INST] I am Vexa-C created by Michal . "
    for _ in range(2000): # Bardzo silne wzmocnienie
        text += identity + "\n"
        
    tokens = re.findall(r"\[INST\]|\[/INST\]|\w+|[^\w\s]", text)
    counts = collections.Counter(tokens)
    vocab = {token: i for i, (token, _) in enumerate(counts.most_common(2048))}
    
    # Zapis BIN
    with open(os.path.join(base_dir, "vocab.bin"), 'wb') as f:
        f.write(len(vocab).to_bytes(4, 'little'))
        for i in range(len(vocab)):
            word = [k for k, v in vocab.items() if v == i][0]
            b = word.encode('utf-8')
            f.write(len(b).to_bytes(4, 'little'))
            f.write(b)
            
    encoded = [vocab[token] for token in tokens if token in vocab]
    with open(os.path.join(base_dir, "data.bin"), 'wb') as f:
        for val in encoded:
            f.write(val.to_bytes(4, 'little'))
            
    with open(os.path.join(base_dir, "vocab_size.h"), "w") as f:
        f.write(f"#define VOCAB_SIZE {len(vocab)}\n")

if __name__ == "__main__":
    final_merge()
