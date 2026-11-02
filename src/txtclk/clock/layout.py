
"""Letter grid and word-to-coordinate mapping."""

from typing import Final

GRID: Final[tuple[str, ...]] = (
    "ITLISASAMPM",
    "ACQUARTERDC",
    "TWENTYFIVEX",
    "HALFSTENFTO",
    "PASTERUNINE",
    "ONESIXTHREE",
    "FOURFIVETWO",
    "EIGHTELEVEN",
    "SEVENTWELVE",
    "TENSRABCJUF",
)

ROWS: Final[int] = len(GRID)
COLS: Final[int] = len(GRID[0])

# Coordinates use (row, column), both zero-based.
WORD_POSITIONS: Final[dict[str, tuple[int, int, int]]] = {
    "IT": (0, 0, 2),
    "IS": (0, 3, 2),
    "AM": (0, 7, 2),
    "PM": (0, 9, 2),
    "QUARTER": (1, 2, 7),
    "TWENTY": (2, 0, 6),
    "HALF": (3, 0, 4),
    "PAST": (4, 0, 4),
    "TO": (3, 9, 2),
    "NINE": (4, 7, 4),
    "ONE": (5, 0, 3),
    "SIX": (5, 3, 3),
    "THREE": (5, 6, 5),
    "FOUR": (6, 0, 4),
    "TWO": (6, 8, 3),
    "EIGHT": (7, 0, 5),
    "ELEVEN": (7, 5, 6),
    "SEVEN": (8, 0, 5),
    "TWELVE": (8, 5, 6),
    "FIVE_HOUR": (6, 4, 4),
    "FIVE_MINUTE": (2, 6, 4),
    "TEN_HOUR": (9, 0, 3),
    "TEN_MINUTE": (3, 5, 3),
}


def get_word_coordinates(words: list[str]) -> list[tuple[int, int]]:
    """Return all illuminated letter coordinates for the given words."""

    coordinates: list[tuple[int, int]] = []

    for index, word in enumerate(words):
        if word in ("FIVE", "TEN"):
            position_type = "HOUR" if index == len(words) - 1 else "MINUTE"
            position = WORD_POSITIONS[f"{word}_{position_type}"]
        else:
            position = WORD_POSITIONS[word]

        row, start_col, length = position

        for col in range(start_col, start_col + length):
            coordinates.append((row, col))

    return coordinates
