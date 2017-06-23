import argparse
import datetime
import os
import sys
from src.base import constants

from src.base.constants import DEFAULT_ADDRESS, DEFAULT_PORT, APP_TITLE, LOG_PATH, DEBUG, INFO


class Launcher(object):

    def __init__(self):
        info = self.getLaunchInfo()
        if info.server:
            self.type = 'ai'
        else:
            self.type = 'client'

        self.__startLogging()

        if info.server:
            self.__launchAIServer(info.address, info.port)
        else:
            self.__launchClient(info.address, info.port)

    def getLogFilePath(self):
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)

        now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        path = '{0}/{1} {2}.{3}.log'.format(LOG_PATH, APP_TITLE, now, self.type)
        return path

    def getLaunchInfo(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--server',
                            dest='server',
                            action='store_true',
                            default=False,
                            help='launch server')
        parser.add_argument('-a', '--address',
                            dest='address',
                            type=str,
                            nargs='?',
                            default=DEFAULT_ADDRESS,
                            help='server address')
        parser.add_argument('-p', '--port',
                            dest='port',
                            type=int,
                            nargs='?',
                            default=DEFAULT_PORT,
                            help='server port')
        args = parser.parse_args()
        return args

    def __startLogging(self):
        if __debug__:
            self.setConfig(level=constants.DEBUG)
        else:
            self.setConfig(filename=self.getLogFilePath())

    def __launchAIServer(self, address, port):
        from src.ai.Server import Server
        from src.ai.Console import Console

        server = Server(address, port)
        console = Console(server.cm, server.bm)

        console.start()
        server.start()

    def __launchClient(self, address, port):
        from src.gui.ClientUI import ClientUI
        ClientUI(address, port).start()

    def setConfig(self, stream=None, filename=None, level=constants.INFO):
        constants.LOG_CONFIG = (stream, filename, level)


if __name__ == '__main__':
    Launcher()
