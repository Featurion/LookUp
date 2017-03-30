from src.base.Notifier import Notifier
from src.sessions.Session import Session


class GroupSession(Session, Notifier):

    def __init__(self, session_id, client, *partners):
        Session.__init__(self, session_id, client, *partners)
        Notifier.__init__(self)

    def start(self):
        pass # TODO

    def stop(self):
        pass # TODO

    def addMember(self, client_id):
        self.__members.append(self.ai.client_manager.getClient(client_id))
