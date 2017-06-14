from src.base.globals import CMD_HELO, CMD_REDY
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase


class ZoneAI(ZoneBase):

    def __init__(self, zone_manager, id_, member_ids):
        ZoneBase.__init__(self, id_, member_ids)
        self.zone_manager = zone_manager
        self.id2redy = {id_: False for id_ in member_ids}

    def emitDatagram(self, datagram):
        datagram.setSender(self.getId())
        self.zone_manager.emitDatagramInsideZone(datagram, self.getId())

    def sendHelo(self):
        datagram = Datagram()
        datagram.setCommand(CMD_HELO)
        self.emitDatagram(datagram)

    def sendRedy(self):
        if all(self.id2redy.values()):
            datagram = Datagram()
            datagram.setCommand(CMD_REDY)
            self.emitDatagram(datagram)

    def redy(self, id_):
        if id_ in self.id2redy:
            self.id2redy[id_] = True

        self.sendRedy()
