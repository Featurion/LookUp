import base64
import socket
import ssl
import struct
import threading

from src.base import constants, utils
from src.base.Datagram import Datagram
from src.base.Node import Node


class ClientBase(Node):

    def __init__(self, address, port):
        Node.__init__(self)
        self.__address = address
        self.__port = port
        self.__socket = None
        self.__name = None
        self.__mode = None
        self.is_secure = False

    def __supportSSL(self, socket_):
        self.setSocket(ssl.wrap_socket(socket_,
                                       ca_certs="certs/pem.crt",
                                       cert_reqs=ssl.CERT_REQUIRED,
                                       ssl_version=ssl.PROTOCOL_TLSv1_2,
                                       ciphers='ECDHE-RSA-AES256-GCM-SHA384'))

    def setupSocket(self, socket_, client=False):
        """Setup socket"""
        try:
            if constants.TLS_ENABLED and client:
                self.notify.info('connecting with SSL!')
                self.__supportSSL(socket_)
            else:
                self.notify.info('connecting without SSL!')
                self.setSocket(socket_)
            self.notify.info('connected to server')
        except ConnectionRefusedError:
            self.notify.error('ConnectionError', 'could not connect to server')
        except ssl.SSLError as e:
            self.notify.error('SSLError', str(e))
        except Exception as e:
            self.notify.error('ConnectionError', str(e))
            self.stop()

    def setupThreads(self):
        Node.setupThreads(self)
        self.__socket_receiver = threading.Thread(target=self.__recv,
                                                  daemon=True)
        self.__socket_receiver.start()

    def socketConnect(self, address, port):
        try:
            self.getSocket().connect((address, port))
        except ssl.SSLError as e:
            self.notify.critical(str(e))

    def getSocket(self):
        """Getter for socket"""
        return self.__socket

    def setSocket(self, socket_):
        """Setter for socket"""
        if self.__socket is None:
            self.__socket = socket_
        else:
            self.notify.critical('suspicious attempt to change socket')

    def sendDatagram(self, datagram):
        datagram.setTimestamp(utils.getTimestamp())
        Node.sendDatagram(self, datagram)

    def start(self):
        Node.start(self)
        self.startManagers()

    def stop(self):
        self.getSocket().shutdown(socket.SHUT_RDWR)

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

    def _send(self):
        try:
            data = self.getDatagramFromOutbox().toJSON()
            self.__send(self.encrypt(data))
            return None
        except queue.Empty:
            return None
        except ValueError:
            self.notify.error('NetworkError', 'tried sending invalid datagram')
            return False
        except Exception as e:
            self.notify.error('NetworkError', str(e))
            return False

    def __send(self, data):
        """Send data length and data"""
        size = len(data)
        self.__sendToSocket(struct.pack('I', socket.htonl(size)), 4)
        self.__sendToSocket(data, size)

    def __sendToSocket(self, data, size):
        """Send data through socket transfer"""
        while size > 0:
            try:
                size -= self.getSocket().send(data[:size])
            except OSError:
                self.notify.error('SocketError', 'error sending data')
                return
            except Exception as e:
                self.notify.error('SocketError', str(e))
                return

    def _recv(self):
        try:
            datagram = self.getDatagramFromInbox()
            self.handleReceivedDatagram(datagram)
            return None
        except InterruptedError:
            self.notify.error('ConnectionError', 'disconnected')
        except ValueError as e:
            self.notify.error('NetworkError', 'received invalid datagram')
        except Exception as e:
            self.notify.error('NetworkError', str(e))
        return False

    def __recv(self):
        """Receive data length and data"""
        while self.is_running:
            try:
                size_indicator = self.__recvFromSocket(4)
                size = socket.ntohl(struct.unpack('I', size_indicator)[0])
                data = self.__recvFromSocket(size)
                if self.is_secure:
                    datagram = Datagram.fromJSON(self.decrypt(data))
                    self.receiveDatagram(datagram)
                else:
                    self.setResp(data)
            except struct.error as e:
                self.notify.error('ConnectionError', 'connection was closed unexpectedly')
                break
            except Exception as e:
                self.notify.error('NetworkError', str(e))
                break

        self.stop()

    def __recvFromSocket(self, size):
        """Receive data through socket transfer"""
        data = b''
        while size > 0:
            try:
                _data = self.getSocket().recv(size)
                if _data:
                    size -= len(_data)
                    data += _data
                else:
                    raise OSError()
            except OSError as e:
                if str(e) == 'timed out':
                    continue
                else:
                    return b''
            except Exception as e:
                self.notify.error('NetworkError', str(e))
                return b''

        return data

    def sendKey(self):
        data = base64.b85encode(str(self.getKey()).encode())
        self.__send(data)
        self.notify.debug('sent public key')

    def receiveKey(self):
        key = int(base64.b85decode(self.getResp()).decode())
        self.generateSecret(key)
        self.notify.debug('received public key')

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
