import json
from src.base import utils
from src.base.globals import SERVER_ID, COMMAND_REQ_SESSION
from src.base.globals import DEBUG_END, DEBUG_SESSION_START, DEBUG_SESSION_JOIN
from src.base.globals import DEBUG_UNAVAILABLE
from src.base.globals import DEBUG_CONNECTED_PRIVATE, DEBUG_CONNECTED_GROUP
from src.base.Message import Message
from src.base.Notifier import Notifier
from src.sessions.Session import Session

class SessionManager(Notifier):

    def __init__(self, client):
        Notifier.__init__(self)
        self.client = client
        self.__sessions = {}

    def getSessions(self):
        return self.__sessions.items()

    def getSessionById(self, id_):
        return self.__sessions.get(id_)

    def getSessionByMembers(self, members):
        for id_, session in self.getSessions():
            if session.getMembers() == members:
                return self.getSessionById(id_)
        return None

    def start(self):
        pass # TODO

    def _startSession(self, members):
        self.client.sendMessage(Message(COMMAND_REQ_SESSION,
                                        self.client.getId(), SERVER_ID,
                                        json.dumps([self.client.getKey(),
                                                    self.client.getId(),
                                                    list(members)],
                                                   ensure_ascii=True)))
        id_ = self.client._waitForResp()
        session = Session(id_, self.client, members)
        self.__sessions[id_] = session
        self.notify.debug(DEBUG_SESSION_START, id_)
        session.start()

    def openSession(self, members):
        for id_, session in self.getSessions():
            if session.getMembers() == members:
                self.notify.debug(DEBUG_CONNECTED, session.getId())
                # TODO: hook back to UI
                return
        _m = set()
        for name in members:
            id_ = self.client.getClientIdByName(name)
            if id_ == '':
                self.notify.debug(DEBUG_UNAVAILABLE, name)
            else:
                _m.add(id_)
        self._startSession(_m)

    def joinSession(self, id_, members, titled_names):
        session = Session(id_, self.client, set(members))
        self.__sessions[id_] = session
        self.notify.debug(DEBUG_SESSION_JOIN, id_)
        session.join()

        tab = self.client.ui.window.addNewTab(titled_names)
        tab.widget_stack.widget(1).setConnectingToName(titled_names)
        tab.widget_stack.setCurrentIndex(1)

    def closeSession(self, id_):
        session = self.__sessions.get(id_)
        if session:
            session.stop()
            del self.__sessions[id_]
        else:
            pass # TODO: error; should not happen

    def stop(self):
        for id_, session in self.getSessions():
            session.stop()
            self.notify.debug(DEBUG_END, id_)
        self.__sessions.clear()
