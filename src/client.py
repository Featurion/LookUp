import asyncio
import jugg
import pyarchy
import socket
import ssl

from src import constants


class Client(jugg.client.Client):

    def __init__(self,
                 host: str, port: int,
                 certificate: str = None,
                 *args, **kwargs):
        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if certificate:
            socket_ = ssl.wrap_socket(
                socket_,
                ca_certs = certificate,
                cert_reqs = ssl.CERT_REQUIRED,
                ssl_version = ssl.PROTOCOL_TLSv1_2,
                ciphers = 'ECDHE-ECDSA-AES256-GCM-SHA384')

        socket_.connect((host, port))

        super().__init__(socket_=socket_, *args, **kwargs)

        self._username = None

        self._zones = pyarchy.data.ItemPool()
        self._zones.object_type = Zone

        # Zone commands
        zone_commands = dict.fromkeys(constants.ZONE_CMDS, self.handle_message)
        self._commands.update(zone_commands)

    async def stop(self):
        await super().stop()
        interface.stop()

    def new_zone(self, tab, id_=None):
        tab._zone = Zone(tab, id_)
        self._zones.add(zone)
        return tab._zone

    def synchronous_send(self, **kwargs):
        asyncio.new_event_loop().run_until_complete(
            self.send_datagram(**kwargs))

    async def send_datagram(self, **kwargs):
        kwargs.pop('sender', None)
        dg = jugg.core.Datagram(sender=self.id, **kwargs)

        # Send zone commands to the proper zone
        if dg.command >= constants.CMD_MSG:
            for zone in self._zones:
                if zone.id == dg.recipient:
                    await zone.send(dg)
        else:
            await self.send(dg)

    async def handle_handshake(self, dg):
        await super().handle_handshake(dg)
        interface.connected_signal.emit()

    async def handle_authenticate(self, dg):
        await super().handle_authenticate(dg)
        interface.login_signal.emit()

    async def do_error(self, errno):
        interface.error_signal.emit(errno)

    async def handle_hello(self, dg):
        interface.hello_signal.emit(dg.sender, *dg.data)

    async def handle_message(self, dg):
        zone = self._zones.get(id=dg.sender)

        dg = jugg.core.Datagram.from_string(dg.data)
        await zone.handle_datagram(dg)


class Zone(jugg.core.Node):

    def __init__(self, tab, id_):
        jugg.core.Node.__init__(
            self,
            conn._stream_reader, conn._stream_writer)

        self.id = pyarchy.core.Identity(id_)

        self._tab = tab
        self.__participants = {conn.id: conn.name}

    @property
    def participants(self):
        return dict(**self.__participants)

    @participants.setter
    def participants(self, participants):
        self.__participants = participants
        self.__participants.update({conn.id: conn.name})

    async def send(self, dg):
        await conn.send(
            jugg.core.Datagram(
                command = constants.CMD_MSG,
                sender = conn.id,
                recipient = self.id,
                data = str(dg)))

    async def do_message(self, ts, sender, msg):
        self._tab.add_message_signal.emit(ts, sender, msg)

    async def handle_message(self, dg):
        await self.do_message(
            dg.timestamp,
            self.participants[dg.sender],
            dg.data)

    async def handle_update(self, dg):
        for id_, name in self.participants.items():
            if id_ not in dg.data:
                await self.do_message(
                    dg.timestamp,
                    'server',
                    name + ' left')

        for id_, name in dg.data.items():
            if id_ not in self.participants:
                await self.do_message(
                    dg.timestamp,
                    'server',
                    name + ' joined')

        self.participants = dg.data
        self._tab.update_title_signal.emit()

    async def handle_message_delete(self, dg):
        self._tab.del_message_signal.emit(
            dg.timestamp,
            self.participants[dg.sender])

    async def handle_message_edit(self, dg):
        await self.do_message(dg.timestamp, *dg.data)

    async def handle_message_typing(self, dg):
        self._tab.typing_message_signal.emit(dg.data)


__all__ = [
    Client,
    Zone,
]
