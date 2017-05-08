import json
import queue
from threading import Event, Thread
from src.base.globals import SERVER_ID, PROTOCOL_VERSION, CONN_CLOSED
from src.base.globals import COMMAND_VERSION, COMMAND_REGISTER, COMMAND_END
from src.base.globals import COMMAND_RELAY, RELAY_COMMANDS, SESSION_COMMANDS
from src.base.globals import REQ_COMMANDS
from src.base.globals import COMMAND_HELO, COMMAND_REDY, COMMAND_REJECT
from src.base.globals import DEBUG_SERVER_COMMAND, DEBUG_END, DEBUG_END_REQ
from src.base.globals import DEBUG_DISCONNECT_WAIT, DEBUG_SERVER_CONN_CLOSED
from src.base.globals import DEBUG_SEND_STOP, DEBUG_RECV_STOP, DEBUG_HELO
from src.base.globals import ERR_INVALID_SEND, ERR_INVALID_RECV, ERR_SEND
from src.base.globals import NetworkError
from src.base.Datagram import Datagram
from src.base.Notifier import Notifier


class RequestManager(Notifier):

    def __init__(self, client):
        Notifier.__init__(self)
        self.client = client
        self.outbox = queue.Queue()
        self.send_handler = Thread(target=self._send, daemon=True)
        self.recv_handler = Thread(target=self._recv, daemon=True)
        self.sending = False
        self.receiving = False

    def start(self):
        self.socket = self.client.socket
        self.send_handler.start()
        self.sending = True
        self.recv_handler.start()
        self.receiving = True

    def stop(self):
        self.__sendServerCommand(COMMAND_END)
        self.__waitForDisconnect()

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

    def sendDatagram(self, datagram):
        assert isinstance(datagram, Datagram)
        self.outbox.put(datagram)

    def __sendServerCommand(self, command, data=None):
        self.notify.debug(DEBUG_SERVER_COMMAND, command)

        datagram = Datagram()
        datagram.setCommand(command)
        datagram.setFromId(self.client.getId())
        datagram.setToId(SERVER_ID)
        datagram.addData(data)

        self.sendDatagram(datagram)

    def sendProtocolVersion(self):
        self.__sendServerCommand(COMMAND_VERSION, PROTOCOL_VERSION)

    def sendName(self, name):
        self.__sendServerCommand(COMMAND_REGISTER, name)

    def _send(self):
        while self.socket and self.socket.connected:
            try:
                datagram = self.outbox.get(timeout=1)
                command = datagram.getCommand()
                from_id = datagram.getFromId()
                to_id = datagram.getToId()
            except:
                continue # no datagrams pending
            try:
                if command == COMMAND_END:
                    if to_id == SERVER_ID:
                        self.socket.send(datagram.toJson())
                        self.__stop()
                        break
                    else:
                        self.client.closeSession(to_id)
                    self.notify.debug(DEBUG_END, to_id)
                elif command in RELAY_COMMANDS + REQ_COMMANDS + SESSION_COMMANDS:
                    self.socket.send(datagram.toJson())
                else:
                    self.notify.warning(ERR_INVALID_SEND, to_id)
            except NetworkError as e:
                if e.err != CONN_CLOSED:
                    self.notify.error(ERR_SEND, to_id, from_id)
                self.__stop()
                break
            finally:
                self.outbox.task_done()
        self.sending = False

    def _recv(self):
        while self.socket and self.socket.connected:
            data = self.socket.recv()
            if data:
                datagram = Datagram.fromJson(data)
                command = datagram.getCommand()
                data = datagram.getData()
                from_id = datagram.getFromId()
                to_id = datagram.getToId()
                if command == COMMAND_RELAY:
                    self.client.resp(data)
                elif command == COMMAND_END:
                    if from_id == SERVER_ID:
                        self.__stop()
                        break
                    else:
                        self.notify.debug(DEBUG_END_REQ, from_id)
                        self.client.closeSession(from_id)
                elif command in SESSION_COMMANDS:
                    if command == COMMAND_HELO:
                        id_, owner, members = json.loads(data)
                        self.notify.debug(DEBUG_HELO, owner[1])
                        members[0].remove(self.client.getId())
                        members[1].remove(self.client.getName())
                        window = self.client.ui.window
                        window.new_client_signal.emit(id_, owner, members)
                    else:
                        _sm = self.client.session_manager
                        session = _sm.getSessionById(from_id)
                        session.postDatagram(datagram)
                else:
                    self.notify.error(ERR_INVALID_RECV, from_id)
                    break
            else: # The server closed the connection unexpectedly (this shouldn't happen)
                # TODO Zach: UI error callback here
                self.notify.info(DEBUG_SERVER_CONN_CLOSED)
                self.socket.disconnect()
        self.receiving = False
