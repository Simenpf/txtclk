
"""Main entry point for txtclk."""

from datetime import datetime

from fastapi import FastAPI, HTTPException

from txtclk.clock.engine import get_clock_state
from txtclk.clock.layout import GRID, get_word_coordinates

from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="txtclk",
    description="A text-based clock",
    version="0.1.0",
)

WEB_DIR = Path(__file__).parent / "web"

app.mount(
    "/static",
    StaticFiles(directory=WEB_DIR / "static"),
    name="static",
)

@app.get("/display")
def display():
    return FileResponse(WEB_DIR / "display.html")


@app.get("/health")
def health():
    """Check whether the application is running."""
    return {"status": "ok"}


@app.get("/api/clock")
def get_clock(hour: int | None = None, minute: int | None = None):
    """Get the current clock state or preview a specific time."""

    if (hour is None) != (minute is None):
        raise HTTPException(
            status_code=400,
            detail="Hour and minute must be provided together.",
        )

    if hour is None or minute is None:
        now = datetime.now().astimezone()
        hour = now.hour
        minute = now.minute

    try:
        state = get_clock_state(hour, minute)
        coordinates = get_word_coordinates(state.words)
    except (ValueError, KeyError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "time": f"{hour:02d}:{minute:02d}",
        "words": state.words,
        "minute_indicators": state.minute_indicators,
        "grid": GRID,
        "active_cells": coordinates,
    }
