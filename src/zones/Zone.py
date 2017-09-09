import jugg
import pyarchy

from src.base import constants
from src.gui import utils

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
            constants.CMD_UPDATE: self.handleUpdate,
        }

    async def send(self, dg):
        await self._client.send(
            jugg.core.Datagram(
                command = constants.CMD_MSG,
                sender = self._client.id,
                recipient = self.id,
                data = str(dg)))

    async def handleUpdate(self, dg):
        code, name = dg.data
        info = constants.UPDATE_INFO_MAP.get(code).format(name)

        if code == constants.UPDATE_JOINED:
            # User joined
            self._members.append(name)
        else:
            try:
                # User left
                self._members.remove(name)
            except ValueError:
                # User rejected invitation or is offline
                pass

        if self._members:
            title = utils.oxford_comma(self._members)
        else:
            title = constants.BLANK_TAB_TITLE

        self._tab.update_title_signal.emit(title)
