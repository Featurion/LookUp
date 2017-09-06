import asyncio
import jugg
import socket
import ssl

from src import constants


class LookUpClient(jugg.client.Client):

    def __init__(self, host, port, certificate = None):
        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if certificate:
            socket_ = ssl.wrap_socket(
                socket_,
                ca_certs = certificate,
                cert_reqs = ssl.CERT_REQUIRED,
                ssl_version = ssl.PROTOCOL_TLSv1_2,
                ciphers = 'ECDHE-ECDSA-AES256-GCM-SHA384')

        socket_.connect((host, port))
        super().__init__(socket_ = socket_)

        self._commands[constants.CMD_HELLO] = self.handle_hello

    async def do_error(self, errno):
        # TODO: Send to interface
        pass

    async def send_hello(self, member_names : list):
        await self.send(
            jugg.core.Datagram(
                command = constants.CMD_HELLO,
                sender = self.id,
                recipient = self.id,
                data = member_names))

    async def handle_hello(self):
        pass


__all__ = [
    LookUpClient,
]
