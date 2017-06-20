import base64
import json

from src.base import constants
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase


class Zone(ZoneBase):

    def __init__(self, tab, zone_id, key, member_ids):
        ZoneBase.__init__(self, tab.getClient(), zone_id, member_ids)
        self.tab = tab
        self.id2key = {id_: None for id_ in member_ids}
        self.__alt_key = key

    def getWorkingKey(self, id_):
        return self.__alt_key

    def handleReceivedDatagram(self, datagram):
        datagram = self.decrypt(datagram)

        if datagram.getCommand() == constants.CMD_REDY:
            self.zoneRedy(datagram)
        else:
            self.notify.warning('received suspicious datagram')

    def sendRedy(self):
        datagram = self.buildZoneDatagram(constants.CMD_REDY,
                                          self.getId(),
                                          self.getKey())
        self.sendDatagram(datagram)

        self.is_secure = True

        self.notify.debug('redy in zone {0}'.format(self.getId()))

    def zoneRedy(self, datagram):
        self.id2key = json.loads(datagram.getData())
        self.tab.zone_redy_signal.emit()
