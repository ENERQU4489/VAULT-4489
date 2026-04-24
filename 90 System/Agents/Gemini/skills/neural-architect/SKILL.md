---
name: neural-architect
description: Automatyczne sugerowanie i budowanie powiązań (WikiLinks) między notatkami. Używaj, gdy chcesz uporządkować wiedzę, połączyć notatki z 40 Brain z logami dziennymi lub projektami.
---

# Neural Architect

Ten skill pomaga przekształcić statyczne notatki w sieć powiązań.

## Główne zadanie
Skanowanie plików pod kątem słów kluczowych, które odpowiadają tytułom notatek w folderze `40 Brain`.

## Procedura (dla Agenta)
1.  **Analiza kontekstu**: Gdy użytkownik pisze nową notatkę lub kończy dzień, sprawdź, czy w tekście występują pojęcia z `40 Brain`.
2.  **Uruchomienie skryptu**: 
    `python "C:\Users\micha\.gemini\skills\neural-architect\scripts\linker.py" "40 Brain" "<ścieżka_do_pliku>"`
3.  **Propozycja**: Przedstaw użytkownikowi listę znalezionych powiązań.
4.  **Implementacja**: Po akceptacji, zaktualizuj plik, zamieniając czysty tekst na `[[Linki]]`.

## Kiedy używać?
- Przy podsumowaniach dnia w `00 Daily`.
- Przy tworzeniu nowych projektów w `20 Projects`.
- Gdy użytkownik prosi o "uporządkowanie myśli" lub "połączenie kropek".

## Skrypt pomocniczy
Skrypt `linker.py` automatyzuje wyszukiwanie pasujących tytułów notatek, dbając o to, by nie dublować istniejących już linków.

[[SYSTEM]]
