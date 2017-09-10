import asyncio
import jugg
import pyarchy
import socket
import ssl

from src import constants


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

    async def stop(self):
        await super().stop()
        self._interface.stop()

    def synchronous_send(self, **kwargs):
        asyncio.new_event_loop().run_until_complete(
            self.send_datagram(**kwargs))

    async def send_datagram(self, **kwargs):
        kwargs.pop('sender', None)
        dg = jugg.core.Datagram(sender = self.id, **kwargs)

        # Commands > CMD_MSG go to their zone
        if dg.command > 5:
            for zone in self._zones:
                if zone.id == dg.recipient:
                    await zone.send(dg)
        else:
            await self.send(dg)

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
        zone = self._zones.get(
            self._zones,
            lambda e: e.id == dg.sender)

        dg = jugg.core.Datagram.from_string(dg.data)
        await zone.handle_datagram(dg)


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
        self._participants = {client.name: client.id}

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
        # TODO: improve this logic
        for name in self._participants:
            if name not in dg.data:
                # print(name, 'left')
                pass

        for name in dg.data:
            if name not in self._participants:
                # print(name, 'joined')
                pass

        self._participants = dg.data
        self._tab.update_title_signal.emit()


__all__ = [
    LookUpClient,
]
