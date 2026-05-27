import os
import re

def final_overfit():
    base_dir = os.path.dirname(__file__)
    # Zdanie bez kropek, z unikalnym końcem
    clean_text = "WhoAreYou I am Vexa-C created by Michal"
    
    tokens = clean_text.split()
    vocab = {token: i for i, token in enumerate(tokens)}
    
    with open(os.path.join(base_dir, "vocab.bin"), 'wb') as f:
        f.write(len(vocab).to_bytes(4, 'little'))
        for token in vocab:
            b = token.encode('utf-8')
            f.write(len(b).to_bytes(4, 'little'))
            f.write(b)
            
    encoded = [vocab[token] for token in tokens]
    with open(os.path.join(base_dir, "data.bin"), 'wb') as f:
        for _ in range(500):
            for val in encoded:
                f.write(val.to_bytes(4, 'little'))
    
    print(f"FINAL OVERFIT DATA READY. Vocab: {len(vocab)}")

if __name__ == "__main__":
    final_overfit()
