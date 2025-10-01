"""Przywraca czystą wersję pliku `snake.py`.

Uruchom ten skrypt, gdy w pliku `snake.py` pojawi się błąd `SyntaxError: invalid decimal literal`
wynikający z przypadkowego wklejenia zawartości łatki (linii zaczynających się od `index`, `+++`, `---`, itp.).
Skrypt nadpisze plik aktualną, poprawną wersją gry.
"""

from __future__ import annotations

from pathlib import Path

SNAKE_SOURCE = '''#!/usr/bin/env python3
"""Terminalowa gra Snake."""

import random
import sys
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Iterable, List, Optional, Tuple

try:  # pragma: no cover - zależy od platformy
    import curses  # type: ignore
except ImportError as exc:  # pragma: no cover - zależy od platformy
    curses = None  # type: ignore[assignment]
    _CURSES_IMPORT_ERROR = exc
else:
    _CURSES_IMPORT_ERROR = None

Point = Tuple[int, int]


@dataclass(frozen=True)
class SnakeConfig:
    height: int = 20
    width: int = 40
    tick_rate: float = 0.1


class SnakeGame:
    """Implementacja logiki gry Snake."""

    def __init__(self, stdscr: "curses._CursesWindow", config: Optional[SnakeConfig] = None) -> None:
        self.stdscr = stdscr
        self.config = config or SnakeConfig()
        self.snake: Deque[Point] = deque()
        self.direction: Point = (0, 1)
        self.food: Optional[Point] = None
        self.score = 0
        self.is_game_over = False
        self._init_game()

    def _init_game(self) -> None:
        curses.curs_set(0)
        self.stdscr.nodelay(False)
        self.stdscr.clear()
        self._ensure_screen_fits()
        self.stdscr.nodelay(True)
        start_y = self.config.height // 2
        start_x = self.config.width // 2
        self.snake.clear()
        self.snake.appendleft((start_y, start_x))
        self.snake.appendleft((start_y, start_x - 1))
        self.snake.appendleft((start_y, start_x - 2))
        self.direction = (0, 1)
        self.score = 0
        self.is_game_over = False
        self._place_food()

    def _ensure_screen_fits(self) -> None:
        lines, cols = self.stdscr.getmaxyx()
        required_lines = self.config.height + 1
        required_cols = self.config.width
        if lines >= required_lines and cols >= required_cols:
            return

        warning_lines = self._too_small_message(lines, cols, required_lines, required_cols)
        for row, text in enumerate(warning_lines):
            trimmed = text[: max(0, cols - 1)]
            try:
                self.stdscr.addstr(row, 0, trimmed)
            except curses.error:
                pass
        self.stdscr.refresh()
        self.stdscr.getch()
        raise SystemExit(1)

    @staticmethod
    def _too_small_message(lines: int, cols: int, req_lines: int, req_cols: int) -> List[str]:
        return [
            "Okno terminala jest zbyt małe dla gry Snake.",
            f"Minimalny rozmiar: {req_cols} kolumn x {req_lines} wierszy.",
            f"Aktualny rozmiar: {cols} kolumn x {lines} wierszy.",
            "",
            "Powiększ terminal i naciśnij dowolny klawisz, aby wyjść.",
        ]

    def _place_food(self) -> None:
        height, width = self.config.height, self.config.width
        available = [
            (y, x)
            for y in range(1, height - 1)
            for x in range(1, width - 1)
            if (y, x) not in self.snake
        ]
        if not available:
            self.food = None
            self.is_game_over = True
            return
        self.food = random.choice(available)

    def _change_direction(self, key: int) -> None:
        directions = {
            curses.KEY_UP: (-1, 0),
            curses.KEY_DOWN: (1, 0),
            curses.KEY_LEFT: (0, -1),
            curses.KEY_RIGHT: (0, 1),
        }
        if key not in directions:
            return
        new_dir = directions[key]
        if new_dir[0] == -self.direction[0] and new_dir[1] == -self.direction[1]:
            return
        self.direction = new_dir

    def _update(self) -> None:
        head_y, head_x = self.snake[0]
        delta_y, delta_x = self.direction
        new_head = (head_y + delta_y, head_x + delta_x)
        if self._hits_wall(new_head) or self._hits_body(new_head):
            self.is_game_over = True
            return
        self.snake.appendleft(new_head)
        if new_head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

    def _hits_wall(self, point: Point) -> bool:
        y, x = point
        height, width = self.config.height, self.config.width
        return y <= 0 or x <= 0 or y >= height - 1 or x >= width - 1

    def _hits_body(self, point: Point) -> bool:
        will_grow = self.food is not None and point == self.food
        body: Iterable[Point] = self.snake if will_grow else list(self.snake)[:-1]
        return point in body

    def _draw_border(self) -> None:
        height, width = self.config.height, self.config.width
        for x in range(width):
            self.stdscr.addch(0, x, "#")
            self.stdscr.addch(height - 1, x, "#")
        for y in range(height):
            self.stdscr.addch(y, 0, "#")
            self.stdscr.addch(y, width - 1, "#")

    def _draw_snake(self) -> None:
        for idx, (y, x) in enumerate(self.snake):
            char = "@" if idx == 0 else "o"
            self.stdscr.addch(y, x, char)

    def _draw_food(self) -> None:
        if self.food:
            self.stdscr.addch(self.food[0], self.food[1], "*")

    def _draw_ui(self) -> None:
        lines, cols = self.stdscr.getmaxyx()
        ui_y = min(self.config.height, lines - 1)
        message = f"Wynik: {self.score}  (q = wyjście)"
        trimmed = message[: max(0, cols - 1)]
        try:
            self.stdscr.move(ui_y, 0)
            self.stdscr.clrtoeol()
            self.stdscr.addstr(ui_y, 0, trimmed)
        except curses.error:
            pass

    def _render(self) -> None:
        self.stdscr.clear()
        self._draw_border()
        self._draw_snake()
        self._draw_food()
        self._draw_ui()
        self.stdscr.refresh()

    def _game_over_screen(self) -> None:
        lines, cols = self.stdscr.getmaxyx()
        message = f"Koniec gry! Wynik: {self.score}. (r = restart, q = wyjście)"
        display = message[: max(0, cols - 1)]
        start_x = max(0, (cols - len(display)) // 2)
        y = min(self.config.height // 2, lines - 1)
        try:
            self.stdscr.addstr(y, start_x, display)
        except curses.error:
            pass
        self.stdscr.refresh()
        self.stdscr.nodelay(False)
        while True:
            key = self.stdscr.getch()
            if key in (ord("q"), ord("Q")):
                break
            if key in (ord("r"), ord("R")):
                self._init_game()
                self._render()
                self.game_loop()
                break
        self.stdscr.nodelay(True)

    def game_loop(self) -> None:
        while not self.is_game_over:
            try:
                key = self.stdscr.getch()
            except curses.error:
                key = -1
            if key == ord("q"):
                break
            if key != -1:
                self._change_direction(key)
            self._update()
            self._render()
            time.sleep(self.config.tick_rate)
        self._game_over_screen()


def _run_game(stdscr: "curses._CursesWindow") -> None:
    game = SnakeGame(stdscr)
    game._render()
    game.game_loop()


def main() -> None:
    if curses is None:
        print(
            "Ta gra wymaga modułu 'curses', który nie jest dostępny w twojej instalacji Pythona.",
            file=sys.stderr,
        )
        if sys.platform.startswith("win"):
            print(
                "Na Windows zainstaluj pakiet 'windows-curses' poleceniem: pip install windows-curses",
                file=sys.stderr,
            )
        if _CURSES_IMPORT_ERROR is not None:
            print(f"Szczegóły błędu: {_CURSES_IMPORT_ERROR}", file=sys.stderr)
        sys.exit(1)
    curses.wrapper(_run_game)


if __name__ == "__main__":
    main()
'''


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    snake_path = project_root / "snake.py"
    snake_path.write_text(SNAKE_SOURCE, encoding="utf-8")
    print(f"Zastąpiono {snake_path} świeżą wersją gry Snake.")
    print("Teraz uruchom: python snake.py")


if __name__ == "__main__":
    main()
