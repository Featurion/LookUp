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

    def emitDatagram(self, datagram):
        """Send message to all clients"""
        for ai in self.server.cm.getClients():
            datagram.setRecipient(ai.getId())
            ai.sendDatagram(datagram)

    def emitDatagramInsideZone(self, datagram, zone_id):
        """Send message to all clients with interest in zone"""
        zone = self.getZoneById(zone_id)
        if zone:
            for ai in zone.getMembers():
                datagram.setRecipient(id_)
                ai.sendDatagram(datagram)

    def emitDatagramOutsideZone(self, datagram, zone_id):
        """Send message to all clients without interest in zone"""
        zone = self.getZoneById(zone_id)
        if zone:
            for ai in self.server.cm.getClients():
                if ai.getId() not in zone.getMembers():
                    datagram.setRecipient(ai.getId())
                    ai.sendDatagram(datagram)

    def getZoneIds(self):
        return [ai.getId() for ai in self.id2owner.values()]

    def getZoneById(self, id_: int):
        zone = self.id2owner.get(id_)
        if zone:
            return zone
        else:
            self.notify.debug('zone {0} does not exist'.format(id_))
            return None

    def addZone(self, client, members, group):
        if group:
            mode = 'group'
        else:
            mode = 'private'

        if not group and members > 2:
            self.notify.error('ZoneError', 'private chats cannot have over 2 members')
            return

        member_ais = [self.server.cm.getClientByName(n) for n in members]
        for member in member_ais:
            if member == None:
                return

        seed = ','.join(members)
        zone_id = self.generateId(mode, seed)
        ai = ZoneAI(client, zone_id, member_ais)
        self.allocateId(mode, seed, zone_id, ai)

        self.notify.debug('created zone {0}'.format(ai.getId()))

        return ai

    def removeZone(self, ai):
        self.deallocateId(ai.getId(), ai.getMode())
