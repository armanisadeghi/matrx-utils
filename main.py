import uvicorn
from app.api import create_app
from core import settings, get_logger

app = create_app()
logger = get_logger()

if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} env={settings.ENVIRONMENT} debug={settings.DEBUG}")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=settings.PORT,
        reload=settings.DEBUG
    )