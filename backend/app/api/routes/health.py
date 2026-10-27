"""Health check endpoint."""

from fastapi import APIRouter

from app.api.schemas import HealthResponse
from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return application health status."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        gemini_configured=bool(settings.gemini_api_key),
        github_configured=bool(settings.github_token),
    )
