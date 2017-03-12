import argparse
import datetime
import logging
import os
import sys
from src.ai.Server import Server
from src.base.globals import DEFAULT_ADDR, DEFAULT_PORT
from src.base.globals import LOG_PATH
from src.client.Client import Client


class Launcher(object):

    def __init__(self):
        info = self.getLaunchInfo()
        if info.server:
            self.type = 'ai'
            service = self.__launchAIServer(info.addr, info.port)
        else:
            self.type = 'client'
            service = self.__launchClient(info.addr, info.port, info.name)
        self.__startLogging()
        service.start()

    def getLogFilePath(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        return '{0}/{1}.{2}.log'.format(LOG_PATH, now, self.type)

    def getLaunchInfo(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--server',
                            dest='server',
                            action='store_true',
                            default=False,
                            help='launch server')
        parser.add_argument('-a', '--addr',
                            dest='addr',
                            type=str,
                            nargs='?',
                            default=DEFAULT_ADDR,
                            help='server address')
        parser.add_argument('-p', '--port',
                            dest='port',
                            type=int,
                            nargs='?',
                            default=DEFAULT_PORT,
                            help='server port')
        parser.add_argument('-n', '--name',
                            dest='name',
                            type=str,
                            nargs='?',
                            default='',
                            help='client username')
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

    def __launchAIServer(self, addr, port):
        return Server(addr, port)

    def __launchClient(self, addr, port, name):
        if name == '':
            return Client(addr, port, name)
        else:
            return Client(addr, port)


if __name__ == '__main__':
    Launcher()
