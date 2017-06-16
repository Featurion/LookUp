import socket

from src.base.Node import Node


class ClientBase(Node):

    def __init__(self, address, port):
        Node.__init__(self)
        self.__address = address
        self.__port = port
        self.__name = None
        self.__mode = None
        self.setupThreads()

    def start(self):
        Node.start(self)
        self.startManagers()

    def startManagers(self): # overwrite in subclass
        pass

    def getAddress(self):
        """Getter for client IP address"""
        return self.__address

    def getPort(self):
        """Getter for client port"""
        return self.__port

    def getName(self):
        """Getter for client name"""
        return self.__name

    def setName(self, name):
        """Setter for client name"""
        if self.__name is None:
            self.__name = name
        else:
            self.notify.critical('suspicious attempt to change name')

    def getMode(self):
        """Getter for client mode"""
        return self.__mode

    def setMode(self, mode):
        """Setter for client mode"""
        if self.__mode is None:
            self.__mode = mode
        else:
            self.notify.critical('suspicious attempt to change mode')

    def sendDatagram(self, datagram):
        datagram.setSender(self.getId())
        Node.sendDatagram(self, datagram)

    def stop(self):
        """Handle stopping of the client"""
        try:
            if self.waitForCleanDisconnect():
                Node.stop(self)
            else:
                return False
        except OSError:
            self.notify.debug('socket is closed')
        except Exception as e:
            self.notify.error('ExitError', str(e))
            return False

        return True

    def waitForCleanDisconnect(self):
        self.setRunning(False)
        self.notify.info('disconnecting from the server...')

        if self.getSendingSuccess():
            self.notify.error('ExitError', 'an error occurred while halting datagram sending')
            return False
        elif self.getReceivingSuccess():
            self.notify.error('ExitError', 'an error occurred while halting datagram receiving')
            return False
        else:
            return True
