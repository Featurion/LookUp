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
        self.__users = []
        self.__name2user = {}
        self.__id2user = {}

    def addClient(self, client_ai):
        self.notify.debug(DEBUG_REGISTERED, client_ai.name, client_ai.id)
        self.__users.append(client_ai)
        self.__id2user[client_ai.id] = client_ai
        self.__name2user[client_ai.name] = client_ai

    def removeClient(self, client_ai):
        self.notify.debug(DEBUG_UNREGISTERED, client_ai.name, client_ai.id)
        self.__users.remove(client_ai)
        del self.__id2user[client_ai.id]
        del self.__name2user[client_ai.name]

    def getClient(self, user_id):
        return self.__id2user.get(user_id)

    def getIdByName(self, user_name):
        user = self.__name2user.get(user_name)
        if user:
            return user.id
        else:
            return ''

    def getNameById(self, user_id):
        user = self.__id2user.get(user_id)
        if user:
            return user.name
        else:
            return ''
