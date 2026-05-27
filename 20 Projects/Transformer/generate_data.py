import requests
import json
import sys
import time

def generate_dataset(output_path, model_name, target_words=2000):
    url = "http://localhost:11434/api/generate"
    
    prompt = f"""Write a very long, repetitive technical lecture about Neural Networks, Transformers, and Linear Algebra. 
    Use words like 'matrix', 'tensor', 'gradient', 'weight', 'layer', 'attention' very often. 
    Explain concepts in a way that repeats patterns. 
    Target length: at least {target_words} words. 
    Format: Plain text only, no markdown headers."""

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": True  # Strumieniujemy, żeby widzieć postęp
    }

    print(f"Connecting to Ollama (Model: {model_name})...")
    try:
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()
    except Exception as e:
        print(f"Error: Could not connect to Ollama. {e}")
        return

    print(f"Generating data to {output_path}...")
    word_count = 0
    char_count = 0
    
    with open(output_path, "w", encoding="utf-8") as f:
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode("utf-8"))
                text = chunk.get("response", "")
                f.write(text)
                f.flush()
                
                char_count += len(text)
                if " " in text:
                    word_count += text.count(" ")
                
                # Prosty pasek postępu w konsoli
                sys.stdout.write(f"\rProgress: ~{word_count} words | {char_count} chars generated...")
                sys.stdout.flush()
                
                if chunk.get("done"):
                    break

    print(f"\nSuccess! Dataset saved to {output_path}")

if __name__ == "__main__":
    MODEL = "huihui_ai/gemma-4-abliterated:e4b"
    OUTPUT = "input.txt"
    generate_dataset(OUTPUT, MODEL)
