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

    async def send_hello(self, zone, participants):
        await self.send(
            jugg.core.Datagram(
                command = constants.CMD_HELLO,
                sender = zone.id,
                recipient = self.id,
                data = [zone.is_group, participants]))

    async def handle_hello(self, dg):
        names = set(dg.data)

        # If we sent the CMD_HELLO, we don't need it back
        try:
            zone = server.zones.get(id=dg.recipient)
            names.update(client.name for client in zone)

            if zone.is_group:
                # The zone exists as a group
                names.discard(self.name)
            else:
                # The zone exists, but is becoming a group
                zone = server.new_zone(is_group=True)
        except KeyError:
            # The client is opening a new zone
            zone = server.new_zone(dg.recipient)
            names.add(self.name)

        clients = set()
        for name in names:
            try:
                client = server.clients.get(name=name)
                clients.add(client)
            except KeyError:
                # This client is not online.
                pass

        if clients == {self}:
            # If no one else is online, the chat becomes an empty group.
            zone.is_group = True
            zone.add(self)
            self.zones.add(zone)
            return

        for client in clients:
            if client not in zone:
                if zone.is_group:
                    # Send a HELLO for the group chat
                    await client.send_hello(zone, zone.participants)
                else:
                    # Send a HELLO for the new private chat
                    await client.send_hello(zone, [self.name])
            else:
                # This client is already in the zone, so we don't need
                # to send out another invite.
                pass

    async def handle_ready(self, dg):
        zone = server.zones.get(id=dg.recipient)

        self.zones.add(zone)
        zone.add(self)

        await zone.send_update()

    async def handle_leave(self, dg):
        zone = server.zones.get(id=dg.recipient)

        self.zones.remove(zone)
        zone.remove(self)

        await zone.send_update()

    async def handle_message(self, dg):
        try:
            zone = server.zones.get(id=dg.recipient)

            dg = jugg.core.Datagram.from_string(dg.data)
            await zone.send(dg)
        except KeyError:
            pass


class ZoneAI(pyarchy.data.ItemPool, pyarchy.core.IdentifiedObject):

    object_type = ClientAI

    def __init__(self, id_, is_group=False):
        pyarchy.data.ItemPool.__init__(self)
        pyarchy.core.IdentifiedObject.__init__(self, False)

        self.id = pyarchy.core.Identity(id_)
        self.is_group = is_group

    @property
    def participants(self):
        return [(client.name, client.id) for client in self]

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

    def new_zone(self, id_=None, is_group=False):
        zone = ZoneAI(id_, is_group)
        self.zones.add(zone)
        return zone


__all__ = [
    ClientAI,
    ZoneAI,
    Server,
]
