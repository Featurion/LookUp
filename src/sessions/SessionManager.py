import json
from src.base import utils
from src.base.globals import SERVER_ID, COMMAND_REQ_SESSION
from src.base.globals import DEBUG_END, DEBUG_SESSION_START, DEBUG_SESSION_JOIN
from src.base.globals import DEBUG_UNAVAILABLE
from src.base.globals import DEBUG_CONNECTED_PRIVATE, DEBUG_CONNECTED_GROUP
from src.base.Datagram import Datagram
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

    def _startSession(self, tab, members):
        datagram = Datagram()
        datagram.setCommand(COMMAND_REQ_SESSION)
        datagram.setFromId(self.client.getId())
        datagram.setToId(SERVER_ID)
        datagram.addData(json.dumps(list(members),
                                    ensure_ascii=True))
        self.client.sendDatagram(datagram)

        id_ = self.client._waitForResp()
        session = Session(tab, id_, self.client, members)
        self.__sessions[id_] = session
        tab.setSession(session)
        self.notify.debug(DEBUG_SESSION_START, id_)
        session.start()

    def openSession(self, tab, members):
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
        _m.add(self.client.getId())
        self._startSession(tab, _m)

    def joinSession(self, tab, id_, members, titled_names):
        session = Session(tab, id_, self.client, set(members))
        self.__sessions[id_] = session
        tab.setSession(session)
        self.notify.debug(DEBUG_SESSION_JOIN, id_)
        session.join()

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
