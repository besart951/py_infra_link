"""py_infra_link FastAPI application entry-point."""

from __future__ import annotations

from fastapi import FastAPI

from app.database.engine import dispose_engine

app = FastAPI(
    title="py_infra_link",
    description="Infrastructure linking platform.",
    version="0.1.0",
)


@app.on_event("shutdown")
async def _on_shutdown() -> None:
    await dispose_engine()


@app.get("/healthz", tags=["health"])
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
