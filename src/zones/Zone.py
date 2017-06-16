import json

from src.base.globals import CMD_REDY
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase


class Zone(ZoneBase):

    def __init__(self, tab, zone_id, member_ids):
        ZoneBase.__init__(self, tab.getClient(), zone_id, member_ids)
        self.tab = tab
        self.id2redy = {id_: False for id_ in member_ids}
        self.id2key = {id_: None for id_ in member_ids}

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
