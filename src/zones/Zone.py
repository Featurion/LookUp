import base64

from src.base import constants
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase


class Zone(ZoneBase):

    def __init__(self, tab, zone_id, key, member_ids):
        ZoneBase.__init__(self, tab.getClient(), zone_id, member_ids)
        self.tab = tab
        self.id2key = {id_: None for id_ in member_ids}
        self.__alt_key = key

        del id_
        del tab
        del zone_id
        del key
        del member_ids

    def cleanup(self):
        ZoneBase.cleanup(self)
        self.__alt_key = None
        if self.tab:
            self.tab.cleanup()
            del self.tab
            self.tab = None
        if self.id2key:
            self.id2key.clear()
            del self.id2key
            self.id2key = None

    def getWorkingKey(self, id_):
        del id_
        return self.__alt_key

    def handleReceivedDatagram(self, datagram):
        datagram = ZoneBase.handleReceivedDatagram(self, datagram)

        if not datagram:
            return

        if datagram.getCommand() == constants.CMD_REDY:
            self.zoneRedy(datagram)
        else:
            self.notify.warning('received suspicious datagram')

        del datagram

    def sendRedy(self):
        datagram = self.buildZoneDatagram(constants.CMD_REDY,
                                          self.getId(),
                                          self.getKey())
        self.sendDatagram(datagram)
        self.setSecure(True)
        self.notify.debug('sent redy'.format(self.getId()))

        del datagram

    def zoneRedy(self, datagram):
        self.id2key = datagram.getData()
        self.tab.zone_redy_signal.emit()
        del datagram
