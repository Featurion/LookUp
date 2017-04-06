from src.base.globals import INVALID_EMPTY_NAME, INVALID_NAME_CONTENT
from src.base.globals import INVALID_NAME_LENGTH, VALID_NAME, MAX_NAME_LENGTH
from src.base.globals import DEBUG_REGISTERED, DEBUG_UNREGISTERED
from src.base.Notifier import Notifier

class ClientManagerAI(Notifier):

    @staticmethod
    def isNameInvalid(name):
        assert isinstance(name, str)
        if not name:
            return INVALID_NAME_EMPTY
        elif not name.isalnum():
            return INVALID_NAME_CONTENT
        elif len(name) > MAX_NAME_LENGTH:
            return INVALID_NAME_LENGTH
        else:
            return VALID_NAME

    def __init__(self, ai):
        Notifier.__init__(self)
        self.ai = ai
        self.__clients = []
        self.__name2client = {}
        self.__id2client = {}

    def getClients(self):
        return self.__clients

    def getClientById(self, id_):
        return self.__id2client.get(id_)

    def getClientByName(self, name):
        return self.__name2client.get(name)

    def addClient(self, client_ai):
        self.notify.debug(DEBUG_REGISTERED,
                         client_ai.getName(),
                         client_ai.getId())
        self.__clients.append(client_ai)
        self.__id2client[client_ai.getId()] = client_ai
        self.__name2client[client_ai.getName()] = client_ai

    def removeClient(self, client_ai):
        self.notify.debug(DEBUG_UNREGISTERED,
                         client_ai.getName(),
                         client_ai.getId())
        self.__clients.remove(client_ai)
        del self.__id2client[client_ai.getId()]
        del self.__name2client[client_ai.getName()]

    def getClientIdByName(self, name):
        client_ai = self.__name2client.get(name)
        if client_ai:
            return client_ai.getId()
        else:
            return ''

    def getClientNameById(self, id_):
        client_ai = self.__id2client.get(id_)
        if client_ai:
            return client_ai.getName()
        else:
            return ''