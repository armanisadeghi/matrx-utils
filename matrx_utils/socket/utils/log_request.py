# matrx_utils\socket\utils\log_request.py
from matrx_utils import vcprint

verbose = True
debug = False
info = False


def log_socket_request(file, handler, event, namespace, sid, data):
    print("\n")
    start = "=" * 10 + f"  NEW SOCKET EVENT RECEIVED BY {file} " + "=" * 10
    end = "=" * 50
    vcprint(start, verbose=verbose, color="lavender")
    vcprint(event, "Event", verbose=verbose, color="blue", inline=True)
    vcprint(namespace, "Namespace", verbose=verbose, color="blue", inline=True)
    vcprint(sid, "SID", verbose=verbose, color="blue", inline=True)
    vcprint(handler, "Handler", verbose=verbose, color="blue", inline=True)
    vcprint(data, "Request Data", verbose=verbose, pretty=True, color="blue")
    print("")
    vcprint(end, verbose=verbose, color="lavender")
    print("\n")

async def handle_error(stream_handler, error_message):
    vcprint(
        verbose=True,
        data=str(error_message),
        title="[Simple Recipe ERROR]",
        color="red",
    )
    await stream_handler.send_error(str(error_message))
