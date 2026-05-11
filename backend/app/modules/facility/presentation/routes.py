from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.facility.application.commands import (
    CreateFacilityCommand,
    UpdateFacilityCommand,
)
from app.modules.facility.application.queries import (
    GetFacilityQuery,
    ListFacilitiesQuery,
)
from app.modules.facility.application.use_cases import FacilityModule
from app.modules.facility.infrastructure.sqlalchemy_adapter import SqlAlchemyFacilityAdapter
from app.modules.facility.presentation.error_mapping import map_facility_error
from app.modules.facility.presentation.schemas import (
    FacilityCreate,
    FacilityRead,
    FacilityUpdate,
)
from app.shared.clock import SystemClock
from app.shared.ids import FacilityId
from app.shared.pagination import Page, PageParams
from app.shared.result import Ok

router = APIRouter(prefix="/facilities", tags=["facilities"])


@router.post("", response_model=FacilityRead, status_code=status.HTTP_201_CREATED)
async def create_facility(
    request: FacilityCreate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> FacilityRead:
    module = FacilityModule(repository=SqlAlchemyFacilityAdapter(session), clock=SystemClock())
    result = await module.create_facility(
        CreateFacilityCommand(name=request.name, description=request.description)
    )

    if isinstance(result, Ok):
        return FacilityRead.model_validate(result.value)

    raise map_facility_error(result.error)


@router.get("/{facility_id}", response_model=FacilityRead)
async def get_facility(
    facility_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> FacilityRead:
    module = FacilityModule(repository=SqlAlchemyFacilityAdapter(session), clock=SystemClock())
    result = await module.get_facility(GetFacilityQuery(facility_id=FacilityId(facility_id)))

    if isinstance(result, Ok):
        return FacilityRead.model_validate(result.value)

    raise map_facility_error(result.error)


@router.get("", response_model=Page[FacilityRead])
async def list_facilities(
    page: int = 1,
    size: int = 20,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Page[FacilityRead]:
    module = FacilityModule(repository=SqlAlchemyFacilityAdapter(session), clock=SystemClock())
    result = await module.list_facilities(
        ListFacilitiesQuery(page=PageParams(page=page, size=size))
    )

    return Page[FacilityRead](
        items=[FacilityRead.model_validate(item) for item in result.items],
        total=result.total,
        page=result.page,
        size=result.size,
    )


@router.patch("/{facility_id}", response_model=FacilityRead)
async def update_facility(
    facility_id: UUID,
    request: FacilityUpdate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> FacilityRead:
    module = FacilityModule(repository=SqlAlchemyFacilityAdapter(session), clock=SystemClock())
    result = await module.update_facility(
        UpdateFacilityCommand(
            facility_id=FacilityId(facility_id),
            name=request.name,
            description=request.description,
        )
    )

    if isinstance(result, Ok):
        return FacilityRead.model_validate(result.value)

    raise map_facility_error(result.error)


@router.delete("/{facility_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_facility(
    facility_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Response:
    module = FacilityModule(repository=SqlAlchemyFacilityAdapter(session), clock=SystemClock())
    result = await module.delete_facility(facility_id=FacilityId(facility_id))

    if isinstance(result, Ok):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise map_facility_error(result.error)
