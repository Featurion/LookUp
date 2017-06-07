import socket
import sys

from src.ai.ClientManager import ClientManager
from src.base.Notifier import Notifier


class Server(Notifier):

    def __init__(self, address, port):
        Notifier.__init__(self)
        self.__socket = None
        self.__address = address
        self.__port = port

    def start(self):
        self.__connect()
        self.startManagers()
        self.waitForClients()

    def stop(self):
        if self.__socket is not None:
            try:
                # log: 'stopping server'
                self.__socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                # log: 'socket is closed'
                pass
            finally:
                self.__socket = None

        # log: 'server stopped'
        sys.exit(0)

    def __connect(self):
        try:
            # log: 'starting server'
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__socket.bind((self.__address, self.__port))
            self.__socket.listen(0) # refuse unaccepted connections
            # log: 'server now running'
        except:
            # log: 'error starting server'
            sys.exit(1)

    def startManagers(self):
        self.client_manager = ClientManager(self.__socket)

    def waitForClients(self):
        while True:
            try:
                # log: 'waiting for client'
                ai = self.client_manager.accept()
                ai.start()
                # log: 'client joined'
            except KeyboardInterrupt:
                # log: 'server killed'
                break
            except Exception as e:
                # log: 'unknown error'
                break
