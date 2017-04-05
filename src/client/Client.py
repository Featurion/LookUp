from threading import Thread
import uuid
from src.base import utils
from src.base.globals import SERVER_ID
from src.base.globals import COMMAND_END, COMMAND_REQ_ID, COMMAND_REQ_NAME
from src.base.globals import DEBUG_CLIENT_START
from src.base.globals import DEBUG_SYNC_WAIT, DEBUG_SYNC_DONE
from src.base.globals import DEBUG_CLIENT_CONNECTED, DEBUG_CLIENT_DISCONNECTED
from src.base.globals import ERR_SESSION_END
from src.base.Message import Message
from src.base.Notifier import Notifier
from src.base.SocketHandler import SocketHandler
from src.client.RequestManager import RequestManager
from src.crypto.CryptoHandler import CryptoHandler
from src.gui.ClientUI import ClientUI
from src.sessions.SessionManager import SessionManager


class Client(Notifier):

    def __init__(self, addr, port, name=None):
        Notifier.__init__(self)
        self.__name = name
        self._resp = None
        self.socket = SocketHandler(addr, port)
        self.__id = uuid.uuid4().hex
        self.key_handler = CryptoHandler()
        self.key_handler.generateDHKey()
        self.pub_key = str(self.key_handler.getDHPubKey())
        self.request_manager = RequestManager(self)
        self.session_manager = SessionManager(self)
        self.ui = ClientUI(self)

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    def setName(self, name):
        self.__name = name

    def start(self):
        self.notify.info(DEBUG_CLIENT_START)
        self.request_manager.start()
        self.notify.info(DEBUG_CLIENT_CONNECTED)
        self.request_manager.sendProtocolVersion()
        self.session_manager.start()
        self.ui.start()

    def register(self, name): # TODO: hook to UI
        assert isinstance(name, str)
        if utils.isNameInvalid(name):
            pass # TODO: callback invalid name
        else:
            self.setName(name)
            self.request_manager.sendName(name)

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

    def getIdByName(self, user_name):
        self.sendMessage(Message(COMMAND_REQ_ID, self.id, SERVER_ID, user_name))
        return self._waitForResp()

    def getNameById(self, user_id):
        self.sendMessage(Message(COMMAND_REQ_NAME, self.id, SERVER_ID, user_id))
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
