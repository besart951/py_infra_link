from __future__ import annotations

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

from app.modules.live_update.domain.interface import EventPublisher
from app.modules.live_update.infrastructure.broadcaster import WebSocketEventPublisher
from app.modules.live_update.infrastructure.connection_manager import ConnectionManager

router = APIRouter(tags=["live-updates"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Accept WebSocket connections and keep them alive for event streaming."""
    manager: ConnectionManager = websocket.app.state.connection_manager
    await manager.connect(websocket)
    try:
        while True:
            # Drain any incoming frames to detect disconnect; clients are
            # receive-only in this design.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def get_event_publisher(request: Request) -> EventPublisher:
    """FastAPI dependency that resolves the live ``EventPublisher``.

    Reads the shared ``ConnectionManager`` from ``app.state`` (set in the
    application lifespan) and wraps it in a ``WebSocketEventPublisher``.
    """
    manager: ConnectionManager = request.app.state.connection_manager
    return WebSocketEventPublisher(manager)
