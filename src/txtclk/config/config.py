from pathlib import Path
from pydantic import BaseModel, Field
from fastapi import WebSocket
import json
import os

CONFIG_PATH = Path(
    os.environ.get(
        "TXTCLK_CONFIG_PATH",
        str(Path(__file__).resolve().parents[3] / "data" / "config.json"),
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