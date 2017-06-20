import queue
import threading

from src.base import utils
from src.base.KeyHandler import KeyHandler


class Node(KeyHandler):

    def __init__(self):
        KeyHandler.__init__(self)
        self.__id = None
        self.is_running = False
        self.success = [None, None]
        self.__resp = None

    def setupThreads(self):
        """Setup messaging threads"""
        self.__inbox = queue.Queue()
        self.__outbox = queue.Queue()

        self.__sender = threading.Thread(target=self.send, daemon=True)
        self.__receiver = threading.Thread(target=self.recv, daemon=True)

        self.is_running = True
        self.__sender.start()
        self.__receiver.start()

    def getId(self):
        """Getter for Node ID"""
        return self.__id

    def setId(self, id_):
        """Setter for Node ID"""
        if self.__id is None:
            self.__id = id_
        else:
            self.notify.critical('suspicious attempt to change ID')

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

    def getResp(self):
        """Getter for received response"""
        return self.__waitForResponse()

    def setResp(self, datagram):
        """Setter for received response"""
        self.__resp = datagram

    def __waitForResponse(self):
        """Stall while waiting for response"""
        while self.__resp is None:
            pass
        resp = self.__resp
        self.__resp = None
        return resp

    def getDatagramFromInbox(self):
        """Getter for next datagram pending"""
        return self.__inbox.get()

    def getDatagramFromOutbox(self):
        """Getter for next datagram pending"""
        return self.__outbox.get()

    def sendDatagram(self, datagram):
        self.__outbox.put(datagram)

    def receiveDatagram(self, datagram):
        self.__inbox.put(datagram)

    def start(self):
        """Handle startup of the Node"""
        try:
            self.setupThreads()
            self.is_running = True
        except Exception as e:
            self.notify.error('MessagingError', str(e))

    def stop(self): # overwrite in subclass
        """Handle stopping of the Node"""
        pass

    def send(self):
        """Threaded function for message sending"""
        while self.getRunning():
            if self._send() is False:
                self.__setSendingSuccess(False)
                return

        self.__setSendingSuccess(True)

    def recv(self):
        """Threaded function for message receiving"""
        while self.getRunning():
            if self._recv() is False:
                self.__setReceivingSuccess(False)
                return

        self.__setReceivingSuccess(True)
        self.notify.warning('done receiving')

    def handleReceivedData(self, data): # overwrite in subclass
        """In-between function for Node reaction to messages received"""
        return NotImplemented
