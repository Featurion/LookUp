from src.base import constants
from src.base.Notifier import Notifier

class BanManagerAI(Notifier):

    def __init__(self, client_manager):
        Notifier.__init__(self)
        self.client_manager = client_manager

    def kick(self, identifier):
        ai = self.client_manager.getClient(identifier)
        if ai:
            ai.sendDisconnect(constants.KICK)
            self.client_manager.removeClient(ai)
            return True
        else:
            return False

    def ban(self, identifier, address_only=False):
        if address_only:
            self.client_manager.banClient(address=identifier)
            return True
        else:
            ai = self.client_manager.getClient(identifier)
            if ai:
                ai.sendDisconnect(constants.BAN)
                self.client_manager.banClient(ai)
                return True
            else:
                return False

    def kill(self, ip):
        ais = self.client_manager.getClientsByAddress(ip)
        if ais:
            for ai in ais:
                ai.sendDisconnect(constants.KILL)
                self.client_manager.removeClient(ai)
            return True
        else:
            return False