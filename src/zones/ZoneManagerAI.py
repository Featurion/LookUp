import os
from uuid import UUID

from src.base.Datagram import Datagram
from src.base.UniqueIDManager import UniqueIDManager
from src.zones.ZoneAI import ZoneAI

class ZoneManagerAI(UniqueIDManager):
    """Manage chat message zones"""

    SCOPES = {
        'system': UUID('94e4b743c9764ce4b891c4124a85d793'),
        'private': UUID('b15a56a6b71e4d3291cd65f66bc0fced'),
        'group': UUID('bc41624a03ca4d2892ba6f5e886673a7'),
    } # listed by precedence
    SCOPES.update(UniqueIDManager.SCOPES)

    def __init__(self, server):
        UniqueIDManager.__init__(self)
        self.server = server
        del server

    def emitDatagram(self, datagram):
        """Send message to all clients"""
        for ai in self.server.cm.getClients():
            datagram.setRecipient(ai.getId())
            ai.sendDatagram(datagram)

        del ai
        del datagram

    def emitDatagramInsideZone(self, datagram, zone_id):
        """Send message to all clients with interest in zone"""
        zone = self.getZoneById(zone_id)
        if zone:
            for ai in zone.getMembers():
                datagram.setRecipient(id_)
                ai.sendDatagram(datagram)

        del zone
        del ai
        del zone_id
        del datagram

    def emitDatagramOutsideZone(self, datagram, zone_id):
        """Send message to all clients without interest in zone"""
        zone = self.getZoneById(zone_id)
        if zone:
            for ai in self.server.cm.getClients():
                if ai.getId() not in zone.getMembers():
                    datagram.setRecipient(ai.getId())
                    ai.sendDatagram(datagram)

        del zone
        del ai
        del zone_id
        del datagram

    def getZoneIds(self):
        return self.id2owner.keys()

    def getZoneById(self, id_: str):
        return self.id2owner.get(id_)

    def addZone(self, client, member_names, is_group):
        if is_group:
            mode = 'group'
        else:
            mode = 'private'

        if len(member_names) > 2 and not is_group:
            self.notify.error('ZoneError',
                              'private chats cannot have over 2 members')
            return

        member_ais = [self.server.cm.getClientByName(n) for n in member_names]
        for member in member_ais:
            if member is None:
                return

        if mode == 'private':
            seed = ','.join(sorted(member_names))
        else:
            seed = ''.join(chr(c) for c in os.urandom(64))

        zone_id = self.generateId(mode, seed).bytes.hex()
        ai = ZoneAI(client, zone_id, member_ais, is_group)
        self.allocateId(mode, seed, zone_id, ai)
        self.notify.debug('created zone {0}'.format(ai.getId()))

        del client
        del member_names
        del is_group
        del member_ais
        del member
        del seed
        del zone_id

        return ai

    def removeZone(self, ai):
        self.deallocateId(ai.getId(), ai.getMode())

        ai.cleanup()
        del ai
