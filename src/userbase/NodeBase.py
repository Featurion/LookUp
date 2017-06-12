import base64
import queue
import socket
import struct
import threading

from src.base import utils
from src.base.globals import CMD_INIT, CMD_RESP, CMD_RESP_OK, CMD_RESP_NO
from src.base.Datagram import Datagram
from src.base.KeyHandler import KeyHandler

class NodeBase(KeyHandler):

    def __init__(self, address, port, socket_, id_=None):
        KeyHandler.__init__(self)
        self.__address = address
        self.__port = port
        self.__socket = None
        self.__id = None
        self.__name = None
        self.__mode = None
        self.__running = False
        self.__success = [None, None]
        self.__resp = None
        self.__setupSocket(socket_)
        self.__setId(id_)
        self.__setupThreads()

    def __setupSocket(self, socket_): # This should not be in the base class
        try:
            if socket_:
                self.__socket = socket_
            else:
                self.__socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_STREAM)
                self.__socket.connect((self.__address, self.__port))
            self.__socket.settimeout(10)
            self.notify.info('connected to server')
        except ConnectionRefusedError:
            self.notify.error('ConnectionError', 'could not connect to server')
        except Exception as e:
            self.notify.error('ConnectionError', str(e))
            self.stop()

    def __setupThreads(self):
        self.__inbox = queue.Queue()
        self.__outbox = queue.Queue()
        self.__sender = threading.Thread(target=self.send, daemon=True)
        self.__receiver = threading.Thread(target=self.recv, daemon=True)

    def getAddress(self):
        """Getter for node IP address"""
        return self.__address

    def getPort(self):
        """Getter for node port"""
        return self.__port

    def getSocket(self):
        """Getter for socket"""
        return self.__socket

    def getId(self):
        """Getter for ID"""
        return self.__id

    def __setId(self, id_):
        if self.__id is None:
            self.__id = id_
        else:
            self.notify.critical('suspicious attempt to change ID')

    def getName(self):
        """Getter for name"""
        return self.__name

    def setName(self, name):
        if self.__name is None:
            self.__name = name
        else:
            self.notify.critical('suspicious attempt to change name')

    def getMode(self):
        """Getter for mode"""
        return self.__mode

    def __setMode(self, mode):
        if self.__mode is None:
            self.__mode = mode
        else:
            self.notify.critical('suspicious attempt to change mode')

    def getSuccess(self):
        return (self.getSendingSuccess() and self.getReceivingSuccess())

    def getSendingSuccess(self):
        return self.__sending_success

    def setSendingSuccess(self, success):
        self.__sending_success = success

    def getReceivingSuccess(self):
        return self.__receiving_success

    def setReceivingSuccess(self, success):
        self.__receiving_success = success

    def getResp(self):
        return self.__waitForResponse()

    def setResp(self, message):
        self.__resp = message

    def getMessage(self):
        return self.__outbox.get()

    def start(self):
        try:
            self.__running = True
            self.__sender.start()
            self.__receiver.start()
        except Exception as e:
            self.notify.error('ConnectionError', str(e))

    def stop(self):
        try:
            if self.__waitForCleanDisconnect():
                self.__socket.shutdown(socket.SHUT_RDWR)
                self.__socket = None
            else:
                self.notify.error('ExitError', 'an error occurred while exiting')
                self.__socket = None
                return False
        except AttributeError:
            self.notify.critical('socket already closed')
        except OSError:
            self.notify.critical('ConnectionError', 'server closed the connection') # TODO: Go back to login, rather than terminating the client
        except Exception as e:
            self.notify.error('ExitError', str(e))
            return False

        return True

    def send(self):
        while self.__running:
            try:
                data = self._send()
                # TODO: Learn to remove your prints before pushing:
                print()
                print('SEND')
                print(data)
                print()
                data = self.encrypt(data)
                self.__send(data)
                continue
            except queue.Empty:
                continue
            except ValueError:
                self.notify.error('NetworkError', 'tried sending invalid datagram over socket')
            except Exception as e:
                self.notify.error('NetworkError', str(e))

            self.setSendingSuccess(False)
            return

        self.setSendingSuccess(True)

    def _send(self): # overwrite in superclass
        return b''

    def __send(self, data):
        size = len(data)
        self.__sendToSocket(struct.pack('I', socket.htonl(size)), 4)
        self.__sendToSocket(data, size)

    def __sendToSocket(self, data, size):
        while size > 0:
            try:
                size -= self.__socket.send(data[:size])
            except AttributeError:
                self.notify.error('NetworkError', 'socket does not exist')
                return
            except OSError:
                self.notify.error('NetworkError', 'error sending data')
                return
            except Exception as e:
                self.notify.error('NetworkError', str(e))
                return

    def recv(self):
        secure = False

        while self.__running:
            try:
                data = self.__recv()
                if not secure:
                    self.setResp(data)
                    secure = True
                else:
                    data = self.decrypt(data)
                    # TODO: Learn to remove your prints before pushing:
                    print()
                    print('RECV')
                    print(data)
                    print()
                    self._recv(data)
                continue
            except InterruptedError:
                # kill in main thread
                self.notify.error('ConnectionError', 'server disconnected the client')
            except ValueError as e:
                self.notify.error('NetworkError', 'received invalid message')
            except Exception as e:
                self.notify.error('NetworkError', str(e))

            self.setReceivingSuccess(False)
            return

        self.setReceivingSuccess(True)

    def _recv(self, data): # overwrite in superclass
        return data

    def __recv(self):
        try:
            size_indicator = self.__recvFromSocket(4)
            size = socket.ntohl(struct.unpack('I', size_indicator)[0])
            data = self.__recvFromSocket(size)
            return data
        except struct.error as e: # TODO: Go back to login
            self.notify.error('ConnectionError', 'connection was closed unexpectedly')
            self.stop()
        except Exception as e:
            self.notify.error('NetworkError', str(e))

    def __recvFromSocket(self, size):
        data = b''
        while size > 0:
            try:
                _data = self.__socket.recv(size)
                if _data:
                    size -= len(_data)
                    data += _data
                else:
                    raise OSError()
            except AttributeError:
                self.notify.error('NetworkError', 'socket does not exist')
                return b''
            except OSError as e:
                if str(e) == 'timed out':
                    continue
                else:
                    self.notify.error('NetworkError', 'error receiving data')
                    return b''
            except Exception as e:
                self.notify.error('NetworkError', str(e))
                return b''

        return data

    def sendMessage(self, datagram):
        datagram.setSender(self.getId())
        datagram.setTimestamp(utils.getTimestamp())
        self.__outbox.put(datagram)

    def sendResp(self, data):
        datagram = Datagram()
        datagram.setCommand(CMD_RESP)
        datagram.setRecipient(self.getId())
        datagram.setData(data)
        self.sendMessage(datagram)

    def sendOK(self):
        datagram = Datagram()
        datagram.setCommand(CMD_RESP_OK)
        datagram.setRecipient(self.getId())
        self.sendMessage(datagram)

    def sendNo(self):
        datagram = Datagram()
        datagram.setCommand(CMD_RESP_NO)
        datagram.setRecipient(self.getId())
        self.sendMessage(datagram)

    def __sendKey(self):
        datagram = Datagram()
        datagram.setCommand(CMD_INIT)
        datagram.setSender(self.getId())
        datagram.setRecipient(self.getId())
        datagram.setData(self.getKey())

        data = datagram.toJSON()
        data = base64.b85encode(str(data).encode())
        self.__send(data)

        self.notify.debug('sent public key')

    def __receiveKey(self):
        data = self.getResp()
        data = base64.b85decode(data).decode()

        datagram = Datagram.fromJSON(data)
        key = datagram.getData()
        self.generateSecret(key)

        self.notify.debug('received public key')

        return datagram

    def __receiveKeyAndId(self):
        datagram = self.__receiveKey()
        id_ = datagram.getRecipient()
        self.__setId(id_)

    def initiateHandshake(self):
        self.__sendKey()
        self.__receiveKey()

    def doHandshake(self):
        self.__receiveKeyAndId()
        self.__sendKey()

    def __waitForCleanDisconnect(self):
        self.__running = False
        self.notify.info('disconnecting from the server')

        if not self.getSuccess():
            if self.getSendingSuccess() is not True:
                self.notify.error('NetworkError', 'an error occurred while halting message sending')

            if self.getReceivingSuccess() is not True:
                self.notify.error('NetworkError', 'an error occurred while halting message receiving')

            return False
        else:
            return True

    def __waitForResponse(self):
        while self.__resp is None:
            pass
        resp = self.__resp
        self.__resp = None
        return resp
