from fastapi import APIRouter

from .config import settings

router = APIRouter(prefix="/docs", tags=["docs"])


@router.get("/capabilities")
async def get_capabilities():
    return {
        "provider_type": settings.provider_type,
        "features": ["client_management", "stats", "config_generation"],
    }
