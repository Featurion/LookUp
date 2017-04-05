import json
from src.base.globals import COMMAND_SYNC
from src.base.Message import Message
from src.base.Notifier import Notifier


class SessionAI(Notifier):

    class _Member(tuple):

        def __new__(cls, id_, key=None):
            _m = tuple.__new__(cls, (id_, key))
            _m.__id = id_
            _m.__key = key
            return _m

        @property
        def key(self):
            return self.__key

        @property
        def id(self):
            return self.__id

        def setKey(self, key):
            if not self.__key:
                self.__key = key

    def __init__(self, ai, session_id, owner_key, owner_id, members):
        Notifier.__init__(self)
        self.ai = ai
        self.__id = session_id
        self.__members = [SessionAI._Member(owner_id, owner_key)]
        self.__pending = [SessionAI._Member(i) for i in sorted(members)]

    @property
    def id(self):
        return self.__id

    @property
    def members(self):
        return self.__members

    def addMember(self, partner_id, partner_key):
        for _member in self.__pending:
            if _member.id == partner_id:
                _member.setKey(partner_key)
                self.__pending.remove(_member)
                self.__members.append(_member)
                return
        # TODO: error; client not expected

    def sync(self):
        for member in self.__members:
            self.ai.forwardMessage(Message(COMMAND_SYNC,
                                           self.id,
                                           member.id,
                                           json.dumps([m.id for m in self.__members])))
