from src.zones.ZoneBase import ZoneBase


class Zone(ZoneBase):

    def __init__(self, tab, id_, member_ids):
        ZoneBase.__init__(self, id_, member_ids)
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
