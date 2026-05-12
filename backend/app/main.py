"""py_infra_link FastAPI application entry-point."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.engine import dispose_engine
from app.modules.building.presentation.routes import router as building_router
from app.modules.control_cabinet.presentation.routes import router as cabinet_router
from app.modules.facility.presentation.routes import router as facility_router
from app.modules.field_device.presentation.routes import router as field_device_router
from app.modules.sps_controller.presentation.routes import router as controller_router
from app.modules.sps_controller_system_type.presentation.routes import (
    router as system_type_router,
)
from app.modules.user.presentation.routes import router as user_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    try:
        yield
    finally:
        await dispose_engine()


app = FastAPI(
    title="py_infra_link",
    description="Infrastructure linking platform.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(user_router)
app.include_router(facility_router)
app.include_router(building_router)
app.include_router(cabinet_router)
app.include_router(system_type_router)
app.include_router(controller_router)
app.include_router(field_device_router)


@app.get("/healthz", tags=["health"])
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
