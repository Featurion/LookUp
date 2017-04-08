import base64
import json
import queue
from threading import Thread
from src.base import utils
from src.base.globals import COMMAND_SYNC, COMMAND_HELO, COMMAND_REDY
from src.base.globals import COMMAND_REJECT, COMMAND_END, COMMAND_MSG, SERVER_ID
from src.base.globals import MSG_TEMPLATE
from src.base.globals import ERR_INVALID_HMAC, ERR_MESSAGE_REPLAY
from src.base.globals import ERR_MESSAGE_DELETION, ERR_DECRYPT_FAILURE
from src.base.Message import Message
from src.base.Notifier import Notifier
from src.crypto.KeyHandler import KeyHandler


class SessionAI(Notifier):

    class _Member(tuple):

        def __new__(cls, id_, name, pub_key):
            _m = tuple.__new__(cls, (id_, name, pub_key))
            _m.__id = id_
            _m.__name = name
            _m.__pub_key = pub_key
            return _m

        def getId(self):
            return self.__id

        def getName(self):
            return self.__name

        def getPubKey(self):
            return self.__pub_key

    def __init__(self, server, id_, members):
        Notifier.__init__(self)

        self.server = server
        self.__id = id_

        self.key_handler = KeyHandler()
        self.key_handler.generateDHKey()
        self.__pub_key = self.key_handler.getDHPubKey()

        _cm = self.server.client_manager
        self.__members = set()
        self.__pending = set(members)

        self.message_queue = queue.Queue()

        self.receiver = Thread(target=self.__receiveMessages, daemon=True)
        self.receiver.start()

    def getId(self):
        return self.__id

    def getPubKey(self):
        return self.__pub_key

    def getMembers(self):
        return self.__members

    def getMemberIds(self):
        return [m.getId() for m in self.getMembers()]

    def getMemberNames(self):
        return [m.getName() for m in self.getMembers()]

    def getMemberPubKey(self, id_):
        for member in self.getMembers():
            if member.getId() == id_:
                return member.getPubKey()
        return None

    def getPendingMembers(self):
        return self.__pending

    def __receiveMessages(self):
        while True:
            message = self.message_queue.get()
            if message.command == COMMAND_END:
                self.emitMessage(message)
                return
            elif message.command == COMMAND_HELO:
                self.__memberJoined(message.from_id, json.loads(message.data))

                _cm = self.server.client_manager
                message.data = json.dumps([
                    message.to_id,
                    [
                        message.from_id,
                        _cm.getClientNameById(message.from_id)
                    ],
                    [
                        list(self.getPendingMembers()),
                        [_cm.getClientNameById(i) for i in self.getPendingMembers()]
                    ]
                ])
                for id_ in self.getPendingMembers():
                    message.to_id = id_
                    self.server.sendMessage(message)
            elif message.command == COMMAND_REDY:
                self.clientAccepted(message.from_id, message.data)
            elif message.command == COMMAND_REJECT:
                self.clientRejected(message.from_id)
            elif message.command == COMMAND_MSG:
                self.__transferEncryptedData(message)
            else:
                pass # unexpected command

    def __verifyHmac(self, hmac, data):
        generated_hmac = self.key_handler.generateHmac(data)
        return utils.secureStrCmp(generated_hmac, hmac)

    def __transferEncryptedData(self, message):
        _kh = self.key_handler
        _kh.computeDHSecret(self.getMemberPubKey(message.from_id))

        enc_data = message.getEncryptedDataAsBinaryString()
        hmac = message.getHmacAsBinaryString()

        if self.__verifyHmac(hmac, enc_data):
            try:
                message.data = _kh.aesDecrypt(enc_data).decode()
                self.emitMessage(message, self.__encryptForMember)
            except:
                self.notify.error(ERR_DECRYPT_FAILURE)
        else:
            self.notify.error(ERR_INVALID_HMAC)

    def __encryptForMember(self, id_, message):
        _cm = self.server.client_manager
        _kh = self.key_handler
        _kh.computeDHSecret(self.getMemberPubKey(id_))

        if id_ == message.from_id:
            src_color = '#0000CC'
        else:
            src_color = '#CC0000'

        msg = MSG_TEMPLATE.format(src_color,
                                  message.time,
                                  _cm.getClientNameById(message.from_id),
                                  message.data)

        enc_data = _kh.aesEncrypt(msg)
        hmac = _kh.generateHmac(enc_data)

        message = Message(COMMAND_MSG, self.getId(), id_)
        message.setEncryptedData(enc_data)
        message.setBinaryHmac(hmac)
        return message

    def __memberJoined(self, id_, key):
        _cm = self.server.client_manager
        self.__pending.remove(id_)
        self.__members.add(SessionAI._Member(id_,
                                             _cm.getClientNameById(id_),
                                             int(key)))

    def clientAccepted(self, id_, key):
        for member_id in self.getPendingMembers():
            if member_id == id_:
                self.__memberJoined(member_id, key)
                self.sync()
                return
        # TODO: error; client not expected

    def clientRejected(self, id_):
        self.__pending.remove(id_)
        self.sync()

    def emitMessage(self, message, modFunc=None, exclude=[]):
        for id_ in self.getMemberIds():
            if id_ in exclude:
                continue
            elif modFunc is not None:
                self.server.sendMessage(modFunc(id_, message))
            else:
                message.from_id = self.getId()
                message.to_id = id_
                self.server.sendMessage(message)

    def sessionReady(self):
        self.emitMessage(Message(COMMAND_REDY,
                                 None,
                                 None,
                                 self.getPubKey()))

    def sync(self):
        _cm = self.server.client_manager
        self.emitMessage(Message(COMMAND_SYNC,
                                 None,
                                 None,
                                 json.dumps([list(zip(self.getMemberIds(),
                                                      self.getMemberNames())),
                                             list(self.getPendingMembers())])))

        if (len(self.getMembers()) > 1) and not self.getPendingMembers():
            self.sessionReady()
        elif self.getPendingMembers():
            pass # still pending
        else:
            self.postMessage(Message(COMMAND_END, self.getId(), None))
            self.server.session_manager.removeSession(self)

    def postMessage(self, message):
        self.message_queue.put(message)
