from src.base.Notifier import Notifier
from src.sessions.Session import Session


class GroupSession(Session, Notifier):

    def __init__(self, partner_ids):
        Session.__init__(self)
        Notifier.__init__(self)
        self.partners = partner_ids

    def start(self):
        pass # TODO

    def stop(self):
        pass # TODO
