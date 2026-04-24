# Mapa projektu: vexa-polish-llm

## 🎯 Cel
Rozwój polskiego modelu językowego (LLM) zintegrowanego z grafami wiedzy.

## 🏗️ Architektura (src/)
- **`core/`**: Sercem projektu są `engine.py` (silnik) oraz `graph.py` (zarządzanie grafem).
- **`integration/`**: `llm_interface.py` odpowiada za komunikację z modelami zewnętrznymi.
- **`utils/`**: Narzędzia do preprocessingu: `tokenizer.py`, `cleaner.py` oraz `wiki_downloader.py` (pobieranie danych treningowych).

## 🛠️ Technologie
- [[Python]] (Główny język)
- [[LLM]] (Integracje)
- Flask/Web (Plik `web_app.py` sugeruje interfejs WWW)
- Docker (Dostępny `Dockerfile`)

## 🚦 Szybki start
- Główne wejście: `main.py`
- Interfejs webowy: `web_app.py`
- Testy: `tests/test_basic.py`

---
## 🧬 Powiązania z Vaultem
- Projekt bazuje na wiedzy o [[LLM]] oraz [[Python]].
- Wykorzystuje techniki przetwarzania grafów (por. [[Neural-Architect]]).
