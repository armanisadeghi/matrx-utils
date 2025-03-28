from fastapi import FastAPI
from core import settings
from .endpoints import router


def create_v1_app() -> FastAPI:
    """Create the v1 version of the API"""
    app = FastAPI(
        title=f"{settings.APP_NAME} - V1",
        version="1.0",
        description="Version 1 of the API",
        docs_url="/docs",  # This becomes /api/v1/docs when mounted
        redoc_url="/redoc"  # This becomes /api/v1/redoc when mounted
    )

    # Include the router with all the v1 endpoints
    app.include_router(router)

    return app