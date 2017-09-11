import asyncio
import builtins
import jugg
import pyarchy
import socket
import ssl
import time

from src import constants, settings


class ClientAI(jugg.server.ClientAI):

    def __init__(self, *args, server = None):
        super().__init__(*args)

        self.zones = pyarchy.data.ItemPool()
        self.zones.object_type = ZoneAI

        self._commands[constants.CMD_HELLO] = self.handle_hello
        self._commands[constants.CMD_READY] = self.handle_ready
        self._commands[constants.CMD_LEAVE] = self.handle_leave
        self._commands[constants.CMD_MSG] = self.handle_message

    def verify_credentials(self, data):
        return super().verify_credentials(data)

    async def start(self):
        await super().start()

        for zone in self.zones:
            zone.remove(self)

            if len(zone) > 0:
                await zone.send_update()
            else:
                server.zones.remove(zone)

        self.zones.clear()

    async def send_hello(self, zone):
        await self.send(
            jugg.core.Datagram(
                command = constants.CMD_HELLO,
                sender = zone.id,
                recipient = self.id,
                data = zone.participants))

    async def handle_hello(self, dg):
        try:
            zone = server.zones.get(id = dg.recipient)
        except KeyError:
            zone = ZoneAI(dg.recipient)
            server.zones.add(zone)
            self.zones.add(zone)
            zone.add(self)

        # If we sent the CMD_HELLO, we don't need it back.
        participants = set(dg.data)
        participants.discard(self.name)

        for name in participants:
            try:
                client = server.clients.get(name = name)

                if client not in zone:
                    await client.send_hello(zone)
                else:
                    # This client is already in the zone, so we don't need
                    # to send out another invite.
                    pass
            except KeyError:
                pass

    async def handle_ready(self, dg):
        zone = server.zones.get(id = dg.recipient)

        self.zones.add(zone)
        zone.add(self)

        await zone.send_update()

    async def handle_leave(self, dg):
        zone = server.zones.get(id = dg.recipient)

        self.zones.remove(zone)
        zone.remove(self)

        await zone.send_update()

    async def handle_message(self, dg):
        try:
            zone = server.zones.get(id = dg.recipient)

            dg = jugg.core.Datagram.from_string(dg.data)
            await zone.send(dg)
        except KeyError:
            pass


class ZoneAI(pyarchy.data.ItemPool, pyarchy.core.IdentifiedObject):

    object_type = ClientAI

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
                data = [time.time(), self.participants]))


class Server(jugg.server.Server, metaclass = pyarchy.meta.MetaSingleton):

    client_handler = ClientAI

    def __new__(cls):
        builtins.server = super().__new__(cls)
        return builtins.server

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

        self.banned = pyarchy.data.ItemPool()
        self.banned.object_type = tuple

        self.zones = pyarchy.data.ItemPool()
        self.zones.object_type = ZoneAI

    async def new_connection(self, stream_reader, stream_writer):
        if stream_writer.transport._sock.getpeername() in self.banned:
            stream_writer.close()
        else:
            await super().new_connection(
                stream_reader, stream_writer,
                server = self)


__all__ = [
    ClientAI,
    ZoneAI,
    Server,
]
