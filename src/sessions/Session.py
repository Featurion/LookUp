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
from src.base.Datagram import Datagram
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

        self.datagram_queue = queue.Queue()
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
        self.sendDatagram(COMMAND_HELO, str(self.getPubKey()))
        self.receiver.start()

    def join(self):
        self.sendDatagram(COMMAND_REDY, str(self.getPubKey()))
        self.receiver.start()

    def stop(self): # TODO
        pass

    def __receiveMessages(self):
        while True:
            datagram = self.datagram_queue.get()
            data = datagram.getData()
            command = datagram.getCommand()
            from_id = datagram.getFromId()
            to_id = datagram.getToId()
            if command == COMMAND_END:
                self.datagram_queue.task_done()
                return # TODO
            elif command == COMMAND_REDY:
                self.notify.debug(DEBUG_REDY, from_id)
                self.setAltPubKey(int(data))
                self.setEncrypted(True)
                self.getTab().widget_stack.setCurrentIndex(2)
                self.__notifyReady()
            elif command == COMMAND_REJECT:
                self.notify.debug(DEBUG_CLIENT_REJECT,
                                  data,
                                  to_id)
            elif command == COMMAND_SYNC:
                self.notify.debug(DEBUG_SYNC, self.getId())

                members, pending = json.loads(data)
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
                        self.notify.error(ERR_BAD_HANDSHAKE, data)
                        return
                self.setPendingMembers(set(pending))
            elif command == COMMAND_MSG:
                if self.getEncrypted():
                    new_data = self.__getDecryptedData(datagram)
                else:
                    new_data = data

                new_data, timestamp = utils.parseTimestampFromMessage(new_data)
                new_data = new_data.format(utils.formatTimestamp(timestamp))

                self.getTab().new_message_signal.emit(new_data, timestamp)
            elif command == COMMAND_CLIENT_MSG:
                new_data = MSG_TEMPLATE.format('#000000',
                                               '',
                                               'server',
                                               data)
                self.getTab().new_message_signal.emit(new_data,
                                                      utils.getTimestamp())
            else:
                pass # unexpected command

    def __notifyReady(self):
        for name in self.getMemberNames():
            if name == self.client.getName():
                continue
            else:
                datagram = Datagram()
                datagram.setCommand(COMMAND_CLIENT_MSG)
                datagram.setFromId(self.getId())
                datagram.setToId(self.client.getId())
                datagram.addData(CLIENT_JOINED.format(name))
                self.datagram_queue.put(datagram)

    def __verifyHmac(self, hmac, data):
        generated_hmac = self.key_handler.generateHmac(data)
        return utils.secureStrCmp(generated_hmac, hmac)

    def __getDecryptedData(self, datagram):
        _kh = self.key_handler
        _kh.computeDHSecret(self.getAltPubKey())

        enc_data = datagram.getData(True)
        hmac = datagram.getHmac(True)

        if self.__verifyHmac(hmac, enc_data):
            try:
                return _kh.aesDecrypt(enc_data).decode()
            except:
                self.notify.error(ERR_DECRYPT_FAILURE)
        else:
            self.notify.error(ERR_INVALID_HMAC)

    def sendDatagram(self, command, data=None):
        datagram = Datagram()
        datagram.setCommand(command)
        datagram.setFromId(self.client.getId())
        datagram.setToId(self.getId())

        if (data is not None) and self.getEncrypted():
            _kh = self.key_handler
            _kh.computeDHSecret(self.getAltPubKey())

            enc_data = _kh.aesEncrypt(data)
            hmac = _kh.generateHmac(enc_data)

            datagram.addData(enc_data, True)
            datagram.addHmac(hmac, True)
        elif data is not None:
            datagram.addData(data)
        else:
            return

        self.client.sendDatagram(datagram)

    def sendChatMessage(self, data):
        self.sendDatagram(COMMAND_MSG, data)

    def postDatagram(self, datagram):
        self.datagram_queue.put(datagram)
