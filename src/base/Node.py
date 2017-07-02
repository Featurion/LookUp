import queue
import threading

from src.base import utils
from src.base.KeyHandler import KeyHandler
from src.base.UniqueIDManager import UniqueIDManager

class Node(KeyHandler):

    def __init__(self):
        KeyHandler.__init__(self)
        self.__id = None
        self.__running = False
        self.__secure = False
        self.__new = False

        self.__inbox = None
        self.__outbox = None
        self.__sender = None
        self.__receiver = None
        self.__threads = []

        self.COMMAND_MAP = {} # update in subclass

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

        del _t

    def joinThreads(self, timeout=5):
        for _t in self.__threads:
            _t.join(timeout)

        del _t

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
        del status

    def setNew(self, status):
        self.__new = status
        del status

    @property
    def isSecure(self):
        return self.__secure

    @property
    def isNew(self):
        return self.__new

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
        """Send a new datagram"""
        datagram._setId(str(UniqueIDManager().generateId())) # Generate a unique ID for the Datagram and then set it
        self.__outbox.put(datagram)
        del datagram

    def emitDatagram(self, datagram):
        """Emit a datagram (meant for relaying)"""
        self.__outbox.put(datagram)
        del datagram

    def receiveDatagram(self, datagram):
        self.__inbox.put(datagram)
        del datagram

    def start(self):
        """Handle startup of the Node"""
        self.setupMessagingThreads()

    def stop(self):
        """Handle stopping of the Node"""
        self.__running = False

    def cleanup(self):
        KeyHandler.cleanup(self)
        self.__id = None
        self.__running = None
        self.__secure = None
        self.__threads = None
        if self.__inbox:
            with self.__inbox.mutex:
                self.__inbox.queue.clear()
            del self.__inbox
            self.__inbox = None
        if self.__outbox:
            with self.__outbox.mutex:
                self.__outbox.queue.clear()
            del self.__outbox
        if self.__sender:
            if self.__sender.isAlive():
                self.__sender.join()
            del self.__sender
            self.__sender = None
        if self.__receiver:
            if self.__receiver.isAlive():
                self.__receiver.join()
            del self.__receiver
            self.__receiver = None

    def send(self):
        """Threaded function for message sending"""
        while self.isRunning:
            if self._send():
                continue
            else:
                self.notify.error('ThreadingError', 'sending thread broke')
                return

        Node.stop(self)
        self.notify.warning('done sending')

    def recv(self):
        """Threaded function for message receiving"""
        while self.isRunning:
            if self._recv():
                continue
            else:
                self.notify.error('ThreadingError', 'receiving thread broke')
                return

        Node.stop(self)
        self.notify.warning('done handling messages')

    def handleReceivedDatagram(self, datagram):
        """In-between function for Node reaction to messages received"""
        if datagram.getCommand() in self.COMMAND_MAP:
            func = self.COMMAND_MAP.get(datagram.getCommand())
            func(datagram)
        else:
            self.notify.warning('received suspicious datagram')

        del datagram
