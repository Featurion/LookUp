import base64
import json
import queue
from threading import Thread
from src.base import utils
from src.base.globals import COMMAND_HELO, COMMAND_REDY, COMMAND_END
from src.base.globals import COMMAND_SYNC, COMMAND_REJECT, COMMAND_MSG
from src.base.globals import COMMAND_CLIENT_MSG, MSG_TEMPLATE, CLIENT_JOINED
from src.base.globals import DEBUG_REDY, DEBUG_SYNC, DEBUG_CLIENT_REJECT
from src.base.globals import DEBUG_CLIENT_CONN
from src.base.globals import ERR_BAD_HANDSHAKE, ERR_MESSAGE_REPLAY
from src.base.globals import ERR_MESSAGE_DELETION, ERR_DECRYPT_FAILURE
from src.base.globals import ERR_INVALID_HMAC
from src.base.Message import Message
from src.base.Notifier import Notifier
from src.crypto.KeyHandler import KeyHandler

class Session(Notifier):

    class _Member(tuple):

        def __new__(cls, id_, name):
            _m = tuple.__new__(cls, (id_, name))
            _m.__id = id_
            _m.__name = name
            return _m

        def getId(self):
            return self.__id

        def getName(self):
            return self.__name

    def __init__(self, tab, id_, client, members):
        Notifier.__init__(self)
        self.client = client

        self.__tab = tab
        self.__id = id_

        self.key_handler = KeyHandler()
        self.key_handler.generateDHKey()
        self.__pub_key = self.key_handler.getDHPubKey()
        self.__alt_pub_key = None

        self.__members = {Session._Member(self.client.getId(),
                                          self.client.getName())}
        self.__pending = set(members)

        self.message_queue = queue.Queue()
        self.encrypted = False

        self.receiver = Thread(target=self.__receiveMessages, daemon=True)

    def getTab(self):
        return self.__tab

    def getId(self):
        return self.__id

    def getPubKey(self):
        return self.__pub_key

    def getAltPubKey(self):
        return self.__alt_pub_key

    def setAltPubKey(self, key):
        assert isinstance(key, int)
        if self.getAltPubKey() is None:
            self.__alt_pub_key = key

    def getMembers(self):
        return set(self.__members)

    def setMembers(self, members):
        assert isinstance(members, set)
        self.__members = members

    def getMemberIds(self):
        return [m.getId() for m in self.getMembers()]

    def getMemberNames(self):
        return [m.getName() for m in self.getMembers()]

    def getMemberIdsAndNames(self):
        return list(zip(self.getMemberIds(), self.getMemberNames()))

    def getPendingMembers(self):
        return set(self.__pending)

    def setPendingMembers(self, pending):
        assert isinstance(pending, set)
        self.__pending = pending

    def getEncrypted(self):
        return self.encrypted

    def setEncrypted(self, encrypted):
        self.encrypted = encrypted

    def start(self):
        self.sendMessage(COMMAND_HELO, str(self.getPubKey()))
        self.receiver.start()

    def join(self):
        self.sendMessage(COMMAND_REDY, str(self.getPubKey()))
        self.receiver.start()

    def stop(self): # TODO
        pass

    def __receiveMessages(self):
        while True:
            message = self.message_queue.get()
            if message.command == COMMAND_END:
                self.message_queue.task_done()
                return # TODO
            elif message.command == COMMAND_REDY:
                self.notify.debug(DEBUG_REDY, message.from_id)
                self.setAltPubKey(int(message.data))
                self.setEncrypted(True)
                self.getTab().widget_stack.setCurrentIndex(2)
                self.__notifyReady()
            elif message.command == COMMAND_REJECT:
                self.notify.debug(DEBUG_CLIENT_REJECT,
                                  message.data,
                                  message.to_id)
            elif message.command == COMMAND_SYNC:
                self.notify.debug(DEBUG_SYNC, self.getId())

                members, pending = json.loads(message.data)
                _m = set(Session._Member(i, n) for i, n in members)
                self.setMembers(_m)

                for id_ in self.getPendingMembers():
                    if (id_ not in pending) and (id_ in self.getMemberIds()):
                        if id_ != self.client.getId():
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
            elif message.command == COMMAND_MSG:
                if self.getEncrypted():
                    data = self.__getDecryptedData(message)
                else:
                    data = message.data

                data, timestamp = utils.parseTimestampFromMessage(data)
                data = data.format(utils.formatTimestamp(timestamp))

                self.getTab().new_message_signal.emit(data, timestamp)
            elif message.command == COMMAND_CLIENT_MSG:
                data = MSG_TEMPLATE.format('#000000',
                                           '',
                                           'server',
                                           message.data)
                self.getTab().new_message_signal.emit(data,
                                                      utils.getTimestamp())
            else:
                pass # unexpected command

    def __notifyReady(self):
        for name in self.getMemberNames():
            if name == self.client.getName():
                continue
            else:
                self.message_queue.put(Message(COMMAND_CLIENT_MSG,
                                               self.getId(),
                                               self.client.getId(),
                                               CLIENT_JOINED.format(name)))

    def __verifyHmac(self, hmac, data):
        generated_hmac = self.key_handler.generateHmac(data)
        return utils.secureStrCmp(generated_hmac, hmac)

    def __getDecryptedData(self, message):
        _kh = self.key_handler
        _kh.computeDHSecret(self.getAltPubKey())

        enc_data = message.getEncryptedDataAsBinaryString()
        hmac = message.getHmacAsBinaryString()

        if self.__verifyHmac(hmac, enc_data):
            try:
                return _kh.aesDecrypt(enc_data).decode()
            except:
                self.notify.error(ERR_DECRYPT_FAILURE)
        else:
            self.notify.error(ERR_INVALID_HMAC)

    def sendMessage(self, command, data=None):
        message = Message(command, self.client.getId(), self.getId())

        if (data is not None) and self.getEncrypted():
            _kh = self.key_handler
            _kh.computeDHSecret(self.getAltPubKey())

            enc_data = _kh.aesEncrypt(data)
            hmac = _kh.generateHmac(enc_data)

            message.setEncryptedData(enc_data)
            message.setBinaryHmac(hmac)
        elif data is not None:
            message.data = data
        else:
            return

        self.client.sendMessage(message)

    def sendChatMessage(self, data):
        self.sendMessage(COMMAND_MSG, data)

    def postMessage(self, message):
        self.message_queue.put(message)
