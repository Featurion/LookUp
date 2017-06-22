import queue
import threading

from src.base import utils
from src.base.KeyHandler import KeyHandler


class Node(KeyHandler):

    def __init__(self):
        KeyHandler.__init__(self)
        self.__id = None
        self.__running = False
        self.__secure = False

        self.__sender = None
        self.__receiver = None
        self.__threads = []

    def setupMessagingThreads(self):
        """Setup messaging threads"""
        self.__inbox = queue.Queue()
        self.__outbox = queue.Queue()

        self.__running = True

        self.__sender = self.addThread(target=self.send, daemon=True)
        self.__receiver = self.addThread(target=self.recv, daemon=True)

    def addThread(self, **kwargs):
        _t = threading.Thread(**kwargs)
        self.__threads.append(_t)
        return _t

    def startThreads(self):
        for _t in self.__threads:
            _t.start()

    def joinThreads(self, timeout=5):
        for _t in self.__threads:
            _t.join(timeout)

    def getId(self):
        """Getter for Node ID"""
        if self.__id:
            return self.__id.bytes.hex()
        else:
            return None

    def setId(self, id_):
        """Setter for Node ID"""
        if self.__id is None:
            self.__id = id_
            self.updateLoggingName('{0}({1})'.format(self.__class__.__name__,
                                                     self.getId()))
        else:
            self.notify.critical('suspicious attempt to change ID')

    def setSecure(self, status):
        self.__secure = status

    @property
    def isSecure(self):
        return self.__secure

    @property
    def isRunning(self):
        """Getter for Node status"""
        return self.__running

    @property
    def isAlive(self):
        return any(_t.isAlive() for _t in self.__threads)

    @property
    def isSending(self):
        """Getter for sending-thread's status"""
        if self.__sender:
            return self.__sender.isAlive()
        else:
            return False

    @property
    def isReceiving(self):
        """Getter for receiving-thread's status"""
        if self.__receiver:
            return self.__receiver.isAlive()
        else:
            return False

    def getDatagramFromInbox(self):
        """Getter for next datagram pending"""
        return self.__inbox.get_nowait()

    def getDatagramFromOutbox(self):
        """Getter for next datagram pending"""
        return self.__outbox.get_nowait()

    def sendDatagram(self, datagram):
        self.__outbox.put(datagram)

    def receiveDatagram(self, datagram):
        self.__inbox.put(datagram)

    def start(self):
        """Handle startup of the Node"""
        self.setupMessagingThreads()

    def stop(self):
        """Handle stopping of the Node"""
        self.__running = False

    def send(self):
        """Threaded function for message sending"""
        while self.isRunning:
            if self._send():
                continue
            else:
                self.notify.error('ThreadingError', 'sending thread broke')
                return

        self.notify.warning('done sending')

    def recv(self):
        """Threaded function for message receiving"""
        while self.isRunning:
            if self._recv():
                continue
            else:
                self.notify.error('ThreadingError', 'receiving thread broke')
                return

        self.notify.warning('done handling messages')

    def handleReceivedData(self, datagram): # overwrite in subclass
        """In-between function for Node reaction to messages received"""
        return NotImplemented
