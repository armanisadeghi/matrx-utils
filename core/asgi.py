import dotenv
from matrx_utils.common import vcprint
import os
import socketio
from core.services.socketio_app import sio
from core import settings

dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

vcprint("[ASGI] Environment variables loaded", color="green")

socketio_app = socketio.ASGIApp(sio, static_files={"/static/": settings.STATIC_ROOT})

