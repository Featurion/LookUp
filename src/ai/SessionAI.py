import json
from src.base.globals import COMMAND_SYNC, COMMAND_REDY
from src.base.Message import Message
from src.base.Notifier import Notifier


class SessionAI(Notifier):

    class _Member(tuple):

        def __new__(cls, id_, name, key):
            _m = tuple.__new__(cls, (id_, name, key))
            _m.__id = id_
            _m.__name = name
            _m.__key = key
            return _m

        def getId(self):
            return self.__id

        def getName(self):
            return self.__name

        def getKey(self):
            return self.__key

    def __init__(self, server, id_, owner_key, owner_id, members):
        Notifier.__init__(self)
        self.server = server
        self.__id = id_
        _cm = self.server.client_manager
        self.__members = {SessionAI._Member(owner_id,
                                            _cm.getClientNameById(owner_id),
                                            owner_key)}
        self.__pending = set(_cm.getClientIdByName(n) for n in members)

    def getId(self):
        return self.__id

    def getMembers(self):
        return self.__members

    def getMemberIds(self):
        return [m.getId() for m in self.getMembers()]

    def getMemberNames(self):
        return [m.getName() for m in self.getMembers()]

    def getPendingMembers(self):
        return self.__pending

    def __memberJoined(self, id_, key):
        _cm = self.server.client_manager
        self.__pending.remove(id_)
        self.__members.add(SessionAI._Member(id_,
                                             _cm.getClientNameById(id_),
                                             key))

    def addMember(self, id_, key):
        for member_id in self.getPendingMembers():
            if member_id == id_:
                self.__memberJoined(member_id, key)
                return
        # TODO: error; client not expected

    def emit(self, message, exclude=False):
        for id_ in self.getMemberIds():
            if (id_ == message.from_id) and exclude:
                continue
            else:
                message.from_id = self.getId()
                message.to_id = id_
                self.server.sendMessage(message)

    def ready(self):
        self.emit(Message(COMMAND_REDY, self.getId(), None))

    def sync(self):
        self.emit(Message(COMMAND_SYNC,
                          self.getId(), None,
                          json.dumps(list(self.getMembers()))))
        if not self.__pending:
            self.ready()
