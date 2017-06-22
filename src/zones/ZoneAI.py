import base64

from src.base import constants
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase


class ZoneAI(ZoneBase):

    def __init__(self, client, zone_id, members):
        ZoneBase.__init__(self, client, zone_id, members)
        self.__id2key = {ai.getId(): None for ai in members}

        self.COMMAND_MAP.update({
            constants.CMD_REDY, self.clientRedy,
        })

    def cleanup(self):
        if hasattr(self, '__id2key') and self.__id2key:
            self.__id2key.clear()
            del self.__id2key
            self.__id2key = Non

    def getMemberIds(self):
        return [ai.getId() for ai in self.getMembers()]

    def getWorkingKey(self, id_):
        return self.__id2key.get(id_)

    def emitDatagram(self, datagram):
        for ai in self.getMembers():
            ai.sendDatagram(datagram)

        del ai
        del datagram

    def emitMessage(self, command, data=None):
        for ai in self.getMembers():
            datagram = self.buildZoneDatagram(command, ai.getId(), data)
            ai.sendDatagram(datagram)

        del ai
        del command
        del data
        del datagram

    def sendHelo(self):
        data = [
            self.getId(),
            self.getKey(),
            [ai.getId() for ai in self.getMembers()],
            [ai.getName() for ai in self.getMembers()],
        ]
        self.emitMessage(constants.CMD_HELO, data)
        self.notify.debug('sent helo'.format(self.getId()))

        del data

    def sendRedy(self):
        self.emitMessage(constants.CMD_REDY, self.__id2key)
        self.notify.debug('sent redy'.format(self.getId()))

        self.__id2key.clear()
        del self.__id2key
        self.__id2key = None

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

        del id_
        del key
        del datagram
