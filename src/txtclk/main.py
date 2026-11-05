
"""Main entry point for txtclk."""

from datetime import datetime
import os
from fastapi import WebSocket, WebSocketDisconnect
from fastapi import FastAPI, HTTPException
import subprocess
from fastapi import Response
import json
from txtclk.clock.engine import get_clock_state
from txtclk.clock.layout import GRID, get_word_coordinates

from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(
    title="txtclk",
    description="A text-based clock",
    version="0.1.0",
)

WEB_DIR = Path(__file__).parent / "web"

CONFIG_PATH = Path(
    os.environ.get(
        "TXTCLK_CONFIG_PATH",
        str(Path(__file__).resolve().parents[2] / "data" / "config.json"),
    )
)


class ClockConfig(BaseModel):
    background: str = Field("#080808", pattern=r"^#[0-9a-fA-F]{6}$")
    inactive_color: str = Field("#303030", pattern=r"^#[0-9a-fA-F]{6}$")
    active_color: str = Field("#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    indicator_color: str = Field("#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")

    glow_intensity: int = Field(12, ge=0, le=40)
    clock_width_vw: float = Field(90, ge=30, le=99)
    letter_size_vw: float = Field(5, ge=1, le=10)
    grid_gap_px: int = Field(0, ge=0, le=20)

    offset_x_px: int = Field(0, ge=-200, le=200)
    offset_y_px: int = Field(0, ge=-200, le=200)

    indicator_size_px: int = Field(10, ge=2, le=30)
    indicator_offset_px: int = Field(20, ge=0, le=100)

DEFAULT_CONFIG = ClockConfig()

class ConfigConnectionManager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, config: dict):
        disconnected = []

        for connection in self.connections:
            try:
                await connection.send_json(config)
            except Exception:
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(connection)


config_manager = ConfigConnectionManager()



def load_config() -> ClockConfig:
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG

    try:
        data = json.loads(CONFIG_PATH.read_text())
        return ClockConfig.model_validate(data)
    except (ValueError, OSError):
        return DEFAULT_CONFIG


def save_config(config: ClockConfig) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = CONFIG_PATH.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(config.model_dump(), indent=4)
    )
    temporary_path.replace(CONFIG_PATH)


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

@app.post("/api/system/reboot")
def reboot_pi():
    try:
        subprocess.Popen(
            ["sudo", "-n", "/usr/sbin/reboot"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {"status": "rebooting"}
    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail="Could not start Raspberry Pi reboot.",
        ) from error

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
