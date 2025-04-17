from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    # App info
    APP_NAME: str = "microservice"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # API settings
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    TEMP_DIR: Path = Path(BASE_DIR) / "temp"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path(TEMP_DIR) / "logs"
    LOG_FILENAME: str = f"matrx-{APP_NAME}-{APP_VERSION}.log"
    LOG_VCPRINT: bool = False

    PORT: int = 8000

    # Migration related settings.

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = 'ignore'


# Create settings instance
settings = Settings()

BASE_DIR = settings.BASE_DIR
TEMP_DIR = settings.TEMP_DIR
# Ensure directories exist
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.LOG_DIR, exist_ok=True)

# Create logging config dict
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(levelname)s %(asctime)s %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": settings.LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(settings.LOG_DIR, settings.LOG_FILENAME),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "standard",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "app": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
}
