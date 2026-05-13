from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from app.shared.ids import (
    BuildingId,
    ControlCabinetId,
    FieldDeviceId,
    SpsControllerId,
)


def _uuid_set() -> set[uuid.UUID]:
    return set()


def _uuid_list_map() -> dict[uuid.UUID, list[uuid.UUID]]:
    return {}


@dataclass(frozen=True, slots=True)
class InMemoryHierarchyReader:
    """In-memory implementation of HierarchyReader for use in tests.

    Seed data via the ``add_*`` helper methods after construction.
    """

    _buildings: set[uuid.UUID] = field(default_factory=_uuid_set)
    _cabinets_by_building: dict[uuid.UUID, list[uuid.UUID]] = field(
        default_factory=_uuid_list_map
    )
    _controllers_by_cabinet: dict[uuid.UUID, list[uuid.UUID]] = field(
        default_factory=_uuid_list_map
    )
    _devices_by_controller: dict[uuid.UUID, list[uuid.UUID]] = field(
        default_factory=_uuid_list_map
    )

    def add_building(self, building_id: BuildingId) -> None:
        self._buildings.add(uuid.UUID(str(building_id)))

    def add_cabinet(
        self, building_id: BuildingId, cabinet_id: ControlCabinetId
    ) -> None:
        key = uuid.UUID(str(building_id))
        self._cabinets_by_building.setdefault(key, []).append(
            uuid.UUID(str(cabinet_id))
        )

    def add_controller(
        self, cabinet_id: ControlCabinetId, controller_id: SpsControllerId
    ) -> None:
        key = uuid.UUID(str(cabinet_id))
        self._controllers_by_cabinet.setdefault(key, []).append(
            uuid.UUID(str(controller_id))
        )

    def add_device(
        self, controller_id: SpsControllerId, device_id: FieldDeviceId
    ) -> None:
        key = uuid.UUID(str(controller_id))
        self._devices_by_controller.setdefault(key, []).append(
            uuid.UUID(str(device_id))
        )

    async def building_exists(self, building_id: BuildingId) -> bool:
        return uuid.UUID(str(building_id)) in self._buildings

    async def list_cabinet_ids_for_building(
        self, building_id: BuildingId
    ) -> list[ControlCabinetId]:
        key = uuid.UUID(str(building_id))
        return [
            ControlCabinetId(cid)
            for cid in self._cabinets_by_building.get(key, [])
        ]

    async def list_controller_ids_for_cabinet(
        self, cabinet_id: ControlCabinetId
    ) -> list[SpsControllerId]:
        key = uuid.UUID(str(cabinet_id))
        return [
            SpsControllerId(cid)
            for cid in self._controllers_by_cabinet.get(key, [])
        ]

    async def list_device_ids_for_controller(
        self, controller_id: SpsControllerId
    ) -> list[FieldDeviceId]:
        key = uuid.UUID(str(controller_id))
        return [
            FieldDeviceId(did)
            for did in self._devices_by_controller.get(key, [])
        ]
