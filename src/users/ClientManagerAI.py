from uuid import UUID

from src.base.UniqueIDManager import UniqueIDManager
from src.users.ClientAI import ClientAI

class ClientManagerAI(UniqueIDManager):
    """Manage connected clients"""

    SCOPES = {
        'temp': UUID('a5f7a870e9254cb39b341ab726df7952'),
        'lite': UUID('e8e4d5b1749a4ff19e0d8dab65bf4ff0'),
        'paid': UUID('e6b429c7ccc8401f8c1d99e9fe3451cd'),
    } # listed by precedence
    SCOPES.update(UniqueIDManager.SCOPES)

    def __init__(self, server):
        UniqueIDManager.__init__(self)
        self.server = server
        self.clients = []

    def acceptClient(self):
        """Accept a connecting client"""
        self.notify.debug('waiting for socket connection...')
        socket_, (address, port) = self.server.accept()
        ai = ClientAI(self.server, address, port)
        ai.setSocket(socket_)
        self.notify.debug('client connected at {0}'.format(ai.getAddress()))
        return ai

    def addClient(self, ai):
        ai.setId(self.generateId(ai.getMode(), ai.getName()))
        self.allocateId(ai.getMode(), ai.getName(), ai.getId(), ai)
        self.clients.append(ai)
        self.notify.debug('client {0}-{1} connected'.format(ai.getName(),
                                                            ai.getId()))

    def removeClient(self, ai):
        """Stop managing an existing client"""
        self.deallocateId(ai.getId(), ai.getMode())
        self.clients.remove(ai)
        self.notify.debug('client {0}-{1} disconnected'.format(ai.getName(),
                                                               ai.getId()))

    def getClients(self):
        return self.clients

    def getClientById(self, id_):
        """Search for a client with the supplied ID"""
        for ai in self.getClients():
            if ai.getId() == id_:
                return ai

        self.notify.debug('client with id {0} does not exist!'.format(id_))
        return None

    def getClientByName(self, name):
        """Search for clients matching the supplied name"""
        for ai in self.getClients():
            if ai.getName() == name:
                return ai

        self.notify.debug('client with name {0} does not exist!'.format(name))
        return None

    def getClientsByMode(self, mode):
        """Search for clients matching the supplied mode"""
        if mode in self.scope_map:
            return self.scope_map.get(mode).values()
        else:
            pass
