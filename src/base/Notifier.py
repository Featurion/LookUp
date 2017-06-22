from _io import TextIOWrapper
import sys

from src.base import constants


class _Message(object):

    def __init__(self, msg: str, level: int, parent: str):
        self.__text = msg
        self.__parent = parent

        level = constants.MsgLevel2Name[level]

        if constants.LOG_FORMAT == 'inbracket':
            level = level.upper().ljust(7)

        self.__prefix = '[' + level + '] '

        if constants.LOG_FORMAT == 'outbracket':
            self.__prefix += ' ' * (10 - len(level))

    def __str__(self):
        return self.__text

    @property
    def formatted(self):
        return self.__prefix \
               + self.__parent \
               + ': ' \
               + self.__text[:1].upper() + self.__text[1:]


class Channel(object):

    def __init__(self, stream=None, filename=None, level=None):
        if stream and not filename:
            self.__log = stream
        elif filename:
            self.__log = open(filename, 'a')
        else:
            self.__log = None

        if level:
            self.__level = level
        else:
            self.__level = constants.LOG_LEVEL

    def cleanup(self):
        if self.__log:
            if hasattr(self.__log, 'close'):
                self.__log.close()
            del self.__log
            self.__log = None

    def log(self, msg, level, parent):
        if self.__level > level:
            return
        else:
            msg = _Message(msg, level, parent)
            if constants.WANT_LOG_FORMATTING is True:
                self.__write(msg.formatted)
            else:
                self.__write(msg)

        del msg
        del level
        del parent

    def exception(self, parent, msg, err='CRITICAL'):
        self.__write(_Message(parent + ': ' + err + ': ' + msg,
                              constants.EXCEPTION,
                              'LookUpException: '))

        del parent
        del msg
        del err

    def __write(self, msg):
        if isinstance(self.__log, TextIOWrapper):
            self.__log.write(msg + "\n")
            self.__log.flush()
        elif self.__log:
            self.__log.write(msg)
        else:
            print(msg)

        del msg


class Notifier(object):

    class _Logger(object):

        def __init__(self, channel, name):
            self.__name = name
            self.__channel = channel

        def cleanup(self):
            self.__name = None
            if self.__channel:
                self.__channel.cleanup()
                del self.__channel
                self.__channel = None

        def setChannelName(self, name):
            self.__name = name
            del name

        def debug(self, msg):
            self.__channel.log(msg, constants.DEBUG, self.__name)
            del msg

        def info(self, msg):
            self.__channel.log(msg, constants.INFO, self.__name)
            del msg

        def warning(self, msg):
            self.__channel.log(msg, constants.WARNING, self.__name)
            del msg

        def error(self, err, msg):
            self.__channel.exception(self.__name, msg, err)
            del err
            del msg

        def critical(self, msg):
            self.__channel.exception(self.__name, msg)
            sys.exit(1)

    def __init__(self):
        self.notify = self._Logger(Channel(*constants.LOG_CONFIG),
                                   self.__class__.__name__)

    def cleanup(self):
        self.notify.cleanup()
        del self.notify
        self.notify = None

    def updateLoggingName(self, name):
        self.notify.setChannelName(name)
        del name
