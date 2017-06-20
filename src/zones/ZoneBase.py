import queue
import threading

from src.base.KeyHandler import KeyHandler


class ZoneBase(KeyHandler):

    def __init__(self, client, zone_id, members):
        KeyHandler.__init__(self)
        self.client = client
        self.__id = zone_id
        self.__members = members
        self.is_running = False
        self.success = [None, None]
        self.setupThreads()
        self.start()

    def start(self):
        self.is_running = True
        self.__sender.start()
        self.__receiver.start()

    def setupThreads(self):
        """Setup messaging threads"""
        self.__inbox = queue.Queue()
        self.__outbox = queue.Queue()
        self.__sender = threading.Thread(target=self.send, daemon=True)
        self.__receiver = threading.Thread(target=self.recv, daemon=True)

    def getId(self):
        """Getter for Node ID"""
        return self.__id

    def getMembers(self):
        """Getter for zone members"""
        return self.__members

    def getRunning(self):
        """Getter for Node status"""
        return self.is_running

    def setRunning(self, running):
        """Setter for Node status"""
        self.is_running = running

    def getSendingSuccess(self):
        """Getter for sending-thread's status"""
        return bool(self.success[0])

    def __setSendingSuccess(self, success: bool):
        """Setter for sending-thread's status"""
        self.success[0] = success

    def getReceivingSuccess(self):
        """Getter for receiving-thread's status"""
        return bool(self.success[1])

    def __setReceivingSuccess(self, success: bool):
        """Setter for receiving-thread's status"""
        self.success[1] = success

    def recvDatagram(self, datagram):
        self.__inbox.put(datagram)

    def sendDatagram(self, datagram):
        self.__outbox.put(datagram)

    def send(self):
        while self.getRunning():
            try:
                datagram = self.__outbox.get()
                Node.sendDatagram(self.client, datagram)
            except Exception as e:
                self.notify.error('ZoneError', str(e))

            self.__setSendingSuccess(False)
            return

        self.__setSendingSuccess(True)

    def recv(self):
        while self.getRunning():
            try:
                datagram = self.__inbox.get()
                self._recv(datagram)
                continue
            except Exception as e:
                self.notify.error('ZoneError', str(e))

            self.__setReceivingSuccess(False)
            return

        self.__setReceivingSuccess(True)
