
import pytest

from txtclk.clock.engine import get_clock_state

@pytest.mark.parametrize(
    ("hour", "minute", "expected_words", "expected_indicators"),
    [
        (7, 3, ["IT", "IS", "SEVEN"], 3),
        (7, 0, ["IT", "IS", "SEVEN"], 0),
        (7, 5, ["IT", "IS", "FIVE", "PAST", "SEVEN"], 0),
        (7, 15, ["IT", "IS", "QUARTER", "PAST", "SEVEN"], 0),
        (7, 25, ["IT", "IS", "TWENTY", "FIVE", "PAST", "SEVEN"], 0),
        (7, 30, ["IT", "IS", "HALF", "PAST", "SEVEN"], 0),
        (7, 35, ["IT", "IS", "TWENTY", "FIVE", "TO", "EIGHT"], 0),
        (7, 45, ["IT", "IS", "QUARTER", "TO", "EIGHT"], 0),
        (7, 55, ["IT", "IS", "FIVE", "TO", "EIGHT"], 0),
        (23, 55, ["IT", "IS", "FIVE", "TO", "TWELVE"], 0),
        (23, 58, ["IT", "IS", "FIVE", "TO", "TWELVE"], 3),
    ],
)
def test_get_clock_state(hour, minute, expected_words, expected_indicators):
    state = get_clock_state(hour, minute)

    assert state.words == expected_words
    assert state.minute_indicators == expected_indicators


@pytest.mark.parametrize("hour", [-1, 24])
def test_invalid_hour(hour):
    with pytest.raises(ValueError):
        get_clock_state(hour, 0)


@pytest.mark.parametrize("minute", [-1, 60])
def test_invalid_minute(minute):
    with pytest.raises(ValueError):
        get_clock_state(7, minute)
