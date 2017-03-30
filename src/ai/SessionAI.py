from src.base.Notifier import Notifier


class SessionAI(Notifier):

    def __init__(self, ai, session_id):
        Notifier.__init__(self)
        self.ai = ai
        self.__id = session_id
        self.__members = []

    @property
    def id(self):
        return self.__id

    @property
    def members(self):
        return self.__members

    def addMember(self, partner_id):
        self.__members.append(partner_id)
