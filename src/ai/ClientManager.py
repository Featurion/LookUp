from uuid import UUID

from src.base.UniqueIDManager import UniqueIDManager
from src.userbase.ClientAI import ClientAI


class ClientManager(UniqueIDManager):
    """Manage connected clients"""

    __SCOPES = {
        'temp': UUID('a5f7a870e9254cb39b341ab726df7952'),
        'lite': UUID('e8e4d5b1749a4ff19e0d8dab65bf4ff0'),
        'paid': UUID('e6b429c7ccc8401f8c1d99e9fe3451cd'),
    } # listed by precedence

    def __init__(self, socket_):
        UniqueIDManager.__init__(self)
        self.__socket = socket_

    def accept(self):
        """Accept a connecting client"""
        # log: 'waiting for socket connection'
        socket_, (address, port) = self.__socket.accept()
        scope, seed, id_ = self.generateId()
        ai = ClientAI(address, port, socket_, id_)
        self.allocateId(scope, seed, id_, ai)
        return ai

    def addClient(self, id_, mode, name):
        if mode not in self.__SCOPES:
            # err: ValueError('received invalid mode')
            # log: WARNING, 'suspicious node allocation attempted'
            return None
        else:
            ai = self.getClientById(id_)
            id_ = self.generateId(mode, name)
            ai._NodeBase__setId(id_)
            ai.start()
            return ai

    def removeClient(self, id_):
        """Stop managing an existing client"""
        return NotImplemented

    def getClientById(self, id_):
        """Search for a client on the supplied channel"""
        client = self.id2owner.get(id_)
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

    def getClientsByName(self, name):
        """Search for clients matching the supplied name"""
        return NotImplemented
