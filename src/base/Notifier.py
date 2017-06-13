import logging
import sys


def upperfirst(x):
    return x[0].upper() + x[1:]


def formatter(func=''):
    def wrapper(self, string, *args):
        string = upperfirst(string)
        return func(self, ' ' + string.format(*args))
    return wrapper


class LookUpException(object):

    def __init__(self, module, err=None, type='', msg=''):
        module = ' ' + module
        if err:
            logging.critical(module + ': ' + err + ': ' + msg)
        else:
            logging.critical(module + ': ' + msg)


class Notifier(object):

    class _ChannelHandler(object):

        def __init__(self, channel, parent):
            self.parent = parent
            self.__channel = channel

        @formatter
        def debug(self, msg):
            self.__channel.debug(msg)

        @formatter
        def info(self, msg):
            self.__channel.info(msg)

        @formatter
        def warning(self, msg):
            self.__channel.warning(msg)

        def error(self, err, msg):
            msg = upperfirst(msg)
            LookUpException(self.parent, err, msg=msg)

        def critical(self, msg):
            msg = upperfirst(msg)
            LookUpException(self.parent, msg=msg)
            sys.exit(1)

    @classmethod
    def generateLoggingChannel(cls, name, parent):
        channel = logging.getLogger(name)
        return cls._ChannelHandler(channel, parent)

    def __init__(self):
        self.__name = str(' ' + self.__class__.__name__)
        self.notify = self.generateLoggingChannel(self.__name,
                                                  self.__class__.__name__)
