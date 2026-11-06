
"""Main entry point for txtclk."""

from datetime import datetime
from txtclk.api import clock, config
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

app.include_router(clock.router)
app.include_router(config.router)
app.include_router(config.websocket_router)


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