import asyncio
import jugg
import pyarchy
import socket
import ssl

from src import constants
from src.gui import utils


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

        self._commands[constants.CMD_HELLO] = self.handle_hello
        self._commands[constants.CMD_MSG] = self.handle_message

    def syncronous_send(self, **kwargs):
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

    async def do_error(self, errno):
        self._interface.error_signal.emit(errno)

    async def handle_hello(self, dg):
        self._interface.hello_signal.emit(dg.sender, dg.data)

    async def handle_message(self, dg):
        try:
            zone = self._zones.get(
                self._zones,
                lambda e: e.id == dg.sender)

            dg = jugg.core.Datagram.from_string(dg.data)
            await zone.handle_datagram(dg)
        except KeyError:
            self._interface._window.new_zone_signal.emit(dg.sender)


class LookUpZone(pyarchy.core.IdentifiedObject, jugg.core.Node):

    def __init__(self, tab, client, id_ = None):
        jugg.core.Node.__init__(
            self,
            client._stream_reader, client._stream_writer)

        if id_:
            pyarchy.core.IdentifiedObject.__init__(self, False)
            self.id = pyarchy.core.Identity(id_)
        else:
            pyarchy.core.IdentifiedObject.__init__(self)

        self._client = client
        self._tab = tab
        self._members = []

        self._commands = {
            constants.CMD_UPDATE: self.handle_update,
        }

    async def send(self, dg):
        await self._client.send(
            jugg.core.Datagram(
                command = constants.CMD_MSG,
                sender = self._client.id,
                recipient = self.id,
                data = str(dg)))

    async def handle_update(self, dg):
        code, name = dg.data
        info = constants.UPDATE_INFO_MAP.get(code).format(name)

        if code == constants.UPDATE_JOINED:
            self._members.append(name)
        else:
            self._members.remove(name)

        if self._members:
            title = utils.oxford_comma(self._members)
        else:
            title = constants.BLANK_TAB_TITLE

        self._tab.update_title_signal.emit(title)


__all__ = [
    LookUpClient,
]
