from __future__ import annotations

import json
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Tracks active WebSocket connections and fans out broadcast messages."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def broadcast(self, data: dict[str, str | dict[str, str]]) -> None:
        """Send JSON-encoded ``data`` to every active connection.

        Silently removes connections that can no longer receive messages.
        """
        message = json.dumps(data)
        dead: list[WebSocket] = []
        for conn in list(self._connections):
            try:
                await conn.send_text(message)
            except Exception:
                dead.append(conn)
        for conn in dead:
            self.disconnect(conn)
