import asyncio
import builtins
import jugg
import pyarchy
import socket
import ssl
import time

from src import constants, settings


class ClientAI(jugg.server.ClientAI):

    def __init__(self, *args):
        super().__init__(*args)

        self.zones = pyarchy.data.ItemPool()
        self.zones.object_type = ZoneAI

        # Zone commands
        zone_commands = dict.fromkeys(constants.ZONE_CMDS, self.handle_message)
        self._commands.update(zone_commands)

    def verify_credentials(self, data):
        return super().verify_credentials(data)

    async def start(self):
        await super().start()

    async def stop(self):
        for zone in self.zones:
            zone.remove(self)

            if len(zone) > 0:
                await zone.send_update()
            else:
                server.zones.remove(zone)

        self.zones.clear()
        await super().stop()

    async def send_hello(self, zone):
        await self.send(
            jugg.core.Datagram(
                command = constants.CMD_HELLO,
                sender = zone.id,
                recipient = self.id,
                data = [zone.is_group, zone.participants]))

    async def handle_hello(self, dg):
        # Find the invitees
        clients = set()
        for name in set(dg.data):
            try:
                clients.add(server.conns.get(name=name))
            except KeyError:
                # This client is not online.
                pass

        # Find the zone
        try:
            zone = server.zones.get(id=dg.recipient)
        except KeyError:
            # The client is opening a new zone
            zone = server.new_zone(dg.recipient)
            # Add ourself to the zone
            self.zones.add(zone)
            zone.add(self)
        else:
            # We don't need to say hello to clients already in the zone
            clients -= set(zone)

            if not clients:
                # No invitees are online, so the chat becomes an empty group
                return
            elif len(zone) > 1 and not zone.is_group:
                # This private chat is becoming a group chat
                clients ^= set(zone)
                zone = server.new_zone(is_group=True)
            else:
                zone.is_group = True

        # Say hello
        for client in clients:
            await client.send_hello(zone)

    async def handle_ready(self, dg):
        # Try to find the zone
        zone = server.zones.get(id=dg.recipient)
        # Leave the zone
        self.zones.add(zone)
        zone.add(self)
        # Update the clients on who joined
        await zone.send_update()

    async def handle_leave(self, dg):
        # Try to find the zone
        zone = server.zones.get(id=dg.recipient)
        # Leave the zone
        self.zones.remove(zone)
        zone.remove(self)
        # Update the clients on who left
        await zone.send_update()

    async def handle_message(self, dg):
        try:
            # Try to find the zone
            zone = server.zones.get(id=dg.recipient)
        except KeyError:
            pass
        else:
            # Send the datagram to the zone
            dg = jugg.core.Datagram.from_string(dg.data)
            await zone.handle_datagram(dg)


class ZoneAI(pyarchy.data.ItemPool, pyarchy.core.IdentifiedObject):

    object_type = ClientAI

    def __init__(self, id_, is_group=False):
        pyarchy.data.ItemPool.__init__(self)
        pyarchy.core.IdentifiedObject.__init__(self, False)

        self.id = pyarchy.core.Identity(id_)
        self.is_group = is_group
        self._typing_status = {}

    @property
    def participants(self):
        return {client.id: client.name for client in self}

    async def handle_datagram(self, dg):
        if dg.command == constants.CMD_MSG_TYPING:
            if dg.timestamp > 0:
                # Client is still typing
                self._typing_status[dg.sender] = dg.timestamp
            else:
                # Client is no longer typing, remove if possible
                # dict.pop is used because the notification may have expired
                self._typing_status.pop(dg.sender, None)

            dg.data = self._typing_status

        await self.send(dg)

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
            conn = await super().new_connection(stream_reader, stream_writer)
            if conn:
                # Maintain the connection
                await conn.start()
                # Cleanup the client
                await conn.stop()

    def new_zone(self, id_=None, is_group=False):
        zone = ZoneAI(id_, is_group)
        self.zones.add(zone)
        return zone


__all__ = [
    ClientAI,
    ZoneAI,
    Server,
]
