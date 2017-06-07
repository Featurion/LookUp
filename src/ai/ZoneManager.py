from uuid import UUID
from src.ai.IDManager import IDManager


class ZoneManagerAI(IDManager):
    """Manage message zones"""

    __SCOPES = {
        'system': UUID('94e4b743c9764ce4b891c4124a85d793'),
        'private': UUID('b15a56a6b71e4d3291cd65f66bc0fced'),
        'group': UUID('bc41624a03ca4d2892ba6f5e886673a7'),
    } # listed by precedence

    def allocateId(self, scope_name, owner_name):
        scope = self.__SCOPES.get(scope_name)
        return self.generateId()
