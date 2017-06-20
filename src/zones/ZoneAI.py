import base64
import json

from src.base import constants
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase


class ZoneAI(ZoneBase):

    def __init__(self, client, zone_id, members):
        ZoneBase.__init__(self, client, zone_id, members)
        self.id2key = {ai.getId(): None for ai in members}

    def getMemberIds(self):
        return [ai.getId() for ai in self.getMembers()]

    def getWorkingKey(self, id_):
        return self.id2key.get(id_)

    def emitDatagram(self, datagram):
        for ai in self.getMembers():
            ai.sendDatagram(datagram)

    def emitMessage(self, command, data=None):
        for ai in self.getMembers():
            datagram = self.buildZoneDatagram(command, ai.getId(), data)
            ai.sendDatagram(datagram)

    def handleReceivedDatagram(self, datagram):
        datagram = self.decrypt(datagram)

        if datagram.getCommand() == constants.CMD_REDY:
            self.clientRedy(datagram)
        else:
            self.notify.warning('received suspicious datagram')

    def sendHelo(self):
        data = json.dumps([
            self.getId(),
            self.getKey(),
            [ai.getId() for ai in self.getMembers()],
            [ai.getName() for ai in self.getMembers()],
        ])
        self.emitMessage(constants.CMD_HELO, data)

        self.notify.debug('sent helo in zone {0}'.format(self.getId()))

    def sendRedy(self):
        self.emitMessage(constants.CMD_REDY, json.dumps(self.id2key))
        self.id2key.clear()

    def clientRedy(self, datagram):
        id_, key = datagram.getSender(), datagram.getData()

        if id_ in self.id2key:
            self.id2key[id_] = key
            self.notify.debug('client {0} redy in zone {1}'.format(id_, self.getId()))
        else:
            self.notify.error('ZoneError', '{0} not in zone'.format(id_))

        if all(self.id2key.values()):
            self.is_secure = True
            self.sendRedy()
            self.notify.debug('zone {0} is redy'.format(self.getId()))
