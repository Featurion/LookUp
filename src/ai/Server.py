import logging
import os
import signal
import socket
import sys
import ssl
from src.ai.ClientAI import ClientAI
from src.ai.ClientManagerAI import ClientManagerAI
from src.ai.SessionManagerAI import SessionManagerAI
from src.base.globals import DEBUG_RECV_CONN, DEBUG_CONN_CLOSED
from src.base.globals import DEBUG_SERVER_START, DEBUG_SERVER_STOP
from src.base.globals import ERR_INVALID_ADDR, ERR_INVALID_PORT
from src.base.globals import ERR_SERVER_START, ERR_INVALID_CLIENT
from src.base.Notifier import Notifier
from src.base.SocketHandler import SocketHandler


class Server(Notifier):

    def __init__(self, addr, port):
        assert isinstance(addr, str)
        assert isinstance(port, int)
        Notifier.__init__(self)
        self.socket = None
        if not SocketHandler.isAddrValid(addr):
            self.notify.error(ERR_INVALID_ADDR, addr)
        else:
            self.addr = addr
        if not SocketHandler.isPortValid(port):
            self.notify.error(ERR_INVALID_PORT, port)
        else:
            self.port = port

    def start(self):
        self.__connect()
        self.__startManagers()
        while True: # Wait for client to connect
            try:
                while True:
                    socket, (addr, port) = self.socket.accept()
                    self.notify.info(DEBUG_RECV_CONN, addr, port)
                    client_socket = SocketHandler(addr, port, socket)
                    client_socket.doHandshake()
                    if client_socket.handshake_done:
                        break
                client_ai = ClientAI(self, client_socket)
                client_ai.start()
            except KeyboardInterrupt:
                self.notify.info(DEBUG_SERVER_STOP)
                break
            except Exception as e:
                self.notify.error(str(e))

    def __startManagers(self):
        self.client_manager = ClientManagerAI(self)
        self.session_manager = SessionManagerAI(self)

    def __connect(self):
        try:
            self.notify.info(DEBUG_SERVER_START)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket = ssl.wrap_socket(self.socket, server_side=True, keyfile='certs/ca.key', certfile='certs/ca.crt',
                                          cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_TLSv1_2,
                                          ciphers='ECDHE-RSA-AES256-GCM-SHA384', do_handshake_on_connect=True)
            self.socket.bind((self.addr, self.port))
            self.socket.listen(0) # Refuse all unaccepted connections
        except:
            self.notify.critical(ERR_SERVER_START)

    def sendMessage(self, message):
        client_ai = self.client_manager.getClientById(message.to_id)
        if client_ai:
            client_ai.sendMessage(message)
        else:
            self.notify.error(ERR_INVALID_CLIENT, message.to_id)

    def stop(self):
        if self.client_manager:
            self.client_manager.stop()
            self.client_manager = None
        if self.socket:
            try:
                self.notify.info(DEBUG_SERVER_STOP)
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                self.notify.warning(DEBUG_CONN_CLOSED)
            finally:
                self.socket = None
