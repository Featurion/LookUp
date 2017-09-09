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

        self._zones = pyarchy.data.ItemPool()
        self._zones.object_type = LookUpZoneAI

        self._commands[constants.CMD_HELLO] = self.handle_hello
        self._commands[constants.CMD_READY] = self.handle_ready
        self._commands[constants.CMD_MSG] = self.handle_message

    def verify_credentials(self, data):
        return super().verify_credentials(data)

    async def start(self):
        await super().start()

        for zone in self._zones:
            zone.remove(self)
            await zone.send_update()

    async def send_hello(self, zone):
        await self.send(
            jugg.core.Datagram(
                command = constants.CMD_HELLO,
                sender = zone.id,
                recipient = self.id,
                data = zone.participants))

    async def handle_hello(self, dg):
        try:
            zone = self._server._zones.get(
                self._server._zones,
                lambda e: e.id == dg.recipient)
        except KeyError:
            zone = LookUpZoneAI(dg.recipient)
            self._server._zones.add(zone)
            self._zones.add(zone)
            zone.add(self)

        for name in dg.data:
            try:
                client = self._server.clients.get(
                    self._server.clients,
                    lambda e: e.name == name)
                await client.send_hello(zone)
            except KeyError:
                pass

    async def handle_ready(self, dg):
        zone = self._server._zones.get(
            self._server._zones,
            lambda e: e.id == dg.recipient)

        self._zones.add(zone)
        zone.add(self)

        await zone.send_update()

    async def handle_message(self, dg):
        try:
            zone = self._server._zones.get(
                self._server._zones,
                lambda e: e.id == dg.recipient)

            dg = jugg.core.Datagram.from_string(dg.data)
            await zone.send(dg)
        except KeyError:
            pass


class LookUpZoneAI(pyarchy.data.ItemPool, pyarchy.core.IdentifiedObject):

    object_type = LookUpClientAI

    def __init__(self, id_):
        pyarchy.data.ItemPool.__init__(self)
        pyarchy.core.IdentifiedObject.__init__(self, False)

        self.id = pyarchy.core.Identity(id_)

    @property
    def participants(self):
        return {client.name: client.id for client in self}

    async def send(self, dg):
        for client in self:
            await client.send(
                jugg.core.Datagram(
                    command = constants.CMD_MSG,
                    sender = self.id,
                    recipient = client.id,
                    data = str(dg)))

    async def send_update(self):
        await self.send(
            jugg.core.Datagram(
                command = constants.CMD_UPDATE,
                sender = self.id,
                recipient = self.id,
                data = self.participants))


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

        self._zones = pyarchy.data.ItemPool()
        self._zones.object_type = LookUpZoneAI

    async def new_connection(self, stream_reader, stream_writer):
        if stream_writer.transport._sock.getpeername() in self._banned:
            stream_writer.close()
        else:
            try:
                await super().new_connection(
                    stream_reader, stream_writer,
                    server = self)
            except ConnectionResetError:
                pass


__all__ = [
    LookUpClientAI,
    LookUpServer,
]
