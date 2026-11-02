
from txtclk.clock.layout import GRID, get_word_coordinates


def test_grid_dimensions():
    assert len(GRID) == 10
    assert all(len(row) == 11 for row in GRID)


def test_it_is_seven():
    coordinates = get_word_coordinates(["IT", "IS", "SEVEN"])

    assert coordinates == [
        (0, 0), (0, 1),
        (0, 3), (0, 4),
        (8, 0), (8, 1), (8, 2), (8, 3), (8, 4),
    ]


def test_twenty_five_past_seven():
    coordinates = get_word_coordinates(
        ["IT", "IS", "TWENTY", "FIVE", "PAST", "SEVEN"]
    )

    assert (2, 6) in coordinates
    assert (6, 4) not in coordinates


def test_five_to_five():
    coordinates = get_word_coordinates(
        ["IT", "IS", "FIVE", "TO", "FIVE"]
    )

    # First FIVE is the minute word, second is the hour word.
    assert (2, 6) in coordinates
    assert (6, 4) in coordinates
