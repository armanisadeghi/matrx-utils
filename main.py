from dotenv import load_dotenv
load_dotenv()
from matrx_utils.common import vcprint
vcprint("[main.py] Loaded environment variables", color="green")

import uvicorn
from app.api import create_app
from core import settings, get_logger
from socketio import ASGIApp
from core.services.socketio_app import sio
from matrx_utils.socket.core.user_sessions import get_user_session_namespace


app = create_app()
logger = get_logger()

socketio_app = ASGIApp(sio, static_files={"/static/": settings.STATIC_ROOT})

user_session_namespace = get_user_session_namespace()
sio.register_namespace(user_session_namespace)

app.mount("/socket.io", socketio_app)


if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} env={settings.ENVIRONMENT} debug={settings.DEBUG}")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=settings.PORT,
        reload=settings.DEBUG
    )