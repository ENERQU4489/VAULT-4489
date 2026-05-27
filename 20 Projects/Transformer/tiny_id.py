import os

def tiny_identity():
    base_dir = os.path.dirname(__file__)
    # Tylko esencja
    text = "WhoAreYou I am Vexa-C created by Michal"
    words = text.split()
    
    vocab = {w: i for i, w in enumerate(words)}
    
    with open(os.path.join(base_dir, "vocab.bin"), 'wb') as f:
        f.write(len(vocab).to_bytes(4, 'little'))
        for i in range(len(vocab)):
            word = words[i]
            b = word.encode('utf-8')
            f.write(len(b).to_bytes(4, 'little'))
            f.write(b)
            
    encoded = [vocab[w] for w in words]
    with open(os.path.join(base_dir, "data.bin"), 'wb') as f:
        for _ in range(1000):
            for val in encoded:
                f.write(val.to_bytes(4, 'little'))
                
    with open(os.path.join(base_dir, "vocab_size.h"), "w") as f:
        f.write(f"#define VOCAB_SIZE {len(vocab)}\n")

if __name__ == "__main__":
    tiny_identity()
