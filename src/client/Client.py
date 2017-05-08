import sys
import ssl
import socket
from threading import Thread
import uuid
from src.base.globals import SERVER_ID, COMMAND_REJECT
from src.base.globals import COMMAND_END, COMMAND_REQ_ID, COMMAND_REQ_NAME
from src.base.globals import DEBUG_CLIENT_START, DEBUG_REJECT
from src.base.globals import DEBUG_SYNC_WAIT, DEBUG_SYNC_DONE
from src.base.globals import DEBUG_CLIENT_CONNECTED, DEBUG_CLIENT_DISCONNECTED
from src.base.globals import ERR_SESSION_END, ERR_CLIENT_START
from src.base.Datagram import Datagram
from src.base.Notifier import Notifier
from src.base.SocketHandler import SocketHandler
from src.client.RequestManager import RequestManager
from src.crypto.KeyHandler import KeyHandler
from src.gui.ClientUI import ClientUI
from src.sessions.SessionManager import SessionManager


class Client(Notifier):

    def __init__(self, addr, port, name=None):
        Notifier.__init__(self)
        self._addr = addr
        self._port = port
        self.__name = name
        self._resp = None
        self.socket = None
        self.__id = uuid.uuid4().hex
        self.request_manager = RequestManager(self)
        self.session_manager = SessionManager(self)
        self.ui = ClientUI(self)

    def getId(self):
        return self.__id

    def getName(self):
        return self.__name

    def setName(self, name):
        self.__name = name

    def start(self):
        self._connect()
        while True:
            self.socket = SocketHandler(self._addr, self._port, self.socket)
            self.socket.connect()
            self.socket.initiateHandshake()
            if self.socket.handshake_done:
                break
        self.request_manager.start()
        self.notify.info(DEBUG_CLIENT_CONNECTED)
        self.request_manager.sendProtocolVersion()
        self.session_manager.start()
        while not self.ui.running:
            self.ui.start()

    def _connect(self):
        try:
            self.notify.info(DEBUG_CLIENT_START)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket = ssl.wrap_socket(self.socket, ssl_version=ssl.PROTOCOL_TLSv1_2, ciphers='ECDHE-RSA-AES256-GCM-SHA384')
        except:
            self.notify.critical(ERR_CLIENT_START)

    def register(self, name):
        assert isinstance(name, str)
        self.setName(name)
        self.request_manager.sendName(name)
        if self._waitForResp():
            raise LookupError()

    def openSession(self, tab, names):
        if names:
            self.session_manager.openSession(tab, names)
        else: # no usernames provided
            pass

    def closeSession(self, session_id): # TODO: finish implementation
        self.session_manager.closeSession(session_id)

    def _waitForResp(self):
        self.notify.debug(DEBUG_SYNC_WAIT)
        while self._resp is None:
            pass
        resp = self._resp
        self._resp = None
        return resp

    def sendDatagram(self, datagram):
        self.request_manager.sendDatagram(datagram)

    def sendRejectDatagram(self, id_):
        self.notify.debug(DEBUG_REJECT, id_)

        datagram = Datagram()
        datagram.setCommand(COMMAND_REJECT)
        datagram.setFromId(self.getId())
        datagram.setToId(id_)
        datagram.addData(self.getName())
        self.sendDatagram(datagram)

    def getClientIdByName(self, name):
        datagram = Datagram()
        datagram.setCommand(COMMAND_REQ_ID)
        datagram.setFromId(self.getId())
        datagram.setToId(SERVER_ID)
        datagram.addData(name)
        self.sendDatagram(datagram)
        return self._waitForResp()

    def getClientNameById(self, id_):
        datagram = Datagram()
        datagram.setCommand(COMMAND_REQ_NAME)
        datagram.setFromId(self.getId())
        datagram.setToId(SERVER_ID)
        datagram.addData(id_)
        self.sendDatagram(datagram)
        return self._waitForResp()

    def resp(self, data):
        self.notify.debug(DEBUG_SYNC_DONE)
        self._resp = data

    def stop(self):
        if self.session_manager:
            self.session_manager.stop()
            self.session_manager = None
        if self.request_manager:
            self.request_manager.stop()
            self.notify.info(DEBUG_CLIENT_DISCONNECTED)
            self.request_manager = None
        if self.socket:
            if self.socket.connected:
                self.socket.disconnect()
            self.socket = None
        if self.ui:
            self.ui.stop()
            self.ui = None
        sys.exit(0)
