# File: app/api/v1/endpoints.py

from fastapi import APIRouter

from core import get_logger, settings
from checks.health_check import get_default_response

router = APIRouter()
logger = get_logger()


@router.get("/", tags=["v1"])
async def root():
    """Root endpoint"""
    logger.debug("Root endpoint called")
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_PREFIX}/docs"
    }


@router.get("/health", tags=["v1"], response_model=dict)
async def health_check():
    return get_default_response()
