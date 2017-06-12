from uuid import UUID

from src.base.UniqueIDManager import UniqueIDManager
from src.userbase.ClientAI import ClientAI


class ClientManager(UniqueIDManager):
    """Manage connected clients"""

    SCOPES = {
        'temp': UUID('a5f7a870e9254cb39b341ab726df7952'),
        'lite': UUID('e8e4d5b1749a4ff19e0d8dab65bf4ff0'),
        'paid': UUID('e6b429c7ccc8401f8c1d99e9fe3451cd'),
    } # listed by precedence
    SCOPES.update(UniqueIDManager.SCOPES)

    def __init__(self, server):
        UniqueIDManager.__init__(self)
        self.__server = server
        self.name2owner = {}

    def acceptClient(self):
        """Accept a connecting client"""
        # log: 'waiting for socket connection'
        socket_, (address, port) = self.__server.accept()
        scope, seed, id_ = self.generateId()
        ai = ClientAI(self,
                      self.__server.zone_manager,
                      address, port, socket_, id_)
        self.allocateId(scope, seed, id_, ai)
        # log: 'client {id} connected'
        return ai

    def removeClient(self, ai):
        """Stop managing an existing client"""
        self.deallocateId(ai.getId(), ai.getMode())
        # log: 'client {id} disconnected'

    def getClientById(self, id_):
        """Search for a client on the supplied channel"""
        client = self.id2owner.get(id_)
        if client:
            return client
        else:
            # log: 'client {id_} does not exist'
            return None

    def getClientByName(self, name):
        """Search for clients matching the supplied name"""
        client = self.name2owner.get(name)
        if client:
            return client
        else:
            # log: 'client {id_} does not exist'
            return None

    def getClientsByMode(self, mode):
        """Search for clients matching the supplied mode"""
        if mode in self.scope_map:
            return self.scope_map.get(mode).values()
        else:
            pass
