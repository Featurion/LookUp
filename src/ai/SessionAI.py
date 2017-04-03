import json
from src.base.globals import COMMAND_SYNC
from src.base.Message import Message
from src.base.Notifier import Notifier


class SessionAI(Notifier):

    def __init__(self, ai, session_id, members):
        Notifier.__init__(self)
        self.ai = ai
        self.__id = session_id
        self.__members = [members.pop(0)]
        self.__pending = sorted(members)

    @property
    def id(self):
        return self.__id

    @property
    def members(self):
        return self.__members

    def addMember(self, partner_id):
        if partner_id in self.__pending:
            self.__pending.remove(partner_id)
            self.__members.append(partner_id)
            self.__members = sorted(self.__members)
        else:
            pass # TODO: error; client not expected

    def sync(self):
        for member in self.__members:
            self.ai.forwardMessage(Message(COMMAND_SYNC,
                                           self.id,
                                           member,
                                           json.dumps(self.__members)))
