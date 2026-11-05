from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "provider": settings.tryon_provider,
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
