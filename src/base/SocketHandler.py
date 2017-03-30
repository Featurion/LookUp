import socket
import struct
import sys
from src.base.globals import MAX_PORT_SIZE, NetworkError, ERR_NO_CONNECTION
from src.base.globals import DEBUG_CONN_CLOSED, ERR_CONN_CLOSED, CONN_CLOSED
from src.base.Notifier import Notifier


class SocketHandler(Notifier):

    @staticmethod
    def isAddrValid(addr):
        assert isinstance(addr, str)
        for n in addr.split('.'):
            if int(n) not in range(0, 256):
                return False
        return True

    @staticmethod
    def isPortValid(port):
        assert isinstance(port, int)
        if port in range(0, pow(2, MAX_PORT_SIZE)):
            return True
        else:
            return False

    def __init__(self, addr, port, sock=None):
        assert SocketHandler.isAddrValid(addr)
        assert SocketHandler.isPortValid(port)
        Notifier.__init__(self)
        self.addr = addr
        self.port = port
        if sock:
            self.socket = sock
            self.connected = True
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connected = False

    def connect(self):
        try:
            self.socket.connect((self.addr, self.port))
            self.connected = True
        except ConnectionRefusedError as e:
            self.notify.error(ERR_NO_CONNECTION)
            sys.exit()
        except socket.error as e:
            self.notify.error(str(e))
            self.connected = False

    def disconnect(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            self.notify.warning(DEBUG_CONN_CLOSED)
        self.connected = False

    def send(self, data):
        data = data.encode('utf-8')
        size = len(data)
        self._send(struct.pack('I', socket.htonl(size)), 4) # Send size
        self._send(data, size) # Send data

    def _send(self, data, size):
        if self.connected:
            sent = 0
            while sent < size:
                try:
                    amount_sent = self.socket.send(data[:size])
                except:
                    self.connected = False
                    self.notify.error(ERR_CONN_CLOSED)
                    raise NetworkError(CONN_CLOSED)
                if amount_sent:
                    sent += amount_sent
                else:
                    self.connected = False
                    self.notify.error(ERR_CONN_CLOSED)
                    raise NetworkError(CONN_CLOSED)
        else:
            self.notify.warning(DEBUG_CONN_CLOSED)

    def recv(self):
        indicator = self._recv(4)
        if indicator:
            size = socket.ntohl(struct.unpack('I', indicator)[0]) # Receive size
            data = self._recv(size).decode('utf-8') # Receive data
            return data
        else:
            return None

    def _recv(self, size):
        if self.connected:
            try:
                data = b''
                amount_recv = 0
                while amount_recv < size:
                    recv_data = self.socket.recv(size - amount_recv)
                    if recv_data:
                        data += recv_data
                        amount_recv += len(recv_data)
                    else:
                        self.connected = False
                        return
                return data
            except socket.error as e:
                self.notify.error(str(e))
        else:
            self.notify.warning(DEBUG_CONN_CLOSED)
