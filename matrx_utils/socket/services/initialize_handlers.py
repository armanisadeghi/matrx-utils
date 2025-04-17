from core.services.socketio_app import sio
from matrx_utils.socket.core.service_factory import ServiceFactory


def initialize_socketio_handlers():
    service_factory = ServiceFactory()
    service_factory.register_default_services()

    import matrx_utils.socket.core.global_socket_events