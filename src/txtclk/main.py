
"""Main entry point for txtclk."""

from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from fastapi import FastAPI, HTTPException
from txtclk.clock.engine import get_clock_state
from txtclk.clock.layout import GRID, get_word_coordinates

from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from txtclk.config.config import ConfigConnectionManager, load_config, save_config, DEFAULT_CONFIG, ClockConfig

app = FastAPI(
    title="txtclk",
    description="A text-based clock",
    version="0.1.0",
)

WEB_DIR = Path(__file__).parent / "web"


config_manager = ConfigConnectionManager()
    
app.mount(
    "/static",
    StaticFiles(directory=WEB_DIR / "static"),
    name="static",
)

@app.get("/")
def index():
    return FileResponse(WEB_DIR / "index.html")

@app.get("/display")
def display():
    return FileResponse(WEB_DIR / "display.html")

@app.get("/extras")
def extras():
    return FileResponse(WEB_DIR / "extras.html")

@app.get("/config")
def config_page():
    return FileResponse(WEB_DIR / "config.html")

@app.get("/health")
def health():
    """Check whether the application is running."""
    return {"status": "ok"}

@app.websocket("/ws/config")
async def config_websocket(websocket: WebSocket):
    await config_manager.connect(websocket)

    try:
        # Send the current settings immediately upon connection.
        await websocket.send_json(load_config().model_dump())

        # Keep the connection alive and detect disconnected clients.
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        config_manager.disconnect(websocket)

@app.get("/api/config")
def get_config():
    return load_config().model_dump()

@app.put("/api/config")
async def update_config(config: ClockConfig):
    try:
        save_config(config)
    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail="Could not save configuration.",
        ) from error

    await config_manager.broadcast(config.model_dump())

    return config.model_dump()

@app.delete("/api/config")
async def reset_config():
    try:
        save_config(DEFAULT_CONFIG)
    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail="Could not reset configuration.",
        ) from error

    await config_manager.broadcast(DEFAULT_CONFIG.model_dump())

    return DEFAULT_CONFIG.model_dump()

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
