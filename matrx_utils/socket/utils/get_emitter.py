from matrx_utils.socket.response.socket_emitter import SocketEmitter


def get_emitter(event_id, sid, namespace="/UserSession"):
    SocketEmitter(event_id, sid, namespace)