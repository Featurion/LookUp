import base64
import json

from src.base.constants import CMD_REDY, CMD_ZONE_MSG
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase


class Zone(ZoneBase):

    def __init__(self, tab, zone_id, key, member_ids):
        ZoneBase.__init__(self, tab.getClient(), zone_id, member_ids)
        self.tab = tab
        self.__zone_key = key
        self.id2redy = {id_: False for id_ in member_ids}
        self.id2key = {id_: None for id_ in member_ids}

    def getKey(self):
        return self.__zone_key

    def sendDatagram(self, command, data):
        dg = Datagram()
        dg.setCommand(command)
        dg.setSender(self.client.getId())
        dg.setRecipient(self.getId())
        dg.setData(data)

        self.generateSecret(self.client.getKey())
        data = base64.b85encode(self.encrypt(dg.toJSON())).decode()

        dg2 = Datagram()
        dg2.setCommand(CMD_ZONE_MSG)
        dg2.setRecipient(self.getId())
        dg2.setData(data)

        self.client.sendDatagram(dg2)

    def sendRedy(self):
        self.sendDatagram(CMD_REDY, self.getKey())
        self.notify.debug('redy in zone {0}'.format(self.getId()))

    def redy(self, id_, key):
        if id_ in self.getMembers():
            self.id2redy[id_] = True
            self.id2key[id_] = key

            self.notify.debug('client {0} is redy in zone {1}'.format(id_, self.getId()))

        if all(self.id2redy.values()):
            self.tab.zone_redy_signal.emit()

    def _recv(self, datagram):
        if datagram.getCommand() == CMD_REDY:
            id_, key = json.loads(datagram.getData())
            self.redy(id_, key)
        else:
            self.notify.warning('received suspicious datagram')
