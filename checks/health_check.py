from models.response_models import HealthResponse
import time
from core import settings


def get_default_response():
    return HealthResponse(
        status=True,
        timestamp=time.time(),
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        checks={}
    ).model_dump()