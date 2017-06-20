from src.base.Notifier import Notifier


class ZoneManager(Notifier):

    def __init__(self):
        Notifier.__init__(self)
        self.__members2tab = {}
        self.__zones = []

    def addZone(self, zone):
        self.__zones.append(zone)

    def removeZone(self, zone):
        self.__zones.remove(zone)

    def addTab(self, tab, members: tuple):
        self.__members2tab.setdefault(members, tab)

    def getZones(self):
        return self.__zones

    def getZoneById(self, id_, search=False):
        for zone in self.getZones():
            if zone.getId() == id_:
                return zone

        if search is True:
            self.notify.debug('zone with id {0} does not exist'.format(id_))

    def getTabByMembers(self, members: tuple):
        return self.__members2tab.get(members)
