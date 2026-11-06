from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from txtclk.config.config import (
    ConfigConnectionManager,
    load_config,
    save_config,
    DEFAULT_CONFIG,
    ClockConfig,
)

config_manager = ConfigConnectionManager()


router = APIRouter(prefix="/api", tags=["config"])
websocket_router = APIRouter()

@router.get("/config")
def get_config():
    return load_config().model_dump()

@router.put("/config")
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

@router.delete("/config")
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

@websocket_router.websocket("/ws/config")
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