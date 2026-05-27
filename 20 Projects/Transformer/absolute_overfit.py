import os
import json
import collections
import re

def absolute_overfit():
    base_dir = os.path.dirname(__file__)
    target_path = os.path.join(base_dir, "enormous_data.txt")
    
    # Tylko jedno zdanie, powtórzone dla batchingu
    clean_text = "[INST] Who are you ? [/INST] I am Vexa-C , created by Michal"
    
    print("Writing absolute overfit dataset...")
    with open(target_path, 'w', encoding='utf-8') as f:
        for _ in range(100):
            f.write(clean_text + "\n")
            
    tokens = re.findall(r"\[INST\]|\[/INST\]|\w+|[^\w\s]", clean_text)
    counts = collections.Counter(tokens)
    vocab = {token: i for i, (token, _) in enumerate(counts.most_common())}
    
    with open(os.path.join(base_dir, "vocab.bin"), 'wb') as f:
        f.write(len(vocab).to_bytes(4, 'little'))
        for token in vocab:
            b = token.encode('utf-8')
            f.write(len(b).to_bytes(4, 'little'))
            f.write(b)
            
    encoded = [vocab[token] for token in tokens if token in vocab]
    with open(os.path.join(base_dir, "data.bin"), 'wb') as f:
        for _ in range(100): # Multi-batch
            for val in encoded:
                f.write(val.to_bytes(4, 'little'))
            
    print(f"ABSOLUTE OVERFIT READY.")
    print(f"Vocab Size: {len(vocab)}")
    print(f"Sequence Length: {len(encoded)}")

if __name__ == "__main__":
    absolute_overfit()
