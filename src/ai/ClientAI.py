import uuid
from src.ai.RequestManagerAI import RequestManagerAI
from src.ai.SessionAI import SessionAI
from src.base.globals import USER_STANDARD, USER_ADMIN
from src.base.Notifier import Notifier


class ClientAI(Notifier):

    def __init__(self, ai, socket):
        Notifier.__init__(self)
        self.ai = ai
        self.session_manager = ai.session_manager
        self.socket = socket
        self.__id = None
        self.__name = None
        self.__mode = USER_STANDARD
        self.monitored = False

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def mode(self):
        return self.__mode

    def setId(self, client_id):
        assert isinstance(client_id, str)
        self.__id = client_id

    def setName(self, name):
        assert isinstance(name, str)
        self.__name = name

    def setMode(self, mode):
        assert isinstance(mode, int)
        self.__mode = mode

    def start(self):
        self.__startManagers()

    def __startManagers(self):
        self.request_manager = RequestManagerAI(self)
        self.request_manager.start()

    def register(self, client_id, name):
        self.setId(client_id)
        self.setName(name)
        self.ai.client_manager.addClient(self) # Track client
        self.monitored = True

    def sendMessage(self, message):
        self.request_manager.sendMessage(message)

    def forwardMessage(self, message):
        self.ai.sendMessage(message)

    def getIdByName(self, user_name):
        return self.ai.getIdByName(user_name)

    def getNameById(self, user_id):
        return self.ai.getNameById(user_id)

    def generateSession(self, owner_key, owner_id, members):
        session_id = uuid.uuid4().hex
        session_ai = SessionAI(self, session_id,
                               owner_key, owner_id,
                               members)
        self.session_manager.addSession(session_ai)
        return session_id

    def stop(self):
        if self.request_manager:
            if not self.request_manager.stopping:
                self.request_manager.stop()
            self.request_manager = None
        if self.monitored:
            self.ai.client_manager.removeClient(self) # Untrack client
        self.monitored = False
