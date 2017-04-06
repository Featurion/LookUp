import json
import queue
from threading import Thread
from src.base.globals import COMMAND_SYNC, COMMAND_HELO, COMMAND_REDY
from src.base.globals import COMMAND_REJECT, COMMAND_END, SERVER_ID
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
        self.__pending = set(members)
        self.message_queue = queue.Queue()
        self.receiver = Thread(target=self.__receiveMessages, daemon=True)
        self.receiver.start()

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

    def __receiveMessages(self):
        while True:
            message = self.message_queue.get()
            if message.command == COMMAND_END:
                self.emit(message)
                return
            elif message.command == COMMAND_HELO:
                _cm = self.server.client_manager
                members = json.loads(message.data)
                message.data = json.dumps([
                    message.to_id,
                    [
                        message.from_id,
                        _cm.getClientNameById(message.from_id)
                    ],
                    [
                        members,
                        [_cm.getClientNameById(i) for i in members]
                    ]
                ])
                for id_ in members:
                    message.to_id = id_
                    self.server.sendMessage(message)
            elif message.command == COMMAND_REDY:
                _sm = self.server.session_manager
                session = _sm.getSessionById(message.to_id)
                session.addMember(message.from_id, message.data)
                session.sync()
            elif message.command == COMMAND_REJECT:
                _sm = self.server.session_manager
                session = _sm.getSessionById(message.to_id)
                session.clientRejected(message.from_id)
                session.sync()

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

    def clientRejected(self, id_):
        self.__pending.remove(id_)

    def sync(self):
        _cm = self.server.client_manager
        self.emit(Message(COMMAND_SYNC,
                          self.getId(), None,
                          json.dumps([list(self.getMembers()),
                                      list(self.getPendingMembers())])))

        if (len(self.getMembers()) > 1) and not self.getPendingMembers():
            self.ready()
        elif self.getPendingMembers():
            pass # still pending
        else:
            self.postMessage(Message(COMMAND_END, self.getId(), None))
            self.server.session_manager.removeSession(self)

    def postMessage(self, message):
        self.message_queue.put(message)
