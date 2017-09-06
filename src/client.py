import asyncio
import jugg
import pyarchy
import socket
import ssl

from src import constants


class LookUpZone(jugg.core.Node):

    def __init__(self, id_, stream_reader, stream_writer):
        super().__init__(stream_reader, stream_writer)

        self.id = id_

        self._commands = {}
        self._commands[constants.CMD_MSG] = self.handle_message

    def handle_message(self, dg):
        pass


class LookUpClient(jugg.client.Client):

    def __init__(self,
                 interface,
                 host : str, port : int,
                 certificate : str = None):
        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if certificate:
            socket_ = ssl.wrap_socket(
                socket_,
                ca_certs = certificate,
                cert_reqs = ssl.CERT_REQUIRED,
                ssl_version = ssl.PROTOCOL_TLSv1_2,
                ciphers = 'ECDHE-ECDSA-AES256-GCM-SHA384')

        socket_.connect((host, port))

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        super().__init__(socket_ = socket_)

        self._interface = interface
        self._username = None

        self._zones = pyarchy.data.ItemPool()
        self._zones.object_type = LookUpZone

        self._commands[constants.CMD_HELLO] = self.handle_hello

    def start(self):
        try:
            self._loop.run_until_complete(super().start())
        except:
            pass
        finally:
            self._loop.run_until_complete(self.stop())

    async def run(self):
        # Handshake is done
        self._interface.connected_signal.emit()

        # Wait for credentials
        while not self._username:
            pass

        # Send the login message
        await self.send_login(self._username)
        if self.name and self.id:
            self._interface.login_signal.emit()
        else:
            await self.stop()

        # Maintain the connection
        await super().run()

    async def stop(self):
        await super().stop()
        self._interface.stop()

    async def do_error(self, errno):
        self._interface.error_signal.emit(errno)

    async def send_hello(self, member_names : list):
        await self.send(
            jugg.core.Datagram(
                command = constants.CMD_HELLO,
                sender = self.id,
                recipient = self.id,
                data = member_names))

    async def handle_hello(self, dg):
        zone = LookUpZone(
            dg.data,
            self._stream_reader, self._stream_writer)
        self._zones.add(zone)


__all__ = [
    LookUpClient,
]
