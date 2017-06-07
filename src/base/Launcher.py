import argparse
import datetime
import logging
import os
import sys
from src.base.globals import DEFAULT_ADDRESS, DEFAULT_PORT, LOG_PATH


class Launcher(object):

    def __init__(self):
        self.__startLogging()

        info = self.getLaunchInfo()
        if info.server:
            self.type = 'ai'
            self.__launchAIServer(info.address, info.port)
        else:
            self.type = 'client'
            self.__launchClient(info.address, info.port)

    def getLogFilePath(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        path = '{0}/{1}.{2}.log'.format(LOG_PATH, now, self.type)
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
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)

        if __debug__:
            logging.basicConfig(stream=sys.stdout,
                                level=logging.DEBUG)
        else:
            logging.basicConfig(filename=self.getLogFilePath(),
                                level=logging.ERROR)

    def __launchAIServer(self, address, port):
        from src.ai.Server import Server
        Server(address, port).start()

    def __launchClient(self, address, port):
        from src.gui.ClientUI import ClientUI
        ClientUI(address, port).start()


if __name__ == '__main__':
    Launcher()
