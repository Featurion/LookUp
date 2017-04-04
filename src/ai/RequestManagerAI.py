import json
import queue
from threading import Event, Thread
from src.ai.ClientManagerAI import ClientManagerAI
from src.base import utils
from src.base.globals import PROTOCOL_VERSION, SERVER_ID, INVALID_COMMAND
from src.base.globals import COMMAND_END, COMMAND_REQ_ID, COMMAND_REQ_NAME
from src.base.globals import COMMAND_REQ_SESSION, COMMAND_HELO, COMMAND_REDY
from src.base.globals import COMMAND_VERSION, COMMAND_REGISTER, COMMAND_ERR
from src.base.globals import COMMAND_RELAY, RELAY_COMMANDS, SESSION_COMMANDS
from src.base.globals import DEBUG_END, DEBUG_RECV_PROTOCOL_VERION
from src.base.globals import DEBUG_SEND_STOP, DEBUG_RECV_STOP, DEBUG_CONN_CLOSED
from src.base.globals import DEBUG_DISCONNECT_WAIT
from src.base.globals import ERR_SEND, ERR_RECV, ERR_MISSING_FIELD, RECV_ERROR
from src.base.globals import ERR_CLIENT_UNREGISTERED
from src.base.globals import NetworkError
from src.base.Message import Message
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

    def sendMessage(self, message):
        self.outbox.put(message)

    def __receiveProtocolVersion(self):
        try:
            data = self.socket.recv()
            if data:
                message = Message.fromJson(data)
            else:
                self.receiving = False
                self.__stop()
                return
        except KeyError:
            self.__handleError(MALFORMED_MESSAGE, ERR_MISSING_FIELD)
            return
        if message.command != COMMAND_VERSION:
            self.__handleError(INVALID_COMMAND,
                               ERR_EXPECTED_VERSION,
                               message.command,
                               COMMAND_VERSION)
            return
        elif message.data != PROTOCOL_VERSION:
            self.__handleError(PROTOCOL_VERSION_MISMATCH, ERR_PROTOCOL_MISMATCH)
            return
        else:
            self.notify.info(DEBUG_RECV_PROTOCOL_VERION, message.from_id)

    def __receiveName(self):
        try:
            data = self.socket.recv()
            if data:
                message = Message.fromJson(data)
            else:
                self.receiving = False
                self.__stop()
                return
        except KeyError:
            self.__handleError(MALFORMED_MESSAGE, ERR_MISSING_FIELD)
            return
        if message.command != COMMAND_REGISTER:
            self.__handleError(INVALID_COMMAND,
                               ERR_CLIENT_UNREGISTERED,
                               message.from_id)
            return
        elif utils.isNameInvalid(message.data):
            self.__handleError(INVALID_NAME,
                               ERR_INVALID_NAME,
                               message.from_id)
            return
        else:
            self.ai.register(message.from_id, message.data)

    def __handleError(self, code, msg, *args):
        self.sendMessage(Message(COMMAND_ERR, err=code))
        self.notify.error(msg, *args)
        self.__stop()

    def _send(self):
        while self.socket and self.socket.connected:
            try:
                message = self.outbox.get(timeout=1)
            except queue.Empty:
                continue # no messages pending
            try:
                self.socket.send(message.toJson())
            except Exception as e:
                if message.to_id != message.from_id:
                    self.notify.error(ERR_SEND, message.to_id, message.from_id)
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
                        message = Message.fromJson(data)
                    except KeyError:
                        self.__handleError(MALFORMED_MESSAGE, ERR_MISSING_FIELD)
                        break
                    if message.command == COMMAND_END:
                        if message.to_id == SERVER_ID:
                            self.receiving = False
                            self.__stop()
                            return
                        else:
                            self.ai.forwardMessage(message)
                            self.notify.info(DEBUG_END, message.to_id)
                    elif message.command in RELAY_COMMANDS:
                        try:
                            if message.command == COMMAND_REQ_ID:
                                message.data = self.ai.getIdByName(message.data)
                            elif message.command == COMMAND_REQ_NAME:
                                message.data = self.ai.getNameById(message.data)
                            elif message.command == COMMAND_REQ_SESSION:
                                members = json.loads(message.data)
                                message.data = self.ai.generateSession(members)
                            else:
                                message.data = ''
                        except:
                            message.data = ''
                        finally:
                            message.command = COMMAND_RELAY
                            message.to_id = message.from_id
                            message.from_id = SERVER_ID
                            self.sendMessage(message)
                    elif message.command in SESSION_COMMANDS:
                        if message.command == COMMAND_HELO:
                            partners = json.loads(message.to_id)
                            message.data = json.dumps([
                                [
                                    message.data,
                                    self.ai.getNameById(message.data)
                                ],
                                [
                                    partners,
                                    [self.ai.getNameById(i) for i in partners]
                                ]
                            ])
                            for partner in partners:
                                message.to_id = partner
                                self.ai.forwardMessage(message)
                        elif message.command == COMMAND_REDY:
                            session_manager = self.ai.session_manager
                            session = session_manager.getSession(message.to_id)
                            session.addMember(message.from_id)
                            session.sync()
                    else:
                        self.__handleError(INVALID_COMMAND,
                                           ERR_INVALID_COMMAND,
                                           message.from_id)
                        break
                else:
                    self.notify.warning(DEBUG_CONN_CLOSED)
            except NetworkError as e:
                if e.err != CONN_CLOSED:
                    self.__handleError(RECV_ERROR, ERR_RECV)
                else:
                    self.__stop()
                break
        self.receiving = False
