from uuid import UUID

from src.base.UniqueIDManager import UniqueIDManager
from src.zones.ZoneAI import ZoneAI


class ZoneManager(UniqueIDManager):
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

    def emitMessage(self, message):
        """Send message to all clients"""
        return NotImplemented

    def emitMessageInsideZone(self, message, zone):
        """Send message to all clients with interest in zone"""
        return NotImplemented

    def emitMessageOutsideZone(self, message, zone):
        """Send message to all clients without interest in zone"""
        return NotImplemented

    def getZoneById(self, id_):
        zone = self.id2owner.get(id_)
        if zone:
            return zone
        else:
            self.notify.debug('Zone with id {0} does not exist!'.format(id_))
            return None

    def addZone(self, members):
        if len(members) > 1:
            mode = self.SCOPES['group']
        else:
            mode = self.SCOPES['private']

        clients = [self.client_manager.getClientByName(n) for n in members]
        member_ids = [c.getId() for c in clients]

        scope, seed, id_ = self.generateId(mode, ','.join(members))
        ai = ZoneAI(self, id_, member_ids)
        self.allocateId(scope, seed, id_, ai)
        return ai

    def removeZone(self, ai):
        self.deallocateId(ai.getId(), ai.getMode())
