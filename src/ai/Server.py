import jugg
import pyarchy
import socket
import ssl

from src.base import settings

from src.node.ClientAI import LookUpClientAI
from src.zones.ZoneAI import LookUpZoneAI

class LookUpServer(jugg.server.Server):

    client_handler = LookUpClientAI

    def __init__(self, host, port):
        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if settings.WANT_TLS:
            socket_ = ssl.wrap_socket(
                socket_,
                keyfile = settings.KEY_PATH,
                certfile = settings.CERT_PATH,
                server_side = True,
                ssl_version = ssl.PROTOCOL_TLSv1_2,
                do_handshake_on_connect = True,
                ciphers = 'ECDHE-ECDSA-AES256-GCM-SHA384')

        socket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_.bind((host, port))

        super().__init__(
            socket_ = socket_,
            hmac_key = settings.HMAC_KEY,
            challenge_key = settings.CHALLENGE_KEY)

        self._banned = pyarchy.data.ItemPool()
        self._banned.object_type = tuple

        self._zones = pyarchy.data.ItemPool()
        self._zones.object_type = LookUpZoneAI

    async def new_connection(self, streamReader, streamWriter):
        if streamWriter.transport._sock.getpeername() in self._banned:
            streamWriter.close()
        else:
            try:
                await super().new_connection(
                    streamReader, streamWriter,
                    server = self)
            except ConnectionResetError:
                pass
