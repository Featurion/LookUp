import jugg
import pyarchy

from src.base import constants

class LookUpZoneAI(
    pyarchy.data.ItemPool,
    pyarchy.core.IdentifiedObject,
    jugg.core.Node):

    def __init__(self, id_):
        pyarchy.data.ItemPool.__init__(self)
        pyarchy.core.IdentifiedObject.__init__(self, False)

        self.id = pyarchy.core.Identity(id_)

        self._commands = {
            constants.CMD_READY: self.send,
        }

    async def send(self, dg):
        for client in self:
            await client.send(
                jugg.core.Datagram(
                    command = constants.CMD_MSG,
                    sender = self.id,
                    recipient = client.id,
                    data = str(dg)))

    async def sendUpdate(self, code, name):
        await self.send(
            jugg.core.Datagram(
                command = constants.CMD_UPDATE,
                sender = self.id,
                recipient = self.id,
                data = (code, name)))
