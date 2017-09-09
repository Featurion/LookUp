import jugg
import pyarchy

from src.base import constants

from src.zones.ZoneAI import LookUpZoneAI

class LookUpClientAI(jugg.server.ClientAI):

    def __init__(self, *args, server = None):
        super().__init__(*args)

        self._server = server

        self._zones = pyarchy.data.ItemPool()
        self._zones.object_type = LookUpZoneAI

        self._commands[constants.CMD_HELLO] = self.handleHello
        self._commands[constants.CMD_READY] = self.handleReady
        self._commands[constants.CMD_REJECT] = self.handleReject
        self._commands[constants.CMD_MSG] = self.handleMessage

    def verify_credentials(self, data):
        return super().verify_credentials(data)

    async def start(self):
        await super().start()

        # Cleanup
        for zone in self._zones:
            await zone.send_update(constants.UPDATE_LEFT, self.name)

    async def sendHello(self, zone):
        await self.send(
            jugg.core.Datagram(
                command = constants.CMD_HELLO,
                sender = zone.id,
                recipient = self.id,
                data = [client.name for client in zone]))

    async def handleHello(self, dg):
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
                await zone.send_update(constants.UPDATE_UNAVAILABLE, name)

    async def handleReady(self, dg):
        zone = self._server._zones.get(
            self._server._zones,
            lambda e: e.id == dg.recipient)

        self._zones.add(zone)
        zone.add(self)

        await zone.send_update(constants.UPDATE_JOINED, self.name)

    async def handleReject(self, dg):
        zone = self._server._zones.get(
            self._server._zones,
            lambda e: e.id == dg.recipient)

        await zone.send_update(constants.UPDATE_REJECTED, self.name)

    async def handleMessage(self, dg):
        try:
            zone = self._server._zones.get(
                self._server._zones,
                lambda e: e.id == dg.recipient)

            dg = jugg.core.Datagram.from_string(dg.data)
            await zone.handle_datagram(dg)
        except KeyError:
            pass
