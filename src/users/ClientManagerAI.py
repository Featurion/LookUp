from uuid import UUID

from src.base import constants
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
        self.banlist = []

    def acceptClient(self):
        """Accept a connecting client"""
        self.notify.debug('waiting for socket connection...')
        socket_, (address, port) = self.server.accept()
        if address in self.banlist:
            # This client has been banned
            self.notify.debug('client banned!')
            socket_.send(constants.BANNED)
            socket_.close()
            return False
        else:
            # This client is not banned
            socket_.send(constants.ACCEPTED)
        ai = ClientAI(self.server, address, port)
        ai.setSocket(socket_)
        self.notify.debug('client connected at {0}'.format(ai.getAddress()))

        del socket_
        del address
        del port

        return ai

    def addClient(self, ai):
        ai.setId(self.generateId(ai.getMode(), ai.getName()))
        self.allocateId(ai.getMode(), ai.getName(), ai.getId(), ai)
        self.clients.append(ai)
        self.notify.debug('client {0}-{1} connected'.format(ai.getName(),
                                                            ai.getId()))

        del ai

    def removeClient(self, ai):
        """Stop managing an existing client"""
        self.deallocateId(ai.getId(), ai.getMode())
        self.clients.remove(ai)
        self.notify.debug('client {0}-{1} disconnected'.format(ai.getName(),
                                                               ai.getId()))

        # ai.cleanup() - TODO Zach: Fix cleanup()
        del ai

    def banClient(self, ai):
        """Kickban an existing client"""
        self.removeClient(ai) # First, kick the client
        self.banlist.append(ai.getAddress())

    def getClients(self):
        return self.clients

    def getClientById(self, id_):
        """Search for a client with the supplied ID"""
        for ai in self.getClients():
            if ai.getId() == id_:
                return ai
        self.notify.debug('client with id {0} does not exist'.format(id_))

        del id_

        return None

    def getClientByName(self, name):
        """Search for clients matching the supplied name"""
        for ai in self.getClients():
            if ai.getName() == name:
                return ai
        self.notify.debug('client with name {0} does not exist'.format(name))

        del name

        return None

    def getClientByAddress(self, ip):
        """Search for clients matching the supplied IP address"""
        for ai in self.getClients():
            if ai.getAddress() == ip:
                return ai
        self.notify.debug('client with ip {0} does not exist'.format(ip))

        del ip

        return None

    def getClientsByAddress(self, ip):
        """Search for multiple clients matching the supplied IP address"""
        ais = []
        for ai in self.getClients():
            if ai.getAddress() == ip:
                ais.append(ip)
                return ais
        self.notify.debug('no client with ip {0} exists'.format(ip))

        del ip

        return None

    def getClientsByMode(self, mode):
        """Search for clients matching the supplied mode"""
        if mode in self.scope_map:
            return self.scope_map.get(mode).values()
        else:
            pass

        del mode

    def getClient(self, identifier):
        ai = self.getClientById(identifier) # Assume it's an ID
        if ai == None: # Not an ID
            ai = self.getClientByName(identifier) # Assume it's a name
            if ai == None: # Not a name
                ai = self.getClientByAddress(identifier) # Assume it's an IP
                if ai == None: # Not an IP
                    self.notify.debug('identifier is not a valid ID, name, or IP!')
                    return None

        return ai