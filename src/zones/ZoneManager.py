from src.base.Notifier import Notifier


class ZoneManager(Notifier):

    def __init__(self):
        Notifier.__init__(self)
        self.__zones = []

    def addZone(self, zone):
        self.__zones.append(zone)

    def removeZone(self, zone):
        self.__zones.remove(zone)

    def getZones(self):
        return self.__zones

    def getZoneById(self, id_):
        for zone in self.getZones():
            if zone.getId() == id_:
                return zone

        self.notify.debug('zone with id {0} does not exist!'.format(id_))
