import asyncio
import jugg
import pyarchy
import socket
import ssl

from src import constants, settings


class LookUpClientAI(jugg.server.ClientAI):

    def __init__(self, *args, server = None):
        super().__init__(*args)

        self._server = server

        self._commands[constants.CMD_HELLO] = self.handle_hello
        self._commands[constants.CMD_READY] = self.handle_ready

    def verify_credentials(self, data):
        return super().verify_credentials(data)

    async def handle_hello(self, dg):
        for name in dg.data:
            try:
                client = self._server.clients.get(
                    self._server.clients,
                    lambda e: e.name == name)
            except KeyError:
                # Red light
                pass
        else:
            # Green light
            pass

    async def handle_ready(self, dg):
        pass


class LookUpServer(jugg.server.Server):

    client_handler = LookUpClientAI

    def __init__(self):
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
        socket_.bind((settings.HOST, settings.PORT))

        super().__init__(
            socket_ = socket_,
            hmac_key = settings.HMAC_KEY,
            challenge_key = settings.CHALLENGE_KEY)

        self._banned = pyarchy.data.ItemPool()
        self._banned.object_type = tuple

    async def new_connection(self, stream_reader, stream_writer):
        if stream_writer.transport._sock.getpeername() in self._banned:
            stream_writer.close()
        else:
            await super().new_connection(
                stream_reader, stream_writer,
                server = self)


__all__ = [
    LookUpClientAI,
    LookUpServer,
]
