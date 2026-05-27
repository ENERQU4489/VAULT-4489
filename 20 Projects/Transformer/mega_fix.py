import os

def mega_fix_data():
    base_dir = os.path.dirname(__file__)
    # Proste zdanie do overfittingu
    text = "VexaIsCool MichalCreatedMe CudaIsFast"
    words = text.split()
    
    # Słownik z rezerwacją ID 0
    vocab = {"[UNK]": 0}
    for i, w in enumerate(words):
        vocab[w] = i + 1
        
    with open(os.path.join(base_dir, "vocab.bin"), 'wb') as f:
        f.write(len(vocab).to_bytes(4, 'little'))
        for token in sorted(vocab, key=vocab.get):
            b = token.encode('utf-8')
            f.write(len(b).to_bytes(4, 'little'))
            f.write(b)
            
    encoded = [vocab[w] for w in words]
    with open(os.path.join(base_dir, "data.bin"), 'wb') as f:
        for _ in range(1000):
            for val in encoded:
                f.write(val.to_bytes(4, 'little'))
    
    print(f"MEGA FIX DATA READY. Vocab size: {len(vocab)}")

if __name__ == "__main__":
    mega_fix_data()
