import json
from src.base.globals import COMMAND_SYNC
from src.base.Message import Message
from src.base.Notifier import Notifier


class SessionAI(Notifier):

    class _Member(tuple):

        def __new__(cls, id_, key):
            _m = tuple.__new__(cls, (id_, key))
            _m.__id = id_
            _m.__key = key
            return _m

        def getId(self):
            return self.__id

        def getKey(self):
            return self.__key

    def __init__(self, server, id_, owner_key, owner_id, members):
        Notifier.__init__(self)
        self.server = server
        self.__id = id_
        _cm = self.server.client_manager
        self.__members = [SessionAI._Member(owner_id, owner_key)]
        self.__pending = [_cm.getClientIdByName(n) for n in members]

    def getId(self):
        return self.__id

    def getMembers(self):
        return self.__members

    def getPendingMembers(self):
        return self.__pending

    def __memberJoined(self, member_id, key):
        self.__pending = [m for m in self.__pending if m != member_id]
        self.__members.append(SessionAI._Member(member_id, key))

    def addMember(self, id_, key):
        for member_id in self.getPendingMembers():
            if member_id == id_:
                self.__memberJoined(member_id, key)
                return
        # TODO: error; client not expected

    def sync(self):
        member_ids = [m.getId() for m in self.getMembers()]
        message = Message(COMMAND_SYNC,
                          self.getId(), None,
                          json.dumps(member_ids))
        for id_ in member_ids:
            message.to_id = id_
            self.server.sendMessage(message)
