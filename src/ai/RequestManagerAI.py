import base64
import json
import queue
from threading import Event, Thread
from src.ai.ClientManagerAI import ClientManagerAI
from src.base import utils
from src.base.globals import PROTOCOL_VERSION, SERVER_ID, INVALID_COMMAND
from src.base.globals import COMMAND_END, COMMAND_REQ_ID, COMMAND_REQ_NAME
from src.base.globals import COMMAND_REQ_SESSION, COMMAND_HELO, COMMAND_REDY
from src.base.globals import COMMAND_VERSION, COMMAND_REGISTER, COMMAND_ERR
from src.base.globals import COMMAND_RELAY, REQ_COMMANDS, SESSION_COMMANDS
from src.base.globals import DEBUG_END, DEBUG_RECV_PROTOCOL_VERION
from src.base.globals import DEBUG_SEND_STOP, DEBUG_RECV_STOP, DEBUG_CLIENT_CONN_CLOSED
from src.base.globals import DEBUG_DISCONNECT_WAIT
from src.base.globals import ERR_SEND, ERR_RECV, ERR_MISSING_FIELD, RECV_ERROR
from src.base.globals import ERR_CLIENT_UNREGISTERED
from src.base.globals import NetworkError
from src.base.Datagram import Datagram
from src.base.Notifier import Notifier
from src.base.SocketHandler import SocketHandler


