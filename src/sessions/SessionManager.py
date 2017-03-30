from src.base.globals import SERVER_ID, COMMAND_REQ_SESSION
from src.base.globals import DEBUG_END, DEBUG_SESSION_START, DEBUG_SESSION_JOIN
from src.base.globals import DEBUG_UNAVAILABLE
from src.base.globals import DEBUG_CONNECTED_PRIVATE, DEBUG_CONNECTED_GROUP
from src.base.Message import Message
from src.base.Notifier import Notifier
from src.sessions.PrivateSession import PrivateSession
from src.sessions.GroupSession import GroupSession


class SessionManager(Notifier):

    def __init__(self, client):
        Notifier.__init__(self)
        self.client = client
        self.__sessions = {}
        self.__priv_session_partners = []
        self.__group_session_partners = []

    @property
    def sessions(self):
        return self.__sessions.items()

    def start(self):
        pass # TODO

    def getSession(self, session_id):
        return self.__sessions.get(session_id)

    def _startSession(self, *partners):
        self.client.sendMessage(Message(COMMAND_REQ_SESSION,
                                        self.client.id, SERVER_ID))
        session_id = self.client._waitForResp()
        if len(partners) > 1:
            session = GroupSession(session_id, self.client, *partners)
        else:
            session = PrivateSession(session_id, self.client, *partners)
        self.__sessions[session.id] = session
        self.notify.info(DEBUG_SESSION_START, session.id)
        session.start()

    def openPrivateSession(self, name):
        if name not in self.__priv_session_partners:
            partner_id = self.client.getIdByName(name)
            if partner_id != '':
                self.__priv_session_partners.append(partner_id)
                self._startSession(partner_id)
            else:
                self.notify.info(DEBUG_UNAVAILABLE, name)
                # TODO: hook back to UI
        else:
            self.notify.info(DEBUG_CONNECTED_PRIVATE, name)
            # TODO: hook back to UI

    def joinPrivateSession(self, session_id, partner_id):
        session = PrivateSession(session_id, self.client, partner_id)
        self.__sessions[session.id] = session
        self.notify.info(DEBUG_SESSION_JOIN, session.id)
        session.join()

    def openGroupSession(self, names):
        names = sorted(names)
        if names not in self.__group_session_partners:
            partners = {n: self.client.getIdByName(n) for n in names}
            for n, i in partners:
                if i == '':
                    self.notify.info(DEBUG_USER_UNAVAILABLE, n)
                    return
            self.__group_session_partners.append(partners.values())
            self._startSession(*partners.values())
        else:
            self.notify.info(DEBUG_CONNECTED_GROUP, name)
            # TODO: hook back to UI

    def joinGroupSession(self, session_id): # TODO
        return NotImplemented

    def closeSession(self, session_id):
        session = self.__sessions.get(session_id)
        if session:
            session.stop()
            del self.__sessions[session_id]

    def stop(self):
        for session_id, session in self.sessions:
            session.stop()
            self.notify.info(DEBUG_END, session_id)
        self.__sessions.clear()
