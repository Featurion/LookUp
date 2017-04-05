import json
from src.base.globals import SERVER_ID, COMMAND_REQ_SESSION
from src.base.globals import DEBUG_END, DEBUG_SESSION_START, DEBUG_SESSION_JOIN
from src.base.globals import DEBUG_UNAVAILABLE
from src.base.globals import DEBUG_CONNECTED_PRIVATE, DEBUG_CONNECTED_GROUP
from src.base.Message import Message
from src.base.Notifier import Notifier
from src.sessions.Session import Session


class SessionManager(Notifier):

    def __init__(self, client):
        Notifier.__init__(self)
        self.client = client
        self.__sessions = {}
        self.__session_member_map = {}

    @property
    def sessions(self):
        return self.__sessions.items()

    def start(self):
        pass # TODO

    def getSession(self, session_id):
        return self.__sessions.get(session_id)

    def getSessionByMembers(self, partners):
        for i, p in self.__session_member_map.items():
            if sorted(partners) == p:
                return self.getSession(i)
        return None

    def _startSession(self, partners):
        self.client.sendMessage(Message(COMMAND_REQ_SESSION,
                                        self.client.id, SERVER_ID,
                                        json.dumps([self.client.pub_key,
                                                    self.client.id,
                                                    partners],
                                                   ensure_ascii=True)))
        session_id = self.client._waitForResp()
        session = Session(session_id, self.client, partners)
        self.__sessions[session.id] = session
        self.__session_member_map[session.id] = partners
        self.notify.debug(DEBUG_SESSION_START, session.id)
        session.start()

    def openSession(self, partners):
        partners = sorted(partners)
        if partners in self.__session_member_map.values():
            self.notify.debug(DEBUG_CONNECTED, name)
            # TODO: hook back to UI
        else:
            id2name = {self.client.getIdByName(n): n for n in partners}
            for i, n in id2name.items():
                if n == '':
                    self.notify.debug(DEBUG_USER_UNAVAILABLE, n)
                    del id2name[i]
            self._startSession(sorted(id2name.keys()))

    def joinSession(self, session_id, partners):
        session = Session(session_id, self.client, partners)
        self.__sessions[session.id] = session
        self.notify.debug(DEBUG_SESSION_JOIN, session.id)
        session.join()

    def closeSession(self, session_id):
        session = self.__sessions.get(session_id)
        if session:
            session.stop()
            del self.__sessions[session_id]
            del self.__session_member_map[session_id]

    def stop(self):
        for session_id, session in self.sessions:
            session.stop()
            self.notify.info(DEBUG_END, session_id)
        self.__sessions.clear()
        self.__session_member_map.clear()
