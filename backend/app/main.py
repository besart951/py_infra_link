"""py_infra_link FastAPI application entry-point."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.engine import dispose_engine
from app.modules.bacnet_object.presentation.routes import router as bacnet_object_router
from app.modules.building.presentation.routes import router as building_router
from app.modules.control_cabinet.presentation.routes import router as cabinet_router
from app.modules.facility.presentation.routes import router as facility_router
from app.modules.field_device.presentation.routes import router as field_device_router
from app.modules.live_update.infrastructure.connection_manager import ConnectionManager
from app.modules.live_update.presentation.routes import router as ws_router
from app.modules.project.presentation.routes import router as project_router
from app.modules.project_resource_link.presentation.routes import (
    import_router as project_import_router,
)
from app.modules.project_resource_link.presentation.routes import (
    router as project_link_router,
)
from app.modules.sps_controller.presentation.routes import router as controller_router
from app.modules.sps_controller_system_type.presentation.routes import (
    router as system_type_router,
)
from app.modules.user.presentation.routes import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    app.state.connection_manager = ConnectionManager()
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

app.include_router(ws_router)
app.include_router(user_router)
app.include_router(facility_router)
app.include_router(building_router)
app.include_router(cabinet_router)
app.include_router(system_type_router)
app.include_router(controller_router)
app.include_router(field_device_router)
app.include_router(bacnet_object_router)
app.include_router(project_router)
app.include_router(project_link_router)
app.include_router(project_import_router)


@app.get("/healthz", tags=["health"])
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
