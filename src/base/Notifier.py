import sys
import time

from contextlib import redirect_stdout

from src.base.constants import DEBUG, INFO, WARNING, EXCEPTION, LOG_CONFIG, LOG_PATH

def upperfirst(x):
    return x[0].upper() + x[1:]

class Channel(object):

    def __init__(self, stream=None, filename=None, level=INFO):
        self.__stream = stream
        self.__filename = filename
        self.__level = level

        if self.__stream == None:
            self.__log_type = self.__filename
        elif self.__filename == None:
            self.__log_type = self.__stream
        else:
            self.__log_type = sys.stdout

        if self.__log_type == None:
            self.__log_type = sys.stdout

    def debug(self, msg):
        if self.__level <= DEBUG:
            self.writeLog(msg)

    def info(self, msg):
        if self.__level <= INFO:
            self.writeLog(msg)

    def warning(self, msg):
        if self.__level <= WARNING:
            self.writeLog(msg)

    def exception(self, module, err='CRITICAL', type='', msg=''):
        if self.__level <= EXCEPTION:
            fullMessage = ('LookUpException: ' + module + ': ' + err + ': ' + msg + '!')
            self.writeLog(fullMessage)

    def __fileWrite(self, msg):
        with open(self.__filename, 'a') as f:
            with redirect_stdout(f):
                print(msg)
                f.flush()

    def writeLog(self, message):
        if self.__log_type == self.__filename:
            self.__fileWrite(message)
        else:
            message += "\n"
            self.__log_type.write(message)

class Notifier(object):

    class _Logger(object):

        def __init__(self, channel, parent):
            self.__parent = parent
            self.__channel = channel

        def debug(self, msg):
            msg = upperfirst(msg)
            msg = ("[" + self.debug.__name__.upper() + "] " + self.__parent + ": " + msg)
            self.__channel.debug(msg)

        def info(self, msg):
            msg = upperfirst(msg)
            msg = ("[" + self.info.__name__.upper() + "] " + self.__parent + ": " + msg)
            self.__channel.info(msg)

        def warning(self, msg):
            msg = upperfirst(msg)
            msg = ("[" + self.warning.__name__.upper() + "] " + self.__parent + ": " + msg)
            self.__channel.warning(msg)

        def error(self, err, msg):
            msg = upperfirst(msg)
            self.__channel.exception(self.__parent, err, msg=msg)

        def critical(self, msg):
            msg = upperfirst(msg)
            self.__channel.exception(self.__parent, msg=msg)
            sys.exit(1)

    @classmethod
    def generateLogger(cls, name, parent):
        stream, filename, level = LOG_CONFIG
        channel = Channel(stream, filename, level)
        return cls._Logger(channel, parent)

    def __init__(self):
        self.__name = str(' ' + self.__class__.__name__)
        self.notify = self.generateLogger(self.__name,
                                                  self.__class__.__name__)
