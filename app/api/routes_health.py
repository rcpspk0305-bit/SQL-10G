"""Health check endpoint for OraCLI 10G Web API."""

from fastapi import APIRouter

from app.api.schemas import HealthResponse
from app.config.settings import settings

router = APIRouter(tags=["Health"])


@router.get("/api/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return backend server status and metadata."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.version,
        database="SQLite (Oracle 10g Compatible)",
    )
