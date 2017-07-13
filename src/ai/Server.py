import socket
import ssl
import sys

from src.base.Notifier import Notifier
from src.base.constants import TLS_ENABLED
from src.users.BanManagerAI import BanManagerAI
from src.users.ClientManagerAI import ClientManagerAI
from src.zones.ZoneManagerAI import ZoneManagerAI
from src.ai.Console import Console

class Server(Notifier):

    def __init__(self, address, port):
        Notifier.__init__(self)
        self.__socket = None
        self.__address = address
        self.__port = port

        self.startManagers()

    def start(self):
        self.__connect()
        self.waitForClients()

    def stop(self):
        if self.__socket is not None:
            try:
                self.notify.info('stopping server...')
                self.__socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                self.notify.critical('failed to stop server, socket is already closed')
                pass
            finally:
                self.__socket = None

        self.notify.info('server stopped')
        sys.exit(0)

    def accept(self):
        return self.__socket.accept()

    def __connect(self):
        try:
            self.notify.info('starting server...')
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if TLS_ENABLED:
                self.notify.info('wrapping socket in SSL')
                self.__socket = ssl.wrap_socket(socket_,
                                                server_side=True,
                                                certfile='certs/pem.crt',
                                                keyfile='certs/pem.key',
                                                ssl_version=ssl.PROTOCOL_TLSv1_3,
                                                ciphers='ECDHE-EDDSA-AES256-GCM-SHA384',
                                                do_handshake_on_connect=True)
            else:
                self.notify.info('SSL is not enabled. Do not use this in production')

            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__socket.bind((self.__address, self.__port))
            self.__socket.listen(0) # refuse unaccepted connections
            self.notify.info('server online')
        except Exception as e:
            self.notify.critical(str(e))

    def startManagers(self):
        self.cm = ClientManagerAI(self)
        self.bm = BanManagerAI(self.cm)
        self.zm = ZoneManagerAI(self)

    def waitForClients(self):
        while True:
            try:
                ai = self.cm.acceptClient()
                if ai == False:
                    # This client has been banned
                    continue
                else:
                    ai.start()
            except KeyboardInterrupt:
                self.notify.error('KeyboardInterrupt',
                                  'server killed while waiting for clients')
                break
            except ssl.SSLError as e:
                self.notify.error('SSLError', str(e))
            except Exception as e:
                self.notify.error('NetworkError', str(e))
                break
