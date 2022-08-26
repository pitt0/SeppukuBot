from dataclasses import dataclass
from enum import Enum

from .typings import Position


__all__ = (
    'Turn',
    'Board'
)

class Turn(Enum):
    X = 1
    O = -1

@dataclass
class Board:
    _board: list[list[Position]] = None # type: ignore

    def __post_init__(self):
        self._board = [[0 for _ in range(3)] for _ in range(3)]

    def place(self, symbol: Turn, x: int, y: int) -> None:
        self._board[y][x] = symbol.value

    def auto_place(self, symbol: Turn) -> None:
        pass

    def placeable(self, x: int, y: int) -> bool:
        return self._board[y][x] == 0

    def is_full(self) -> bool:
        return not any(sp == 0 for row in self._board for sp in row)

    def game_ended(self) -> bool:
        if any(sum(row) in (3, -3) for row in self._board):
            # Rows
            return True
        if any(sum(row[col] for row in self._board) in (3, -3) for col in range(3)):
            # Columns
            return True
        if self._board[0][0] + self._board[1][1] + self._board[2][2] in (3, -3):
            # Oblique 7-3
            return True
        if self._board[0][2] + self._board[1][1] + self._board[2][0] in (3, -3):
            # Oblique 9-1
            return True

        return self.is_full()