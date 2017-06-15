from src.base.globals import CMD_HELO, CMD_REDY
from src.base.Datagram import Datagram
from src.base.KeyHandler import KeyHandler
from src.base.Notifier import Notifier


class ZoneAI(KeyHandler):

    def __init__(self, zone_manager, id_, member_ids):
        KeyHandler.__init__(self)
        self.__id = id_
        self.__members = set(member_ids)
        self.zone_manager = zone_manager
        self.id2data = {id_: (False, None) for id_ in member_ids}

    def getId(self):
        return self.__id

    def getMembers(self):
        return self.__members

    def remove(self, id_):
        if id_ in self.getMembers():
            self.__members.remove(id_)

    def emitDatagram(self, datagram):
        datagram.setSender(self.getId())
        self.zone_manager.emitDatagramInsideZone(datagram, self.getId())

    def sendHelo(self):
        datagram = Datagram()
        datagram.setCommand(CMD_HELO)
        self.emitDatagram(datagram)

    def sendRedy(self):
        if all(data[0] for data in self.id2data.values()):
            datagram = Datagram()
            datagram.setCommand(CMD_REDY)
            datagram.setData(self.getKey())
            self.emitDatagram(datagram)

    def redy(self, id_, key):
        if id_ in self.id2data:
            self.id2data[id_] = (True, key)

        self.sendRedy()
