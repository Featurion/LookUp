from src.base.Notifier import Notifier

class BanManagerAI(Notifier):

    def __init__(self, client_manager):
        Notifier.__init__(self)
        self.client_manager = client_manager

    def kick(self, identifier):
        ai = self.client_manager.getClient(identifier)
        if ai:
            self.client_manager.removeClient(ai)
            return True
        else:
            return False

    def ban(self, identifier):
        ai = self.client_manager.getClient(identifier)
        if ai:
            self.client_manager.banClient(ai)
            return True
        else:
            return False

    def kill(self, ip):
        ais = self.client_manager.getClientsByAddress(ip)
        if ais:
            for ai in ais:
                self.client_manager.removeClient(ai)
            return True
        else:
            return False