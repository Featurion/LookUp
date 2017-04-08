import base64
import socket
import struct
import sys
from src.base.globals import MAX_PORT_SIZE, NetworkError, ERR_NO_CONNECTION
from src.base.globals import DEBUG_CONN_CLOSED, ERR_CONN_CLOSED, CONN_CLOSED
from src.base.Notifier import Notifier
from src.crypto.KeyHandler import KeyHandler

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
        self.handshake_done = False
        self.key_handler = KeyHandler()
        self.key_handler.generateDHKey()
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
            self.notify.debug(DEBUG_CONN_CLOSED)
        self.connected = False

    def initiateHandshake(self):
        our_key = base64.b64encode(str(self.key_handler.getDHPubKey()).encode()) # Get our public key
        self.send(our_key) # send public key

        their_key = self.recv() # Receive the data from the server
        self.key_handler.computeDHSecret(int(base64.b64decode(their_key)))

        self.handshake_done = True

    def doHandshake(self):
        their_key = self.recv() # Receive the data from the client
        self.key_handler.computeDHSecret(int(base64.b64decode(their_key)))

        our_key = base64.b64encode(str(self.key_handler.getDHPubKey()).encode()) # Get our public key
        self.send(our_key) # Send our public key

        self.handshake_done = True

    def send(self, data):
        if not self.handshake_done:
            size = len(data)

            self._send(struct.pack('I', socket.htonl(size)), 4) # Send size
            self._send(data, size) # Send data
        else:
            enc_data = base64.b64encode(data.encode('utf-8'))
            data = self.key_handler.aesEncrypt(enc_data)

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
            data = self._recv(size) # Receive data
            if self.handshake_done:
                data = base64.b64decode(self.key_handler.aesDecrypt(data))
            return data.decode('utf-8')
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
            except socket.error:
                pass # RequestManager handles this
        else:
            self.notify.warning(DEBUG_CONN_CLOSED)
