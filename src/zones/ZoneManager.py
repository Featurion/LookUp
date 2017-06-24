from src.base.Notifier import Notifier


class ZoneManager(Notifier):

    def __init__(self):
        Notifier.__init__(self)
        self.__members2tab = {}
        self.__zones = []

    def cleanup(self):
        if self.__members2tab:
            self.__members2tab.clear()
            del self.__members2tab
            del _m
            del _t
            self.__members2tab = None
        if self.__zones:
            for _z in self.__zones:
                _z.cleanup()
            del _z
            del self.__zones[:]
            del self.__zones
            self.__zones = None

    def addZone(self, zone):
        self.__zones.append(zone)
        del zone

    def removeZone(self, zone):
        self.__zones.remove(zone)
        del zone

    def addTab(self, tab, members: tuple):
        self.__members2tab.setdefault(members, tab)

        del tab
        del members

    def getZones(self):
        return self.__zones

    def getZoneIds(self):
        return [z.getId() for z in self.__zones]

    def getZoneById(self, id_):
        for zone in self.getZones():
            if zone.getId() == id_:
                return zone

        self.notify.warning('zone {0} does not exist'.format(id_))

        del id_

    def getTabByMembers(self, members: tuple):
        return self.__members2tab.get(members)
