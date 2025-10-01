# Snake Game

Prosta implementacja klasycznej gry Snake działająca w terminalu.

## Wymagania

- Python 3.10 lub nowszy
- Terminal obsługujący bibliotekę `curses` (na Windows można skorzystać z `Windows Terminal`; jeśli pojawi się błąd o braku modułu `curses`, zainstaluj pakiet `windows-curses` poleceniem `pip install windows-curses`).
- Okno terminala o minimalnym rozmiarze około 40 kolumn x 21 wierszy (program sprawdza to przy starcie i poprosi o powiększenie, jeśli miejsca będzie zbyt mało).

## Uruchamianie

```bash
python snake.py
```

Sterowanie odbywa się za pomocą klawiszy strzałek. Naciśnij `q`, aby zakończyć grę. Po przegranej można nacisnąć `r`, aby rozpocząć rozgrywkę od nowa.

## Rozwiązywanie problemów

Jeżeli podczas uruchamiania pojawi się błąd w stylu `SyntaxError: invalid decimal literal` ze wskazaniem na linię z tekstem `index 00000...`, oznacza to, że do pliku trafiły fragmenty łatki (diff).

1. Najprościej uruchomić naprawę poleceniem:
   ```bash
   python scripts/refresh_snake_file.py
   ```
   Skrypt nadpisze `snake.py` czystą, działającą wersją gry.
2. Alternatywnie pobierz plik ponownie bezpośrednio w trybie "Raw" albo sklonuj repozytorium i upewnij się, że w pliku `snake.py` pierwsza linia zaczyna się od `#!/usr/bin/env python3`.
