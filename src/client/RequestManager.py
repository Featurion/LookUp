import queue
from threading import Event, Thread
from src.base.globals import SERVER_ID, PROTOCOL_VERSION
from src.base.globals import COMMAND_VERSION, COMMAND_REGISTER, COMMAND_END
from src.base.globals import RELAY_COMMANDS
from src.base.globals import DEBUG_SERVER_COMMAND, DEBUG_END, DEBUG_END_REQ
from src.base.globals import DEBUG_DISCONNECT_WAIT, DEBUG_CONN_CLOSED
from src.base.globals import DEBUG_SEND_STOP, DEBUG_RECV_STOP
from src.base.globals import DEBUG_CLIENT_CONNECTED, DEBUG_CLIENT_DISCONNECTED
from src.base.globals import ERR_INVALID_SEND, ERR_INVALID_RECV, ERR_SEND
from src.base.globals import NetworkError
from src.base.Message import Message
from src.base.Notifier import Notifier


class RequestManager(Notifier):

    def __init__(self, client):
        Notifier.__init__(self)
        self.client = client
        self.socket = client.socket
        self.outbox = queue.Queue()
        self.send_handler = Thread(target=self._send)
        self.recv_handler = Thread(target=self._recv)
        self.sending = False
        self.receiving = False

    def start(self):
        self.socket.connect()
        self.send_handler.start()
        self.sending = True
        self.recv_handler.start()
        self.receiving = True
        self.notify.info(DEBUG_CLIENT_CONNECTED)

    def stop(self):
        self.__sendServerCommand(COMMAND_END)
        self.__waitForDisconnect()
        self.notify.info(DEBUG_CLIENT_DISCONNECTED)

    def __stop(self):
        if self.socket:
            self.socket.disconnect()
            self.socket = None

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
        assert isinstance(message, Message)
        self.outbox.put(message)

    def __sendServerCommand(self, command, data=None):
        self.notify.debug(DEBUG_SERVER_COMMAND, command)
        message = Message(command, self.client.id, SERVER_ID, data)
        self.sendMessage(message)

    def sendProtocolVersion(self):
        self.__sendServerCommand(COMMAND_VERSION, PROTOCOL_VERSION)

    def sendName(self, name):
        self.__sendServerCommand(COMMAND_REGISTER, name)

    def _send(self):
        while self.socket and self.socket.connected:
            try:
                message = self.outbox.get(timeout=1)
            except:
                continue # no messages pending
            try:
                if message.command == COMMAND_END:
                    if message.to_id == SERVER_ID:
                        self.socket.send(message.toJson())
                        self.__stop()
                        break
                    else:
                        self.client.endSession(message.to_id)
                    self.notify.debug(DEBUG_END, message.to_id)
                elif message.command in RELAY_COMMANDS:
                    self.socket.send(message.toJson())
                else:
                    self.notify.warning(ERR_INVALID_SEND, message.to_id)
            except NetworkError as e:
                if e.err != CONN_CLOSED:
                    self.notify.error(ERR_SEND, message.to_id, message.from_id)
                self.__stop()
                break
            finally:
                self.outbox.task_done()
        self.sending = False

    def _recv(self):
        while self.socket and self.socket.connected:
            data = self.socket.recv()
            if data:
                message = Message.fromJson(data)
                if message.command == COMMAND_RELAY:
                    self.client.resp(message.data)
                elif message.command == COMMAND_END:
                    self.notify.debug(DEBUG_END_REQ, message.from_id)
                    if message.from_id == SERVER_ID:
                        self.__stop()
                        break
                    else:
                        self.client.endSession(message.from_id)
                else:
                    self.notify.error(ERR_INVALID_RECV, message.from_id)
        self.receiving = False
