import base64
import json
import queue
from threading import Thread
from src.base.globals import COMMAND_HELO, COMMAND_REDY, COMMAND_END
from src.base.globals import COMMAND_SYNC, COMMAND_REJECT
from src.base.globals import DEBUG_REDY, DEBUG_SYNC, DEBUG_CLIENT_REJECT
from src.base.globals import DEBUG_CLIENT_CONN
from src.base.globals import ERR_BAD_HANDSHAKE, ERR_MESSAGE_REPLAY
from src.base.globals import ERR_MESSAGE_DELETION, ERR_DECRYPT_FAILURE
from src.base.globals import ERR_INVALID_HMAC
from src.base.utils import secureStrCmp
from src.base.Message import Message
from src.base.Notifier import Notifier
from src.crypto.KeyHandler import KeyHandler

class Session(Notifier):

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

    def __init__(self, id_, client, members):
        Notifier.__init__(self)
        self.client = client
        self.__id = id_
        self.__members = {Session._Member(self.client.getId(),
                                          self.client.getName(),
                                          self.client.getKey())}
        self.__pending = set(members)
        self.message_queue = queue.Queue()
        self.incoming_message_num = 0
        self.outgoing_message_num = 0
        self.key_handler = KeyHandler()
        self.key_handler.generateDHKey()
        self.encrypted = False
        self.receiver = Thread(target=self.__receiveMessages, daemon=True)

    def getId(self):
        return self.__id

    def getMembers(self):
        return set(self.__members)

    def getMemberIds(self):
        return [m.getId() for m in self.getMembers()]

    def getMemberNames(self):
        return [m.getName() for m in self.getMembers()]

    def setMembers(self, members):
        self.__members = members

    def getPendingMembers(self):
        return set(self.__pending)

    def setPendingMembers(self, pending):
        self.__pending = pending

    def start(self):
        self.sendMessage(COMMAND_HELO, json.dumps(list(self.getPendingMembers()),
                                                  ensure_ascii=True))
        self.receiver.start()

    def join(self):
        self.sendMessage(COMMAND_REDY, self.client.getKey())
        self.receiver.start()

    def stop(self): # TODO
        pass

    def __verifyHmac(self, hmac, data):
        generated_hmac = self.key_handler.generateHmac(data)
        return secureStrCmp(generated_hmac, base64.b64decode(hmac))

    def __receiveMessages(self):
        while True:
            message = self.message_queue.get()
            if message.command == COMMAND_END:
                self.message_queue.task_done()
                return # TODO
            elif message.command == COMMAND_REDY:
                self.notify.debug(DEBUG_REDY, message.from_id)
                self.encrypted = True
                # TODO: secure the chat
            elif message.command == COMMAND_REJECT:
                self.notify.debug(DEBUG_CLIENT_REJECT,
                                  message.data,
                                  message.to_id)
            elif message.command == COMMAND_SYNC:
                self.notify.debug(DEBUG_SYNC, self.getId())
                members, pending = json.loads(message.data)
                _m = set(Session._Member(i, n, k) for i, n, k in members)
                self.setMembers(_m)
                for id_ in self.getPendingMembers():
                    if (id_ not in pending) and (id_ in self.getMemberIds()):
                        self.notify.debug(DEBUG_CLIENT_CONN,
                                          id_,
                                          self.getId())
                    elif id_ in pending:
                        pass # still pending
                    elif id_ not in self.getMemberIds():
                        self.notify.debug(DEBUG_CLIENT_REJECT,
                                          id_,
                                          self.getId())
                    else:
                        self.notify.error(ERR_BAD_HANDSHAKE, message.data)
                        return
                self.setPendingMembers(set(pending))
            else:
                _data = self.getDecryptedData(message)
                pass

    def getDecryptedData(self, message):
        if self.encrypted:
            data = message.getEncryptedDataAsBinaryString()
            enc_num = message.getMessageNumAsBinaryString()
            if not self.__verifyHmac(message.hmac, data):
                self.notify.error(ERR_INVALID_HMAC)
            else:
                try:
                    num = int(self.key_handler.aesDecrypt(enc_num))
                    if self.incoming_message_num > num:
                        self.notify.error(ERR_MESSAGE_REPLAY)
                    elif self.incoming_message_num < num:
                        self.notify.error(ERR_MESSAGE_DELETION)
                    self.incoming_message_num += 1
                    data = self.key_handler.aesDecrypt(data)
                except:
                    self.notify.error(ERR_DECRYPT_FAILURE)
        else:
            return message.data

    def sendMessage(self, command, data=None):
        message = Message(command,
                          self.client.getId(),
                          self.getId())
        if (data is not None) and self.encrypted:
            enc_data = self.key_handler.aesEncrypt(data)
            num = self.key_handler.aesEncrypt(str(self.outgoing_message_num).encode())
            hmac = self.key_handler.generateHmac(enc_data)
            message.setEncryptedData(enc_data)
            message.setBinaryHmac(hmac)
            message.setBinaryMessageNum(num)
            self.outgoing_message_num += 1
        elif data is not None:
            message.data = data
        else:
            pass
        self.client.sendMessage(message)

    def sendChatMessage(self, text):
        self.sendMessage(COMMAND_MSG, data=text)

    def sendTypingMessage(self, status):
        self.sendMessage(COMMAND_TYPING, data=str(status))

    def postMessage(self, message):
        self.message_queue.put(message)
