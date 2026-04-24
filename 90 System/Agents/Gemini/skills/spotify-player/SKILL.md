---
name: spotify-player
description: Sterowanie odtwarzaniem muzyki i wyszukiwanie na Spotify przy użyciu spotify_player. Używaj, gdy użytkownik chce zarządzać muzyką, przełączać utwory lub sprawdzać co jest odtwarzane.
---

# spotify_player (Windows Setup)

Lokalizacja binarki: `~\.gemini\bin\spotify_player.exe`

## Kluczowe komendy (PowerShell)
Zawsze używaj operatora wywołania `&` z pełną ścieżką lub upewnij się, że binarka jest w PATH.

- **Status / Co leci:** `& "$HOME\.gemini\bin\spotify_player.exe" get key playback` (zwraca JSON)
- **Następny utwór:** `& "$HOME\.gemini\bin\spotify_player.exe" playback next`
- **Poprzedni utwór:** `& "$HOME\.gemini\bin\spotify_player.exe" playback previous`
- **Pauza/Play:** `& "$HOME\.gemini\bin\spotify_player.exe" playback pause` | `play`
- **Uruchomienie playlisty:** `& "$HOME\.gemini\bin\spotify_player.exe" playback start context playlist --id "spotify:playlist:<ID>"`
- **Wyszukiwanie:** `& "$HOME\.gemini\bin\spotify_player.exe" search "<fraza>"`

## Uwagi dla Agenta
- Przy sprawdzaniu statusu parsuj JSON: `.item.name` to tytuł, `.item.artists[0].name` to autor.
- Jeśli komenda zawiedzie, poproś użytkownika o uruchomienie aplikacji Spotify lub terminalowego playera.

[[SYSTEM]]
