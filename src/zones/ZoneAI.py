import json

from src.base.globals import CMD_HELO, CMD_REDY
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase


class ZoneAI(ZoneBase):

    def __init__(self, id_, members):
        ZoneBase.__init__(self, id_, members)
        self.id2redy = {ai.getId(): False for ai in members}

    def getMemberIds(self):
        return [ai.getId() for ai in self.getMembers()]

    def emitDatagram(self, datagram):
        for ai in self.getMembers():
            dg = Datagram()
            dg.setCommand(datagram.getCommand())
            dg.setSender(self.getId())
            dg.setRecipient(ai.getId())
            dg.setData(datagram.getData())
            dg.setHMAC(datagram.getHMAC())
            ai.sendDatagram(dg)

    def sendHelo(self):
        datagram = Datagram()
        datagram.setCommand(CMD_HELO)
        datagram.setData(json.dumps([
            [ai.getId() for ai in self.getMembers()],
            [ai.getName() for ai in self.getMembers()],
        ]))
        self.emitDatagram(datagram)

    def relayRedy(self, id_, key):
        datagram = Datagram()
        datagram.setCommand(CMD_REDY)
        datagram.setData(json.dumps([id_, key]))
        self.emitDatagram(datagram)

    def redy(self, id_, key):
        if id_ in self.id2redy:
            self.id2redy[id_] = True

        self.relayRedy(id_, key)

        if all(self.id2redy.values()):
            self.notify.debug('zone {0} is redy'.format(self.getId()))
