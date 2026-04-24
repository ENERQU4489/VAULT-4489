import os
import re
import sys

def get_brain_notes(brain_path):
    notes = []
    for root, dirs, files in os.walk(brain_path):
        for file in files:
            if file.endswith(".md"):
                notes.append(file[:-3])  # Usuwamy .md
    return sorted(notes, key=len, reverse=True)  # Najdłuższe nazwy najpierw dla lepszego dopasowania

def suggest_links(content, notes):
    suggestions = []
    for note in notes:
        # Szukamy całych słów, które nie są już w linkach [[]]
        pattern = rf'(?<!\[\[)\b{re.escape(note)}\b(?!\]\])'
        if re.search(pattern, content, re.IGNORECASE):
            suggestions.append(note)
    return suggestions

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python linker.py <brain_path> <target_file>")
        sys.exit(1)

    brain_path = sys.argv[1]
    target_file = sys.argv[2]

    if not os.path.exists(target_file):
        print(f"File {target_file} not found.")
        sys.exit(1)

    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    notes = get_brain_notes(brain_path)
    links = suggest_links(content, notes)

    if links:
        print("Sugerowane linki do dodania:")
        for link in links:
            print(f"- [[{link}]]")
    else:
        print("Nie znaleziono nowych powiązań.")
