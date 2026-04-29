# Plan Projektu: Gemini Web UI

## Cel (Objective)
Stworzenie nowoczesnego, estetycznego interfejsu webowego (nakładki) dla lokalnego narzędzia Gemini CLI. Aplikacja ma przypominać klasyczny czat (styl ChatGPT/Claude), z prostym polem do wpisywania promptów na dole i renderowaniem odpowiedzi (z obsługą Markdown) powyżej.

## Tech Stack
- **Frontend:** React + TypeScript (prawdopodobnie inicjowany przez Vite), stylizacja np. Tailwind CSS lub proste CSS Modules.
- **Backend:** Node.js + Express (lub Fastify).
- **Komunikacja:** WebSockets (do strumieniowania odpowiedzi z CLI w czasie rzeczywistym) + ewentualne REST API do konfiguracji.

## Architektura i Wyzwania
1. **Zarządzanie procesem (CLI Bridging):** 
   Zamiast wykonywać jednorazowe strzały do CLI, backend w Node.js musi uruchomić proces `gemini` w tle (używając `child_process.spawn` lub `node-pty`, jeśli CLI wymaga pseudo-terminala do interaktywnego działania) i utrzymywać go przy życiu.
2. **Strumieniowanie I/O:** 
   Wejście użytkownika (prompty) z UI trafiają przez WebSocket na strumień `stdin` procesu CLI. Z kolei to, co proces wypluwa (`stdout`/`stderr`), jest przesyłane z powrotem na frontend przez WebSocket.
3. **Parsowanie ANSI i Markdown:** 
   CLI często zwraca tekst z kodami kolorów ANSI. Backend (lub frontend) musi "oczyścić" tekst z ANSI, a frontend odpowiednio wyrenderować go jako czysty Markdown (np. przy użyciu biblioteki `react-markdown`).

## Etapy Implementacji

### Etap 1: Inicjalizacja Repozytorium i Struktury
- Utworzenie folderu projektu (np. `20 Projects/GeminiWebUI`).
- Inicjalizacja backendu w Node.js (`npm init`, instalacja Express, `ws` lub `socket.io`).
- Inicjalizacja frontendu w React (`npm create vite@latest`).

### Etap 2: Backend (Serwer i CLI Wrapper)
- Stworzenie prostego serwera HTTP i WebSocket.
- Implementacja managera procesu: odpalenie komendy odpowiadającej za start Gemini CLI i podpięcie strumieni I/O do gniazd WebSockets.

### Etap 3: Frontend (Interfejs Użytkownika)
- Budowa widoku czatu (lista wiadomości, input, przycisk wyślij).
- Podłączenie klienta WebSocket.
- Renderowanie przychodzącego strumienia tekstowego do dymków czatu.
- Dodanie renderowania Markdown (np. `react-markdown` + `react-syntax-highlighter` do bloków kodu).

### Etap 4: Integracja i Szlify
- Testowanie komunikacji dwukierunkowej.
- Czyszczenie kodów ucieczki ANSI, aby nie psuły wyświetlania Markdown.
- Poprawki UI (np. automatyczne przewijanie w dół, stany ładowania).

## Weryfikacja i Testy
- Sprawdzenie czy polecenie wpisane w UI wyzwala poprawną reakcję Gemini CLI.
- Weryfikacja czy aplikacja potrafi utrzymać długą sesję bez zamykania procesu w tle.
- Potwierdzenie poprawnego renderowania kodu źródłowego i tekstu.