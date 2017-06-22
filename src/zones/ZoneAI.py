import base64

from src.base import constants
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase


class ZoneAI(ZoneBase):

    def __init__(self, client, zone_id, members):
        ZoneBase.__init__(self, client, zone_id, members)
        self.__id2key = {ai.getId(): None for ai in members}

    def getMemberIds(self):
        return [ai.getId() for ai in self.getMembers()]

    def getWorkingKey(self, id_):
        return self.__id2key.get(id_)

    def emitDatagram(self, datagram):
        for ai in self.getMembers():
            ai.sendDatagram(datagram)

    def emitMessage(self, command, data=None):
        for ai in self.getMembers():
            datagram = self.buildZoneDatagram(command, ai.getId(), data)
            ai.sendDatagram(datagram)

    def handleReceivedDatagram(self, datagram):
        datagram = ZoneBase.handleReceivedDatagram(self, datagram)

        if not datagram:
            return

        if datagram.getCommand() == constants.CMD_REDY:
            self.clientRedy(datagram)
        else:
            self.notify.warning('received suspicious datagram')

    def sendHelo(self):
        data = [
            self.getId(),
            self.getKey(),
            [ai.getId() for ai in self.getMembers()],
            [ai.getName() for ai in self.getMembers()],
        ]
        self.emitMessage(constants.CMD_HELO, data)
        self.notify.debug('sent helo'.format(self.getId()))

    def sendRedy(self):
        self.emitMessage(constants.CMD_REDY, self.__id2key)
        self.notify.debug('sent redy'.format(self.getId()))

        self.__id2key.clear()
        del self.__id2key

    def clientRedy(self, datagram):
        id_, key = datagram.getSender(), datagram.getData()

        if id_ in self.__id2key:
            self.__id2key[id_] = key
            self.notify.debug('client {0} is redy'.format(id_, self.getId()))
        else:
            self.notify.error('ZoneError', '{0} not in zone'.format(id_))

        if all(self.__id2key.values()):
            self.setSecure(True)
            self.sendRedy()
