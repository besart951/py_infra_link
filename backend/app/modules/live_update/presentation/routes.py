from __future__ import annotations

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.live_update.domain.interface import EventPublisher
from app.modules.live_update.infrastructure.broadcaster import WebSocketEventPublisher
from app.modules.live_update.infrastructure.composite_publisher import (
    CompositeEventPublisher,
)
from app.modules.live_update.infrastructure.connection_manager import ConnectionManager
from app.modules.notification.infrastructure.event_publisher import (
    NotificationEventPublisher,
)
from app.modules.notification.infrastructure.sqlalchemy_adapter import (
    SqlAlchemyNotificationAdapter,
)
from app.shared.clock import SystemClock

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


def get_event_publisher(
    request: Request,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> EventPublisher:
    """FastAPI dependency that resolves the live ``EventPublisher``.

    Returns a ``CompositeEventPublisher`` that fans out each domain event to
    both the WebSocket broadcaster and the notification persister.
    """
    manager: ConnectionManager = request.app.state.connection_manager
    ws_publisher = WebSocketEventPublisher(manager)
    notification_publisher = NotificationEventPublisher(
        SqlAlchemyNotificationAdapter(session),
        SystemClock(),
    )
    return CompositeEventPublisher(ws_publisher, notification_publisher)
