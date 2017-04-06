import sys
from threading import Thread
import uuid
from src.base.globals import SERVER_ID, COMMAND_REJECT
from src.base.globals import COMMAND_END, COMMAND_REQ_ID, COMMAND_REQ_NAME
from src.base.globals import DEBUG_CLIENT_START, DEBUG_REJECT
from src.base.globals import DEBUG_SYNC_WAIT, DEBUG_SYNC_DONE
from src.base.globals import DEBUG_CLIENT_CONNECTED, DEBUG_CLIENT_DISCONNECTED
from src.base.globals import ERR_SESSION_END
from src.base.Message import Message
from src.base.Notifier import Notifier
from src.base.SocketHandler import SocketHandler
from src.client.RequestManager import RequestManager
from src.crypto.KeyHandler import KeyHandler
from src.gui.ClientUI import ClientUI
from src.sessions.SessionManager import SessionManager


class Client(Notifier):

    def __init__(self, addr, port, name=None):
        Notifier.__init__(self)
        self.__name = name
        self._resp = None
        self.socket = SocketHandler(addr, port)
        self.__id = uuid.uuid4().hex
        self.key_handler = KeyHandler()
        self.key_handler.generateDHKey()
        self.__pub_key = str(self.key_handler.getDHPubKey())
        self.request_manager = RequestManager(self)
        self.session_manager = SessionManager(self)
        self.ui = ClientUI(self)

    def getId(self):
        return self.__id

    def getKey(self):
        return self.__pub_key

    def getName(self):
        return self.__name

    def setName(self, name):
        self.__name = name

    def start(self):
        self.notify.info(DEBUG_CLIENT_START)
        self.request_manager.start()
        self.notify.info(DEBUG_CLIENT_CONNECTED)
        self.request_manager.sendProtocolVersion()
        self.session_manager.start()
        while not self.ui.running:
            self.ui.start()

    def register(self, name): # TODO: hook to UI
        assert isinstance(name, str)
        self.setName(name)
        self.request_manager.sendName(name)
        if self._waitForResp():
            raise LookupError()

    def openSession(self, names): # TODO: hook to UI
        if names:
            self.session_manager.openSession(names)
        else: # no usernames provided
            pass # TODO: hook to UI

    def closeSession(self, session_id): # TODO: hook to UI
        self.session_manager.closeSession(session_id)

    def _waitForResp(self):
        self.notify.debug(DEBUG_SYNC_WAIT)
        while self._resp is None:
            pass
        resp = self._resp
        self._resp = None
        return resp

    def sendMessage(self, message):
        self.request_manager.sendMessage(message)

    def sendRejectMessage(self, id_):
        self.notify.debug(DEBUG_REJECT, id_)
        self.sendMessage(Message(COMMAND_REJECT,
                                 self.getId(), id_,
                                 self.getName()))

    def getClientIdByName(self, name):
        self.sendMessage(Message(COMMAND_REQ_ID,
                                 self.getId(), SERVER_ID,
                                 name))
        return self._waitForResp()

    def getClientNameById(self, id_):
        self.sendMessage(Message(COMMAND_REQ_NAME,
                                 self.getId(), SERVER_ID,
                                 id_))
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
