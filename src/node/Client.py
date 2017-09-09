import asyncio
import jugg
import pyarchy
import socket
import ssl

from src.base import constants

from src.zones.Zone import LookUpZone

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

        super().__init__(socket_ = socket_)

        self._interface = interface
        self._username = None

        self._zones = pyarchy.data.ItemPool()
        self._zones.object_type = LookUpZone

        self._commands[constants.CMD_HELLO] = self.handleHello
        self._commands[constants.CMD_MSG] = self.handleMessage

    def synchronousSend(self, **kwargs):
        kwargs.pop('sender', None)
        asyncio.new_event_loop().run_until_complete(
            self.send(
                jugg.core.Datagram(
                    sender = self.id,
                    **kwargs)))

    async def stop(self):
        await super().stop()
        self._interface.stop()

    async def handle_handshake(self, dg):
        await super().handle_handshake(dg)
        self._interface.connected_signal.emit()

    async def handle_login(self, dg):
        await super().handle_login(dg)
        self._interface.login_signal.emit()

    async def doError(self, errno):
        self._interface.error_signal.emit(errno)

    async def handleHello(self, dg):
        self._interface.hello_signal.emit(dg.sender, dg.data)

    async def handleMessage(self, dg):
        try:
            zone = self._zones.get(
                self._zones,
                lambda e: e.id == dg.sender)

            dg = jugg.core.Datagram.from_string(dg.data)
            await zone.handle_datagram(dg)
        except KeyError:
            self._interface._window.new_zone_signal.emit(dg.sender)
