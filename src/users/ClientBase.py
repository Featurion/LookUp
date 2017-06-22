import queue
import select
import socket
import struct

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
        self.__resp = None

        self.__socket_receiver = None
        self.__send_success_flag = False

    def start(self):
        Node.start(self)
        self.setupSocket()
        self.startManagers()
        self.startThreads()

    def startManagers(self): # overwrite in subclass
        pass

    def stop(self):
        """Handle stopping of the client"""
        try:
            Node.stop(self)
            self.joinThreads(constants.DISCONNECT_DELAY) # wait for clean disconnect
        except OSError:
            self.notify.debug('socket is closed')
        except Exception as e:
            self.notify.error('ExitError', str(e))
            return False

        return True

    def cleanup(self):
        Node.cleanup(self)
        self.__address = None
        self.__port = None
        self.__name = None
        self.__mode = None
        self.__resp = None
        self.send_success_flag = None
        if self.__socket:
            self.__socket.shutdown(socket.SHUT_RDWR)
            self.__socket.close()
            del self.__socket
            self.__socket = None
        if self.__socket_receiver:
            self.__socket_receiver.join()
            del self.__socket_receiver
            self.__socket_receiver = None

    def getSocket(self):
        """Getter for socket"""
        return self.__socket

    def setSocket(self, socket_):
        """Setter for socket"""
        if self.__socket is None:
            self.__socket = socket_
        else:
            self.notify.critical('suspicious attempt to change socket')

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

    def getResp(self):
        """Getter for received response"""
        return self.__waitForResponse()

    def setResp(self, datagram):
        """Setter for received response"""
        self.__resp = datagram

    def __waitForResponse(self):
        """Stall while waiting for response"""
        self.notify.debug('waiting for a response')

        while self.isRunning and self.__resp is None:
            pass
        resp = self.__resp
        self.__resp = None
        return resp

    def __waitForSendSuccess(self):
        """Stall while sending data"""
        while self.isRunning and not self.__send_success_flag:
            pass

        self.notify.debug('sent data successfully')
        self.__send_success_flag = False

    def setupSocket(self):
        self.getSocket().settimeout(constants.SOCKET_TIMEOUT)

    def setupMessagingThreads(self):
        Node.setupMessagingThreads(self)
        self.__socket_receiver = self.addThread(target=self.__recv,
                                                daemon=True)

    def _send(self):
        try:
            data = self.getDatagramFromOutbox().toJSON()
            self.__send(data)
            del data
            return True # successful
        except queue.Empty:
            return True # successful
        except ValueError:
            self.notify.error('NetworkError', 'tried sending invalid datagram')
        except Exception as e:
            self.notify.error('NetworkError', str(e))

        return False # unsuccessful

    def __send(self, data):
        """Send data length and data"""
        if self.isSecure:
            data = self.encrypt(data)
        elif data:
            data = data.encode()
        else:
            return

        size = len(data)
        self.__sendToSocket(struct.pack('I', socket.htonl(size)), 4)
        self.__sendToSocket(data, size)

        self.__send_success_flag = True

        del size
        del data

    def __sendToSocket(self, data, size):
        """Send data through socket transfer"""
        while self.isRunning and size > 0:
            try:
                size -= self.getSocket().send(data[:size])
            except OSError:
                self.notify.error('SocketError', 'error sending data')
                break
            except Exception as e:
                self.notify.error('SocketError', str(e))
                break

        if size > 0:
            Node.stop(self)

        del data
        del size

    def _recv(self):
        try:
            datagram = self.getDatagramFromInbox()
            self.handleReceivedDatagram(datagram)
            del datagram
            return True # successful
        except queue.Empty:
            return True # successful
        except InterruptedError:
            self.notify.error('ConnectionError', 'disconnected')
        except ValueError as e:
            self.notify.error('NetworkError', 'received invalid datagram')
        except Exception as e:
            self.notify.error('NetworkError', str(e))

        return False # unsuccessful

    def __recv(self):
        """Receive data length and data"""
        while self.isRunning:
            try:
                size_indicator = self.__recvFromSocket(4)
                size = socket.ntohl(struct.unpack('I', size_indicator)[0])
                data = self.__recvFromSocket(size)

                if self.isSecure:
                    data = self.decrypt(data)

                datagram = Datagram.fromJSON(data)
                self.receiveDatagram(datagram)

                del size_indicator
                del size
                del data
                del datagram
            except struct.error as e:
                self.notify.warning('connection was closed unexpectedly')
                break
            except Exception as e:
                self.notify.error('NetworkError', str(e))
                break

        Node.stop(self)
        self.notify.debug('done receiving')

    def __recvFromSocket(self, size):
        """Receive data through socket transfer"""
        data = b''
        while self.isRunning and size > 0:
            try:
                _data = self.getSocket().recv(size)
                if _data:
                    size -= len(_data)
                    data += _data
                else:
                    raise OSError()
                del _data
            except OSError as e:
                if str(e) == 'timed out':
                    continue
                else:
                    return b''
            except Exception as e:
                self.notify.error('NetworkError', str(e))
                return b''

        del size
        return data

    def sendDatagram(self, datagram):
        datagram.setTimestamp(utils.getTimestamp())
        Node.sendDatagram(self, datagram)

        self.__waitForSendSuccess()

        del datagram

    def sendResp(self, data):
        datagram = Datagram()
        datagram.setCommand(constants.CMD_RESP)
        datagram.setSender(self.getId())
        datagram.setRecipient(self.getId())
        datagram.setData(data)

        self.sendDatagram(datagram)

        del data
        del datagram

    def handleReceivedDatagram(self, datagram):
        if datagram.getCommand() == constants.CMD_RESP:
            self.setResp(datagram)
        else:
            return datagram

        del datagram
        return None
