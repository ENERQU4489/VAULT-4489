import requests
import json

def generate_instruct_set(output_path, model_name):
    url = "http://localhost:11434/api/generate"
    
    prompt = """Generate a simple instruction dataset for a very small AI model. 
    Format: Each example should be [INST] Question [/INST] Answer.
    Topics: Basic math, definitions, and simple facts.
    Keep it repetitive and simple.
    Example: [INST] What is 2+2? [/INST] 2+2 is 4.
    Generate 100 such pairs in plain text."""

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }

    print(f"Generating Instruct Dataset via {model_name}...")
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(data["response"])
        print(f"Success! Instruct data saved to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_instruct_set("instruct.txt", "huihui_ai/gemma-4-abliterated:e4b")
