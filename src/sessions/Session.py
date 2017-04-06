import base64
import json
import queue
from threading import Thread
from src.base.globals import *
from src.base.utils import secureStrCmp
from src.base.Message import Message
from src.base.Notifier import Notifier
from src.crypto.CryptoHandler import CryptoHandler

class Session(Notifier):

    def __init__(self, id_, client, members):
        Notifier.__init__(self)
        self.client = client
        self.__id = id_
        self.__pending = members
        self.__members = {self.client.getId()}
        self.message_queue = queue.Queue()
        self.incoming_message_num = 0
        self.outgoing_message_num = 0
        self.key_handler = CryptoHandler()
        self.key_handler.generateDHKey()
        self.encrypted = False
        self.receiver = Thread(target=self.__receiveMessages)

    def getId(self):
        return self.__id

    def getMembers(self):
        return set(self.__members)

    def start(self):
        self.client.sendMessage(Message(COMMAND_HELO,
                                        self.client.getId(),
                                        self.getId(),
                                        json.dumps(list(self.__pending),
                                                   ensure_ascii=True)))
        self.receiver.start()

    def join(self):
        self.client.sendMessage(Message(COMMAND_REDY,
                                        self.client.getId(),
                                        self.getId(),
                                        self.client.getKey()))
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
                pass # TODO
            elif message.command == COMMAND_SYNC:
                self.notify.debug(DEBUG_SYNC, self.getId())
                members = json.loads(message.data)
                self.__members = members
                for member in self.__members:
                    if (member in self.__pending) and (member != self.client.getId()):
                        self.__pending.remove(member)
                        self.notify.debug(DEBUG_CLIENT_CONN, member, self.getId())
            elif message.command == COMMAND_REJECT:
                if message.data in self.__pending:
                    self.notify.error(ERR_CONN_REJECT)
                else:
                    self.notify.error(ERR_BAD_HANDSHAKE, message.data)
            else:
                _data = self.getDecryptedData(message)
                self.message_queue.task_done()
                return _data

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
