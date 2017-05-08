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
from src.base.Datagram import Datagram
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

        self.datagram_queue = queue.Queue()

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
            datagram = self.datagram_queue.get()
            command = datagram.getCommand()
            from_id = datagram.getFromId()
            to_id = datagram.getToId()
            data = datagram.getData()
            if command == COMMAND_END:
                self.emitDatagram(datagram)
                return
            elif command == COMMAND_HELO:
                self.__memberJoined(from_id, json.loads(data))

                _cm = self.server.client_manager
                datagram.addData(json.dumps([
                        to_id,
                        [
                            from_id,
                            _cm.getClientNameById(from_id)
                        ],
                        [
                            list(self.getPendingMembers()),
                            [_cm.getClientNameById(i) for i in self.getPendingMembers()]
                        ]
                    ]))
                for id_ in self.getPendingMembers():
                    datagram.setToId(id_)
                    self.server.sendDatagram(datagram)
            elif command == COMMAND_REDY:
                self.clientAccepted(from_id, data)
            elif command == COMMAND_REJECT:
                self.clientRejected(from_id)
            elif command == COMMAND_MSG:
                self.__transferEncryptedData(datagram)
            else:
                pass # unexpected command

    def __verifyHmac(self, hmac, data):
        generated_hmac = self.key_handler.generateHmac(data)
        return utils.secureStrCmp(generated_hmac, hmac)

    def __transferEncryptedData(self, datagram):
        _kh = self.key_handler
        _kh.computeDHSecret(self.getMemberPubKey(datagram.getFromId()))

        enc_data = datagram.getData(True)
        hmac = datagram.getHmac(True)

        if self.__verifyHmac(hmac, enc_data):
            try:
                datagram.addData(_kh.aesDecrypt(enc_data).decode())
                self.emitDatagram(datagram, self.__encryptForMember)
            except:
                self.notify.error(ERR_DECRYPT_FAILURE)
        else:
            self.notify.error(ERR_INVALID_HMAC)

    def __encryptForMember(self, id_, datagram):
        time = datagram.getTime()
        data = datagram.getData()
        from_id = datagram.getFromId()

        _cm = self.server.client_manager
        _kh = self.key_handler
        _kh.computeDHSecret(self.getMemberPubKey(id_))

        if id_ == from_id:
            src_color = '#0000CC'
        else:
            src_color = '#CC0000'

        msg = MSG_TEMPLATE.format(src_color,
                                  time,
                                  _cm.getClientNameById(from_id),
                                  data)

        enc_data = _kh.aesEncrypt(msg)
        hmac = _kh.generateHmac(enc_data)

        datagram = Datagram()
        datagram.setCommand(COMMAND_MSG)
        datagram.setFromId(self.getId())
        datagram.setToId(id_)
        datagram.addData(enc_data, True)
        datagram.addHmac(hmac, True)
        return datagram

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

    def emitDatagram(self, datagram, modFunc=None, exclude=[]):
        for id_ in self.getMemberIds():
            if id_ in exclude:
                continue
            elif modFunc is not None:
                self.server.sendDatagram(modFunc(id_, datagram))
            else:
                datagram.setFromId(self.getId())
                datagram.setToId(id_)
                self.server.sendDatagram(datagram)

    def sessionReady(self):
        datagram = Datagram()
        datagram.setCommand(COMMAND_REDY)
        datagram.addData(self.getPubKey())
        self.emitDatagram(datagram)

    def sync(self):
        _cm = self.server.client_manager
        datagram = Datagram()
        datagram.setCommand(COMMAND_SYNC)
        datagram.addData(json.dumps([list(zip(self.getMemberIds(),
                                              self.getMemberNames())),
                                     list(self.getPendingMembers())]))
        self.emitDatagram(datagram)

        if (len(self.getMembers()) > 1) and not self.getPendingMembers():
            self.sessionReady()
        elif self.getPendingMembers():
            pass # still pending
        else:
            datagram = Datagram()
            datagram.setCommand(COMMAND_END)
            datagram.setFromId(self.getId())
            self.postDatagram(datagram)
            self.server.session_manager.removeSession(self)

    def postDatagram(self, datagram):
        self.datagram_queue.put(datagram)
