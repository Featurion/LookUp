from src.base import constants
from src.base.Notifier import Notifier

class BanManagerAI(Notifier):

    def __init__(self, server):
        Notifier.__init__(self)
        self.server = server

    def kick(self, identifier):
        ai = self.server.cm.getClient(identifier)
        if ai:
            ai.sendDisconnect(constants.KICK)
            self.server.cm.removeClient(ai)
            return True
        else:
            return False

    def ban(self, identifier, address_only=False):
        if address_only:
            self.server.cm.banClient(address=identifier)
            return True
        else:
            ai = self.server.cm.getClient(identifier)
            if ai:
                ai.sendDisconnect(constants.BAN)
                self.server.cm.banClient(ai)
                return True
            else:
                return False

    def kill(self, ip):
        ais = self.server.cm.getClientsByAddress(ip)
        if ais:
            for ai in ais:
                ai.sendDisconnect(constants.KILL)
                self.server.cm.removeClient(ai)
            return True
        else:
            return False
