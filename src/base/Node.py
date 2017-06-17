import base64
import queue
import socket
import ssl
import struct
import threading

from src.base import utils
from src.base.KeyHandler import KeyHandler


class Node(KeyHandler):

    def __init__(self):
        KeyHandler.__init__(self)
        self.__socket = None
        self.__id = None
        self.is_running = False
        self.success = [None, None]
        self.__resp = None
        self.__wantSSL = False

    def __supportSSL(self, socket_):
        return ssl.wrap_socket(socket_,
                               ssl_version=ssl.PROTOCOL_TLSv1_2,
                               ciphers='ECDHE-RSA-AES256-GCM-SHA384')

    def setupSocket(self, socket_, client=False):
        """Setup socket"""
        try:
            if self.__wantSSL and client:
                self.__socket = self.__supportSSL(socket_)
            else:
                self.__socket = socket_
            self.__socket.settimeout(10)
            self.notify.info('connected to server')
        except ConnectionRefusedError:
            self.notify.error('ConnectionError', 'could not connect to server')
        except Exception as e:
            self.notify.error('ConnectionError', str(e))
            self.stop()

    def setupThreads(self):
        """Setup messaging threads"""
        self.__inbox = queue.Queue()
        self.__outbox = queue.Queue()
        self.__sender = threading.Thread(target=self.send, daemon=True)
        self.__receiver = threading.Thread(target=self.recv, daemon=True)

    def getSocket(self):
        """Getter for socket"""
        return self.__socket

    def setSocket(self, socket_):
        """Setter for socket"""
        if self.__socket is None:
            self.__socket = socket_
        else:
            self.notify.critical('suspicious attempt to change socket')

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

    def getDatagram(self):
        """Getter for next datagram pending"""
        return self.__outbox.get()

    def sendDatagram(self, datagram):
        datagram.setTimestamp(utils.getTimestamp())
        self.__outbox.put(datagram)

    def start(self):
        """Handle startup of the Node"""
        try:
            self.is_running = True
            self.__sender.start()
            self.__receiver.start()
        except Exception as e:
            self.notify.error('ConnectionError', str(e))

    def stop(self):
        """Handle stopping of the Node"""
        self.getSocket().shutdown(socket.SHUT_RDWR)

    def send(self):
        """Threaded function for message sending"""
        while self.getRunning():
            try:
                data = self.getDatagram().toJSON()
                data = self.encrypt(data)
                self.__send(data)
                continue
            except queue.Empty:
                continue
            except ValueError:
                self.notify.error('NetworkError', 'tried sending invalid datagram')
            except Exception as e:
                self.notify.error('NetworkError', str(e))
                raise e

            self.__setSendingSuccess(False)
            return

        self.__setSendingSuccess(True)
        self.notify.warning('done sending')

    def __send(self, data):
        """Send data length and data"""
        size = len(data)
        self.__sendToSocket(struct.pack('I', socket.htonl(size)), 4)
        self.__sendToSocket(data, size)

    def __sendToSocket(self, data, size):
        """Send data through socket transfer"""
        while size > 0:
            try:
                size -= self.__socket.send(data[:size])
            except OSError:
                self.notify.error('SocketError', 'error sending data')
                return
            except Exception as e:
                self.notify.error('SocketError', str(e))
                return

    def recv(self):
        """Threaded function for message receiving"""
        secure = False

        while self.getRunning():
            try:
                data = self.__recv()
                if not secure:
                    self.setResp(data)
                    secure = True
                    continue
                elif data:
                    data = self.decrypt(data)
                    self._recv(data)
                    continue
                else:
                    break
            except InterruptedError:
                self.notify.error('ConnectionError', 'disconnected')
            except ValueError as e:
                self.notify.error('NetworkError', 'received invalid datagram')
            except Exception as e:
                self.notify.error('NetworkError', str(e))
                raise e

            self.__setReceivingSuccess(False)
            return

        self.__setReceivingSuccess(True)

    def _recv(self, data): # overwrite in superclass
        """In-between function for Node reaction to messages received"""
        return data

    def __recv(self):
        """Receive data length and data"""
        try:
            size_indicator = self.__recvFromSocket(4)
            size = socket.ntohl(struct.unpack('I', size_indicator)[0])
            data = self.__recvFromSocket(size)
            return data
        except struct.error as e:
            self.notify.error('ConnectionError', 'connection was closed unexpectedly')
            self.stop()
        except Exception as e:
            self.notify.error('NetworkError', str(e))
            raise e

    def __recvFromSocket(self, size):
        """Receive data through socket transfer"""
        data = b''
        while size > 0:
            try:
                _data = self.__socket.recv(size)
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
