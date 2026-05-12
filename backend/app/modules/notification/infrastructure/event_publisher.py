from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.modules.live_update.domain.events import DomainEvent, DomainEventType
from app.modules.notification.domain.interface import NotificationRepository
from app.modules.notification.domain.models import Notification
from app.shared.clock import Clock
from app.shared.ids import NotificationId, UserId, new_id


@dataclass(frozen=True, slots=True)
class NotificationEventPublisher:
    """EventPublisher adapter that persists a Notification for each domain event.

    Maps every supported ``DomainEventType`` to a human-readable notification
    targeted at the resource owner (extracted from ``event.payload["owner_id"]``).
    Events without an ``owner_id`` in their payload are silently ignored.
    """

    _repository: NotificationRepository
    _clock: Clock

    async def publish(self, event: DomainEvent) -> None:
        notification = self._map(event)
        if notification is not None:
            await self._repository.create(notification)

    def _map(self, event: DomainEvent) -> Notification | None:
        owner_id_str = event.payload.get("owner_id")
        if not owner_id_str:
            return None
        user_id = UserId(uuid.UUID(owner_id_str))

        match event.event_type:
            case DomainEventType.PROJECT_CREATED:
                title = "Project created"
                body = f"Project \"{event.payload.get('name', '')}\" has been created."
            case DomainEventType.PROJECT_UPDATED:
                title = "Project updated"
                body = f"Project \"{event.payload.get('name', '')}\" has been updated."
            case DomainEventType.PROJECT_DELETED:
                title = "Project deleted"
                body = "One of your projects has been deleted."
            case DomainEventType.PROJECT_RESOURCE_LINKED:
                resource_type = event.payload.get("resource_type", "resource")
                title = "Resource linked"
                body = f"A {resource_type} has been linked to your project."
            case DomainEventType.PROJECT_RESOURCE_UNLINKED:
                title = "Resource unlinked"
                body = "A resource has been unlinked from your project."
            case DomainEventType.PROJECT_BUILDING_IMPORTED:
                linked = event.payload.get("linked", "0")
                title = "Building imported"
                body = f"{linked} resource(s) have been imported from a building."
            case _:
                return None

        return Notification(
            id=new_id(NotificationId),
            user_id=user_id,
            title=title,
            body=body,
            is_read=False,
            created_at=self._clock.now(),
        )
