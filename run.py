import os
import sys
import logging
import socket
from datetime import datetime
from cryptography.utils import CryptographyDeprecationWarning
import warnings
import uvicorn
from core.settings import settings  # Keep core.settings (Pydantic)

directories_to_ensure = [
    f"/var/log/{settings.LOG_FILENAME}",
    "temp",
    "reports",
    f"/var/log/{settings.APP_NAME}/"
]

for directory in directories_to_ensure:
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        print(f"Error creating directory {directory}: {e}")
        sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"/var/log/{settings.APP_NAME}/run_py.log"),
    ],
)
logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    print(f"[AI MATRX] {settings.APP_NAME} Server | Version {settings.APP_VERSION}\n")
    logger.info(f"Starting run.py at {datetime.now()}")

    host = os.environ.get("HOST", "0.0.0.0")
    preferred_port = int(os.environ.get("PORT", 8000))

    logger.info(f"Preferred host: {host}, Preferred port: {preferred_port}")

    if is_port_in_use(preferred_port):
        logger.warning(f"Port {preferred_port} is in use. Finding a random available port.")
        print(f"Port {preferred_port} is in use. Finding a random available port.")
        port = find_free_port()
        logger.info(f"Found available port: {port}")
    else:
        port = preferred_port
        logger.info(f"Using preferred port: {port}")

    logger.info(f"Starting server on http://{host}:{port}")
    print(f"Starting server on http://{host}:{port}")
    print(f"Local Link: http://localhost:{port}")

    try:
        logger.info("Attempting to start Uvicorn...")
        uvicorn.run("main:app", host=host, port=port, log_level="info")
    except Exception as e:
        logger.error(f"Error starting Uvicorn: {str(e)}", exc_info=True)
        sys.exit(1)

    from matrx_utils.common import vcprint
    vcprint("\n[FINE!] You want to leave? See if I care!\n\nBye Boo!\n", color="pink")