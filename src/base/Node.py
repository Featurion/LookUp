import queue
import threading
import base64

from src.base import constants, utils
from src.base.KeyHandler import KeyHandler
from src.base.UniqueIDManager import UniqueIDManager


class Node(KeyHandler):

    def __init__(self):
        KeyHandler.__init__(self)
        self.__id = None
        self.__stopping = False
        self.__secure = False

        self.__inbox = None
        self.__outbox = None
        self.__sender = None
        self.__receiver = None
        self.__threads = []

        self.COMMAND_MAP = {} # update in subclass

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

    def startStopping(self):
        self.__stopping = True

    @property
    def isSecure(self):
        return self.__secure

    @property
    def isStopping(self):
        return self.__stopping

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

    def start(self):
        """Handle startup of the Node"""
        self.setupMessagingThreads()

    def stop(self):
        """Handle stopping of the Node"""
        if not self.isStopping:
            self.startStopping()
            self.joinThreads(constants.DISCONNECT_DELAY) # wait for clean disconnect
        elif self.isAlive:
            self.notify.warning('already stopping')
        else:
            pass

    def setupMessagingThreads(self):
        """Setup messaging threads"""
        self.__inbox = queue.Queue()
        self.__outbox = queue.Queue()

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

        del self.__threads[:]

    def getOutbox(self):
        """Getter for datagram outbox"""
        return self.__outbox

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

    def receiveDatagram(self, datagram):
        """Receive a datagram"""
        self.__inbox.put(datagram)
        del datagram

    def cleanup(self):
        KeyHandler.cleanup(self)
        self.__id = None
        self.__stopping = False
        self.__secure = False
        if self.__threads:
            del self.__threads[:]
            self.__threads = []
        if self.__inbox:
            with self.__inbox.mutex:
                self.__inbox.queue.clear()
            del self.__inbox
            self.__inbox = None
        if self.__outbox:
            with self.__outbox.mutex:
                self.__outbox.queue.clear()
            del self.__outbox

    def send(self):
        """Threaded function for message sending"""
        while not self.isStopping:
            if not self._send():
                self.notify.error('ThreadingError', 'sending thread broke')
                return

        self.notify.debug('done sending')

    def recv(self):
        """Threaded function for message receiving"""
        while not self.isStopping:
            if not self._recv():
                self.notify.error('ThreadingError', 'receiving thread broke')
                return

        self.notify.debug('done receiving')

    def handleReceivedDatagram(self, datagram):
        """In-between function for Node reaction to messages received"""
        if datagram.getCommand() in self.COMMAND_MAP:
            func = self.COMMAND_MAP.get(datagram.getCommand())
            func(datagram)
        else:
            self.notify.warning('received suspicious datagram')

        del datagram

    def verifyHMAC(self, givenHMAC, data, key=None):
        """Verify an HMAC"""
        if key is None:
            generatedHMAC = self.generateHMAC(data)
        else:
            generatedHMAC = self.generateHMAC(data, key)
        return utils.secureStrCmp(generatedHMAC, base64.b85decode(givenHMAC))
