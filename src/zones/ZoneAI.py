import base64
import json

from src.base.constants import CMD_HELO, CMD_REDY, CMD_ZONE_MSG
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase


class ZoneAI(ZoneBase):

    def __init__(self, client, zone_id, members):
        ZoneBase.__init__(self, client, zone_id, members)
        self.id2redy = {ai.getId(): False for ai in members}

    def getMemberIds(self):
        return [ai.getId() for ai in self.getMembers()]

    def emitDatagram(self, command, data):
        for ai in self.getMembers():
            dg = Datagram()
            dg.setCommand(command)
            dg.setSender(self.getId())
            dg.setRecipient(ai.getId())
            dg.setData(data)

            self.generateSecret(self.getKey())
            data = base64.b85encode(self.encrypt(dg.toJSON())).decode()

            dg2 = Datagram()
            dg2.setCommand(CMD_ZONE_MSG)
            dg2.setRecipient(ai.getId())
            dg2.setData(data)

            ai.sendDatagram(dg2)

        self.notify.debug('sent helo in zone {0}'.format(self.getId()))

    def decryptDatagram(self, datagram):
        self.generateSecret(self.getKey()) # This needs to be the member's public key, not its own public key
        data = self.decrypt(base64.b85decode(datagram.getData())) # TODO: fix!
        return data

    def sendHelo(self):
        data = json.dumps([
            str(self.getId()),
            str(self.getKey()),
            [ai.getId() for ai in self.getMembers()],
            [ai.getName() for ai in self.getMembers()],
        ])

        for ai in self.getMembers():
            datagram = Datagram()
            datagram.setCommand(CMD_HELO)
            datagram.setRecipient(ai.getId())
            datagram.setData(data)

            ai.sendDatagram(datagram)

        self.notify.debug('sent helo in zone {0}'.format(self.getId()))

    def redy(self, id_, key):
        if id_ in self.id2redy:
            self.id2redy.setdefault(id_, True)
            self.notify.debug('client {0} redy in zone {1}'.format(id_, self.getId()))
        else:
            self.notify.error('ZoneError', 'id not in zone')

        self.emitDatagram(CMD_REDY, json.dumps([id_, key]))

        if all(self.id2redy.values()):
            self.notify.debug('zone {0} is redy'.format(self.getId()))

    def _recv(self, datagram):
        datagram = self.decryptDatagram(datagram)

        if datagram.getCommand() == CMD_REDY:
            self.redy(datagram.getData())
        else:
            self.notify.warning('received suspicious datagram')

        return datagram
