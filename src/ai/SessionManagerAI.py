from src.base.Notifier import Notifier


class SessionManagerAI(Notifier):

    def __init__(self, ai):
        self.ai = ai
        self.__sessions = []
        self.__id2session = {}

    def addSession(self, session_ai):
        self.__sessions.append(session_ai)
        self.__id2session[session_ai.id] = session_ai

    def removeSession(self, session_ai):
        self.__sessions.remote(session_ai)
        del self.__id2session[session_ai.id]

    def getSession(self, session_id):
        return self.__id2session.get(session_id)

    def getSessionByMembers(self, members):
        for session in self.__sessions:
            if session.members == members:
                return session
        return None