class RequestManagerAI(Notifier):

    def __init__(self, client_ai):
        Notifier.__init__(self)
        self.ai = client_ai
        self.socket = client_ai.socket
        self.outbox = queue.Queue()
        self.send_handler = Thread(target=self._send, daemon=True)
        self.recv_handler = Thread(target=self._recv, daemon=True)
        self.sending = False
        self.receiving = False

    def start(self):
        self.send_handler.start()
        self.sending = True
        self.recv_handler.start()
        self.receiving = True
        self.stopping = False

    def stop(self):
        self.stopping = True
        self.__waitForDisconnect()
        del self.stopping

    def __stop(self):
        if self.socket and self.socket.connected:
            self.socket.disconnect()
            self.socket = None
        self.ai.stop()

    def __waitForDisconnect(self):
        self.notify.debug(DEBUG_DISCONNECT_WAIT)
        self.__waitCleanupSend()
        self.__waitCleanupRecv()
        while self.socket and self.socket.connected:
            pass

    def __waitCleanupSend(self):
        while self.sending:
            pass
        self.send_handler = None
        self.notify.debug(DEBUG_SEND_STOP)

    def __waitCleanupRecv(self):
        while self.receiving:
            pass
        self.recv_handler = None
        self.notify.debug(DEBUG_RECV_STOP)

    def sendDatagram(self, datagram):
        self.outbox.put(datagram)

    def __receiveProtocolVersion(self):
        try:
            data = self.socket.recv()
            if data:
                datagram = Datagram.fromJson(data)
                data = datagram.getData()
                command = datagram.getCommand()
                from_id = datagram.getFromId()
            else:
                self.receiving = False
                self.__stop()
                return
        except KeyError:
            self.__handleError(MALFORMED_DATAGRAM, ERR_MISSING_FIELD)
            return
        if command != COMMAND_VERSION:
            self.__handleError(INVALID_COMMAND,
                               ERR_EXPECTED_VERSION,
                               command,
                               COMMAND_VERSION)
            return
        elif data != PROTOCOL_VERSION:
            self.__handleError(PROTOCOL_VERSION_MISMATCH, ERR_PROTOCOL_MISMATCH)
            return
        else:
            self.notify.debug(DEBUG_RECV_PROTOCOL_VERION, from_id)

    def __receiveName(self):
        try:
            data = self.socket.recv()
            if data:
                datagram = Datagram.fromJson(data)
                command = datagram.getCommand()
                data = datagram.getData()
                from_id = datagram.getFromId()
            else:
                self.receiving = False
                self.__stop()
                return
        except KeyError:
            self.__handleError(MALFORMED_DATAGRAM, ERR_MISSING_FIELD)
            return
        if command != COMMAND_REGISTER:
            self.__handleError(INVALID_COMMAND,
                               ERR_CLIENT_UNREGISTERED,
                               from_id)
            return
        elif utils.isNameInvalid(data):
            self.__handleError(INVALID_NAME,
                               ERR_INVALID_NAME,
                               from_id)
            return
        else:
            _cm = self.ai.server.client_manager

            _dg = Datagram()
            _dg.setCommand(COMMAND_RELAY)
            _dg.setToId(datagram.getFromId())
            _dg.setFromId(SERVER_ID)
            if not _cm.getClientIdByName(data):
                self.ai.register(from_id, data)
            else:
                _dg.setData(None)
            self.sendDatagram(_dg)

    def __handleError(self, code, msg, *args):
        datagram = Datagram()
        datagram.setCommand(COMMAND_ERR)
        datagram.setErr(code)
        self.sendDatagram(datagram)
        self.notify.error(msg, *args)
        self.__stop()

    def _send(self):
        while self.socket and self.socket.connected:
            try:
                datagram = self.outbox.get(timeout=1)
                from_id = datagram.getFromId()
                to_id = datagram.getToId()
            except queue.Empty:
                continue # no datagrams pending
            try:
                self.socket.send(datagram.toJson())
            except Exception as e:
                if to_id != from_id:
                    self.notify.error(ERR_SEND, to_id, from_id)
                break
            finally:
                self.outbox.task_done()
        self.sending = False

    def _recv(self):
        self.__receiveProtocolVersion()
        self.__receiveName()
        while self.socket and self.socket.connected:
            try:
                data = self.socket.recv()
                if data:
                    try:
                        datagram = Datagram.fromJson(data)
                        command = datagram.getCommand()
                        data = datagram.getData()
                        from_id = datagram.getFromId()
                        to_id = datagram.getToId()
                    except KeyError:
                        self.__handleError(MALFORMED_DATAGRAM, ERR_MISSING_FIELD)
                        break
                    if command == COMMAND_END:
                        if to_id == SERVER_ID:
                            self.receiving = False
                            self.__stop()
                            return
                        else:
                            self.ai.server.sendDatagram(datagram)
                            self.notify.debug(DEBUG_END, to_id)
                    elif command in REQ_COMMANDS:
                        try:
                            if command == COMMAND_REQ_ID:
                                _cm = self.ai.server.client_manager
                                data = _cm.getClientIdByName(data)
                            elif command == COMMAND_REQ_NAME:
                                _cm = self.ai.server.client_manager
                                data = _cm.getClientNameById(data)
                            elif command == COMMAND_REQ_SESSION:
                                _sm = self.ai.server.session_manager
                                members = json.loads(data)
                                data = _sm.generateSession(set(members))
                            else:
                                data = ''
                        except:
                            data = ''
                        finally:
                            _dg = Datagram()
                            _dg.setCommand(COMMAND_RELAY)
                            _dg.setFromId(to_id)
                            _dg.setToId(self.ai.getName())
                            _dg.addData(data)
                            self.sendDatagram(_dg)
                    elif command in SESSION_COMMANDS:
                        _sm = self.ai.server.session_manager
                        session = _sm.getSessionById(to_id)
                        session.postDatagram(datagram)
                    else:
                        self.__handleError(INVALID_COMMAND,
                                           ERR_INVALID_COMMAND,
                                           from_id)
                        break
                else: # client closed connection unexpectedly
                    self.notify.debug(DEBUG_CLIENT_CONN_CLOSED)
                    self.socket.disconnect()
            except NetworkError as e:
                if e.err != CONN_CLOSED:
                    self.__handleError(RECV_ERROR, ERR_RECV)
                else:
                    self.__stop()
                break
        self.receiving = False
