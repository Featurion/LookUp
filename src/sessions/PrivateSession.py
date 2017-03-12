from src.base.Notifier import Notifier
from src.sessions.Session import Session


class PrivateSession(Session, Notifier):

    def __init__(self, partner_id):
        Session.__init__(self)
        Notifier.__init__(self)
        self.partner = partner_id

    def start(self):
        pass # TODO

    def stop(self):
        pass # TODO
