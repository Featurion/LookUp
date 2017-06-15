from src.base.Notifier import Notifier


class ZoneManager(Notifier):

    def __init__(self):
        Notifier.__init__(self)
        self.__id2zone = {}

    def addZone(self, zone):
        self.__id2zone[zone.getId()] = zone

    def removeZone(self, zone):
        del self.__id2zone[zone.getId()]

    def getZoneById(self, id_):
        return self.__id2zone.get(id_)
