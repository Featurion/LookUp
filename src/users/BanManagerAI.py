from src.base import constants
from src.base.Notifier import Notifier


class BanManagerAI(Notifier):

    def __init__(self, server):
        Notifier.__init__(self)
        self.server = server

    def kick(self, identifier, reason):
        ai = self.server.cm.getClient(identifier)
        if ai:
            ai.sendDisconnect(reason, constants.KICK)
            self.server.cm.removeClient(ai)
            return True
        else:
            return False

    def ban(self, identifier, reason, address_only=False):
        if address_only:
            self.server.cm.banClient(reason, address=identifier)
            return True
        else:
            ai = self.server.cm.getClient(identifier)
            if ai:
                ai.sendDisconnect(reason, constants.BAN)
                self.server.cm.banClient(reason, ai)
                return True
            else:
                return False

    def kill(self, ip, reason):
        ais = self.server.cm.getClientsByAddress(ip)
        if ais:
            for ai in ais:
                ai.sendDisconnect(reason, constants.KILL)
                self.server.cm.removeClient(ai)
            return True
        else:
            return False
