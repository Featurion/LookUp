from src.base.globals import INVALID_NAME_EMPTY, INVALID_NAME_CONTENT
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

    def start(self):
        pass # TODO

    def stop(self):
        pass # TODO

    def addClient(self, client_ai):
        self.notify.info(DEBUG_REGISTERED, client_ai.name, client_ai.id)

    def removeClient(self, client_ai):
        self.notify.info(DEBUG_UNREGISTERED, client_ai.name, client_ai.id)
