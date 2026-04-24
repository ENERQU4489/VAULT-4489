# Projekt: Zgłoszenie bomberV2 do CERT Polska

## 📝 Opis
Analiza i przygotowanie do wysyłki próbek potencjalnie złośliwego oprogramowania znalezionego w katalogu `bomberV2`.

## 📁 Zawartość paczki
- `loader.ps1`: Skrypt PowerShell (prawdopodobnie dropper/loader)
- `lantern.js` / `trace.js`: Skrypty JavaScript
- `frankaa.hta`: Aplikacja HTML (częsty wektor ataku)
- `fixed_payload.exe` / `shellcode2.bin.exe`: Pliki wykonywalne (payload) - podejrzenie techniki [[Process Hollowing]]
- `decrypt.py`: Skrypt do deszyfrowania danych ([[Python]])

## 📋 Lista zadań
- [x] Inwentaryzacja plików
- [ ] Analiza wstępna skryptów (obfuskacja, C2)
- [ ] Przygotowanie archiwum ZIP z hasłem `infected`
- [ ] Napisanie treści zgłoszenia dla CERT.pl

## 🛡️ Bezpieczeństwo
**UWAGA:** Katalog zawiera aktywne pliki wykonywalne. Nie uruchamiać poza izolowanym środowiskiem (sandbox).
