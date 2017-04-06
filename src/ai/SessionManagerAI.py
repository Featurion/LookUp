import uuid
from src.ai.SessionAI import SessionAI
from src.base.Notifier import Notifier


class SessionManagerAI(Notifier):

    def __init__(self, server):
        self.server = server
        self.__sessions = []
        self.__id2session = {}

    def getSessions(self):
        return self.__sessions

    def getSessionById(self, session_id):
        return self.__id2session.get(session_id)

    def getSessionByMembers(self, members):
        for session in self.getSessions():
            if set(session.members) == set(members):
                return session
        return None

    def generateSession(self, key, id_, members):
        session_id = uuid.uuid4().hex
        session_ai = SessionAI(self.server,
                               session_id,
                               key, id_,
                               members)
        self.addSession(session_ai)
        return session_id

    def addSession(self, session_ai):
        self.__sessions.append(session_ai)
        self.__id2session[session_ai.getId()] = session_ai

    def removeSession(self, session_ai):
        self.__sessions.remote(session_ai)
        del self.__id2session[session_ai.getId()]
