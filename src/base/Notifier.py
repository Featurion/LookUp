import sys

from src.base.constants import DEBUG, INFO, WARNING, EXCEPTION, LOG_CONFIG, LOG_FORMAT

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
            self.__log_type = print

        if self.__log_type == None:
            self.__log_type = print

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
            f.write(msg + "\n")
            f.flush()

    def writeLog(self, message):
        if self.__log_type == self.__filename:
            self.__fileWrite(message)
        else:
            self.__log_type(message)


class Notifier(object):

    class _Logger(object):

        def __init__(self, channel, name):
            self.__name = name
            self.__channel = channel

        def format(self, msg_type, msg):
            log_format = LOG_FORMAT
            if log_format == 'inbracket':
                return '[{0}] {1}: {2}'.format(msg_type.upper().ljust(7),
                                               self.__name,
                                               msg[:1].upper() + msg[1:])
            elif log_format == 'outbracket':
                width = 7
                padding = width - len(msg_type)
                return '[{0}] {1} {2}: {3}'.format(msg_type.upper(),
                                               ''.ljust(padding),
                                               self.__name,
                                               msg[:1].upper() + msg[1:])
            else:
                return '[{0}] {1}: {2}'.format(msg_type.upper(),
                                               self.__name,
                                               msg[:1].upper() + msg[1:])

        def debug(self, msg):
            self.__channel.debug(self.format('debug', msg))

        def info(self, msg):
            self.__channel.info(self.format('info', msg))

        def warning(self, msg):
            self.__channel.warning(self.format('warning', msg))

        def error(self, err, msg):
            self.__channel.exception(self.__name, err, msg=msg.capitalize())

        def critical(self, msg):
            self.__channel.exception(self.__name, msg=msg.capitalize())
            sys.exit(1)

    def __init__(self):
        self.notify = self._Logger(Channel(*LOG_CONFIG),
                                   self.__class__.__name__)
