import socket
import sys

from src.ai.ClientManager import ClientManager
from src.ai.ZoneManager import ZoneManager
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
                self.notify.info('Stopping server...')
                self.__socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                self.notify.critical('Failed to stop server, socket is already closed')
                pass
            finally:
                self.__socket = None

        self.notify.info('Server stopped!')
        sys.exit(0)

    def accept(self):
        return self.__socket.accept()

    def __connect(self):
        try:
            self.notify.info('Starting server...')
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__socket.bind((self.__address, self.__port))
            self.__socket.listen(0) # refuse unaccepted connections
            self.notify.info('Server online!')
        except:
            self.notify.critical('Failed to start server')

    def startManagers(self):
        self.client_manager = ClientManager(self)
        self.zone_manager = ZoneManager(self.client_manager)

    def waitForClients(self):
        while True:
            try:
                self.notify.debug('Waiting for client...')
                ai = self.client_manager.acceptClient()
                ai.start()
                self.notify.debug('Client joined!')
            except KeyboardInterrupt:
                self.notify.error('Server killed')
                break
            except Exception as e:
                self.notify.error('Unknown error')
                raise e
                break
