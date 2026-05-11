from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.building.application.commands import (
    CreateBuildingCommand,
    UpdateBuildingCommand,
)
from app.modules.building.application.queries import (
    GetBuildingQuery,
    ListBuildingsQuery,
)
from app.modules.building.application.use_cases import BuildingModule
from app.modules.building.infrastructure.sqlalchemy_adapter import SqlAlchemyBuildingAdapter
from app.modules.building.presentation.error_mapping import map_building_error
from app.modules.building.presentation.schemas import (
    BuildingCreate,
    BuildingRead,
    BuildingUpdate,
)
from app.modules.facility.infrastructure.sqlalchemy_adapter import SqlAlchemyFacilityAdapter
from app.shared.clock import SystemClock
from app.shared.ids import BuildingId, FacilityId
from app.shared.pagination import Page, PageParams
from app.shared.result import Ok

router = APIRouter(prefix="/facilities/{facility_id}/buildings", tags=["buildings"])


@router.post("", response_model=BuildingRead, status_code=status.HTTP_201_CREATED)
async def create_building(
    facility_id: UUID,
    request: BuildingCreate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> BuildingRead:
    module = BuildingModule(
        building_repository=SqlAlchemyBuildingAdapter(session),
        facility_repository=SqlAlchemyFacilityAdapter(session),
        clock=SystemClock(),
    )
    result = await module.create_building(
        CreateBuildingCommand(
            facility_id=FacilityId(facility_id),
            name=request.name,
            description=request.description,
        )
    )

    if isinstance(result, Ok):
        return BuildingRead.model_validate(result.value)

    raise map_building_error(result.error)


@router.get("/{building_id}", response_model=BuildingRead)
async def get_building(
    facility_id: UUID,
    building_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> BuildingRead:
    module = BuildingModule(
        building_repository=SqlAlchemyBuildingAdapter(session),
        facility_repository=SqlAlchemyFacilityAdapter(session),
        clock=SystemClock(),
    )
    result = await module.get_building(
        GetBuildingQuery(facility_id=FacilityId(facility_id), building_id=BuildingId(building_id))
    )

    if isinstance(result, Ok):
        return BuildingRead.model_validate(result.value)

    raise map_building_error(result.error)


@router.get("", response_model=Page[BuildingRead])
async def list_buildings(
    facility_id: UUID,
    page: int = 1,
    size: int = 20,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Page[BuildingRead]:
    module = BuildingModule(
        building_repository=SqlAlchemyBuildingAdapter(session),
        facility_repository=SqlAlchemyFacilityAdapter(session),
        clock=SystemClock(),
    )
    result = await module.list_buildings(
        ListBuildingsQuery(
            facility_id=FacilityId(facility_id), page=PageParams(page=page, size=size)
        )
    )

    return Page[BuildingRead](
        items=[BuildingRead.model_validate(item) for item in result.items],
        total=result.total,
        page=result.page,
        size=result.size,
    )


@router.patch("/{building_id}", response_model=BuildingRead)
async def update_building(
    facility_id: UUID,
    building_id: UUID,
    request: BuildingUpdate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> BuildingRead:
    module = BuildingModule(
        building_repository=SqlAlchemyBuildingAdapter(session),
        facility_repository=SqlAlchemyFacilityAdapter(session),
        clock=SystemClock(),
    )
    result = await module.update_building(
        UpdateBuildingCommand(
            facility_id=FacilityId(facility_id),
            building_id=BuildingId(building_id),
            name=request.name,
            description=request.description,
        )
    )

    if isinstance(result, Ok):
        return BuildingRead.model_validate(result.value)

    raise map_building_error(result.error)


@router.delete("/{building_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_building(
    facility_id: UUID,
    building_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Response:
    module = BuildingModule(
        building_repository=SqlAlchemyBuildingAdapter(session),
        facility_repository=SqlAlchemyFacilityAdapter(session),
        clock=SystemClock(),
    )
    result = await module.delete_building(
        facility_id=FacilityId(facility_id), building_id=BuildingId(building_id)
    )

    if isinstance(result, Ok):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise map_building_error(result.error)
