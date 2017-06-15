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

    def __init__(self, client_manager):
        UniqueIDManager.__init__(self)
        self.client_manager = client_manager

    def emitDatagram(self, datagram):
        """Send message to all clients"""
        for ai in self.client_manager.getClients():
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
            for ai in self.client_manager.getClients():
                if ai.getId() not in zone.getMembers():
                    datagram.setRecipient(ai.getId())
                    ai.sendDatagram(datagram)

    def getZoneById(self, id_):
        zone = self.id2owner.get(id_)
        if zone:
            return zone
        else:
            self.notify.debug('zone with id {0} does not exist!'.format(id_))
            return None

    def addZone(self, members):
        if len(members) > 1:
            mode = self.SCOPES['group']
        else:
            mode = self.SCOPES['private']

        member_ais = [self.client_manager.getClientByName(n) for n in members]

        scope, seed, id_ = self.generateId(mode, ','.join(members))
        ai = ZoneAI(id_, member_ais)
        self.allocateId(scope, seed, id_, ai)

        self.notify.debug('created zone {0}'.format(ai.getId()))

        return ai

    def removeZone(self, ai):
        self.deallocateId(ai.getId(), ai.getMode())
