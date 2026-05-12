"""Typed UUID-based identity helpers.

Each domain entity gets its own ``NewType`` alias so that the type checker
rejects accidentally passing a ``BuildingId`` where a ``FacilityId`` is
expected, without introducing any runtime overhead.

Usage::

    from app.shared.ids import new_id, FacilityId

    facility_id: FacilityId = new_id(FacilityId)

``new_id`` is a typed factory — it calls ``uuid4()`` and casts the result to
the requested ``NewType``, preserving static type information.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import NewType

# ── Entity ID types ────────────────────────────────────────────────────────────
FacilityId = NewType("FacilityId", uuid.UUID)
BuildingId = NewType("BuildingId", uuid.UUID)
ControlCabinetId = NewType("ControlCabinetId", uuid.UUID)
SpsControllerId = NewType("SpsControllerId", uuid.UUID)
SpsControllerSystemTypeId = NewType("SpsControllerSystemTypeId", uuid.UUID)
FieldDeviceId = NewType("FieldDeviceId", uuid.UUID)
BacnetObjectId = NewType("BacnetObjectId", uuid.UUID)
ProjectId = NewType("ProjectId", uuid.UUID)
ProjectResourceLinkId = NewType("ProjectResourceLinkId", uuid.UUID)
NotificationId = NewType("NotificationId", uuid.UUID)
UserId = NewType("UserId", uuid.UUID)

# Generic alias used in type annotations where the exact ID type is not known.
AnyEntityId = (
    FacilityId
    | BuildingId
    | ControlCabinetId
    | SpsControllerId
    | SpsControllerSystemTypeId
    | FieldDeviceId
    | BacnetObjectId
    | ProjectId
    | ProjectResourceLinkId
    | NotificationId
    | UserId
)


def new_id[T](id_type: Callable[[uuid.UUID], T]) -> T:
    """Return a new random UUID cast to ``id_type``.

    Because ``id_type`` is a ``NewType``, this is purely a cast at runtime
    (``NewType`` constructors are identity functions), but the static type
    checker treats the result as ``T``.
    """
    return id_type(uuid.uuid4())
