import base64
import queue
import socket
import struct
import threading

from src.base import utils
from src.base.globals import SERVER, CMD_INIT, CMD_RESP_OK, CMD_RESP_NO
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

    def __setupSocket(self, socket_):
        try:
            if socket_:
                self.__socket = socket_
            else:
                self.__socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_STREAM)
                self.__socket.connect((self.__address, self.__port))
            self.__socket.settimeout(10)
            # log: INFO, 'connected to server'
        except ConnectionRefusedError:
            # err: INFO, 'could not connect to server'
            pass
        except Exception as e:
            # err
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
            # log: DEBUG, 'suspicious attempt to change ID'
            pass

    def getName(self):
        """Getter for name"""
        return self.__name

    def __setName(self, name):
        if self.__name is None:
            self.__name = name
        else:
            # log: DEBUG, 'suspicious attempt to change name'
            pass

    def getMode(self):
        """Getter for mode"""
        return self.__mode

    def __setMode(self, mode):
        if self.__mode is None:
            self.__mode = mode
        else:
            # log: DEBUG, 'suspicious attempt to change mode'
            pass

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
            # err
            pass

    def stop(self):
        try:
            if self.__waitForCleanDisconnect():
                self.__socket.shutdown(socket.SHUT_RDWR)
                self.__socket = None
            else:
                # err: 'an error occured while exiting'
                self.__socket = None
                return False
        except AttributeError:
            # err: DEBUG, 'socket does not exist'
            pass
        except OSError:
            # err: INFO, 'server closed the connection'
            pass
        except Exception as e:
            # err
            return False

        return True

    def send(self):
        while self.__running:
            try:
                data = self._send()
                data = self.encrypt(data)
                self.__send(data)
                continue
            except queue.Empty:
                continue
            except ValueError:
                # err: DEBUG, 'tried sending invalid message'
                pass
            except Exception as e:
                # err
                pass

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
                # log: DEBUG, 'socket does not exist'
                return
            except OSError:
                # log: DEBUG, 'error sending data'
                return
            except Exception as e:
                # err
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
                    self._recv(data)
                continue
            except InterruptedError:
                # log: DEBUG, 'server disconnected the client'
                # kill in main thread
                pass
            except ValueError as e:
                # err
                # log: DEBUG, 'received invalid message'
                pass
            except Exception as e:
                # err
                pass

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
        except struct.error as e:
            # log: DEBUG, 'connection was closed unexpectedly'
            pass
        except Exception as e:
            # err
            pass

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
                # log: DEBUG, 'socket does not exist'
                return b''
            except OSError as e:
                if str(e) == 'timed out':
                    continue
                else:
                    # log: DEBUG, 'error receiving data'
                    return b''
            except Exception as e:
                # err
                return b''

        return data

    def sendMessage(self, datagram):
        datagram.setSender(self.getId())
        datagram.setTimestamp(utils.getTimestamp())
        self.__outbox.put(datagram)

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
        # log: DEBUG, 'sent key'

    def __receiveKey(self):
        data = self.getResp()
        data = base64.b85decode(data).decode()

        datagram = Datagram.fromJSON(data)
        key = datagram.getData()
        self.generateSecret(key)
        # log: DEBUG, 'received key'

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
        # log: INFO, 'disconnecting from server'

        if not self.getSuccess():
            if self.getSendingSuccess() is not True:
                # err: 'an error occured while halting message sending'
                pass

            if self.getReceivingSuccess() is not True:
                # err: 'an error occured while halting message receiving'
                pass

            return False
        else:
            return True

    def __waitForResponse(self):
        while self.__resp is None:
            pass
        resp = self.__resp
        self.__resp = None
        return resp
