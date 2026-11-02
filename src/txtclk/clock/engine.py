
"""Clock engine for converting time into word-clock output."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ClockState:
    """Represents the current word-clock state."""

    words: list[str]
    minute_indicators: int


def get_clock_state(hour: int, minute: int) -> ClockState:
    """Convert an hour and minute into a word-clock state."""

    if not 0 <= hour <= 23:
        raise ValueError("Hour must be between 0 and 23")

    if not 0 <= minute <= 59:
        raise ValueError("Minute must be between 0 and 59")

    rounded_minutes = (minute // 5) * 5
    minute_indicators = minute % 5

    display_hour = hour

    if rounded_minutes > 30:
        display_hour = (hour + 1) % 24

    display_hour %= 12

    if display_hour == 0:
        display_hour = 12

    words = ["IT", "IS"]

    if rounded_minutes == 0:
        words.extend([_get_hour_word(display_hour)])

    elif rounded_minutes == 5:
        words.extend(["FIVE", "PAST", _get_hour_word(display_hour)])

    elif rounded_minutes == 10:
        words.extend(["TEN", "PAST", _get_hour_word(display_hour)])

    elif rounded_minutes == 15:
        words.extend(["QUARTER", "PAST", _get_hour_word(display_hour)])

    elif rounded_minutes == 20:
        words.extend(["TWENTY", "PAST", _get_hour_word(display_hour)])

    elif rounded_minutes == 25:
        words.extend(["TWENTY", "FIVE", "PAST", _get_hour_word(display_hour)])

    elif rounded_minutes == 30:
        words.extend(["HALF", "PAST", _get_hour_word(display_hour)])

    elif rounded_minutes == 35:
        words.extend(["TWENTY", "FIVE", "TO", _get_hour_word(display_hour)])

    elif rounded_minutes == 40:
        words.extend(["TWENTY", "TO", _get_hour_word(display_hour)])

    elif rounded_minutes == 45:
        words.extend(["QUARTER", "TO", _get_hour_word(display_hour)])

    elif rounded_minutes == 50:
        words.extend(["TEN", "TO", _get_hour_word(display_hour)])

    elif rounded_minutes == 55:
        words.extend(["FIVE", "TO", _get_hour_word(display_hour)])

    return ClockState(
        words=words,
        minute_indicators=minute_indicators,
    )


def _get_hour_word(hour: int) -> str:
    """Return the English word for an hour."""

    hour_words = {
        1: "ONE",
        2: "TWO",
        3: "THREE",
        4: "FOUR",
        5: "FIVE",
        6: "SIX",
        7: "SEVEN",
        8: "EIGHT",
        9: "NINE",
        10: "TEN",
        11: "ELEVEN",
        12: "TWELVE",
    }

    return hour_words[hour]
