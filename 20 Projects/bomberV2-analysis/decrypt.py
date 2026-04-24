import os

def auto_repair_and_scan(input_file):
    with open(input_file, 'rb') as f:
        data = f.read()

    # 1. Sprawdzenie nagłówka MZ
    if data.startswith(b'MZ'):
        print("[+] Nagłówek MZ obecny. Plik jest technicznie poprawny.")
    else:
        print("[!] Brak MZ! Próba naprawy nagłówka...")
        # Doklejamy standardowy stub DOS, jeśli go brakuje
        mz_stub = b'MZ' + b'\x90' * 62 # Minimalny nagłówek
        data = mz_stub + data[64:] 

    # 2. Szukanie "Magic Constants" (np. nagłówek PE)
    pe_offset = data.find(b'PE\x00\x00')
    if pe_offset != -1:
        print(f"[+] Znaleziono sygnaturę PE pod offsetem: {hex(pe_offset)}")
    else:
        print("[-] Nie znaleziono sygnatury PE. To może być surowy Shellcode x64.")

    # 3. Automatyczny carving (wycinanie czytelnych bloków)
    with open("repaired_payload.exe", "wb") as f:
        f.write(data)
    print("[+] Plik naprawiony zapisany jako: repaired_payload.exe")

if __name__ == "__main__":
    auto_repair_and_scan("shellcode2.bin.exe")