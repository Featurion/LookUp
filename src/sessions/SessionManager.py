from src.base.globals import DEBUG_END
from src.base.Notifier import Notifier
from src.sessions.PrivateSession import PrivateSession
from src.sessions.GroupSession import GroupSession


class SessionManager(Notifier):

    def __init__(self, client):
        Notifier.__init__(self)
        self.client = client
        self.__sessions = {}

    @property
    def sessions(self):
        return self.__sessions.items()

    def start(self):
        pass # TODO

    def _startSession(self, session):
        self.__sessions[session.id] = session
        session.start()

    def openPrivateSession(self, partner_id):
        new_session = PrivateSession(partner_id)
        self._startSession(new_session)

    def openGroupSession(self, partner_ids):
        new_session = GroupSession(partner_ids)
        self._startSession(new_session)

    def closeSession(self, session_id):
        session = self.__sessions.get(session_id)
        if session:
            session.stop()

    def stop(self):
        for partner_id, session in self.sessions:
            session.stop()
            self.notify.info(DEBUG_END, partner_id)
        self.__sessions.clear()
