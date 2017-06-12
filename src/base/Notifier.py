import logging
import sys

def formatter(func):
    def wrapper(self, string, *args):
        return func(self, ' ' + string.format(*args))
    return wrapper

def upperfirst(x):
    return x[0].upper() + x[1:]

class LookupException(object):
    def __init__(self, module, err='CRITICAL', type='', msg='', exit=0):
        print('LookupException: ' + module + ': ' + err + ':' + msg + '!')
        if exit:
            sys.exit(1)

class Notifier(object):
    class _ChannelHandler(object):
        def __init__(self, channel, parent):
            self.parent = parent
            self.__channel = channel

        @formatter
        def debug(self, msg):
            msg = upperfirst(msg)
            self.__channel.debug(msg)

        @formatter
        def info(self, msg):
            msg = upperfirst(msg)
            self.__channel.info(msg)

        @formatter
        def warning(self, msg):
            msg = upperfirst(msg)
            self.__channel.warning(msg)

        @formatter
        def error(self, err='ERROR', msg):
            msg = upperfirst(msg)
            LookupException(self.parent, err, msg=msg, exit=0)

        @formatter
        def critical(self, msg):
            msg = upperfirst(msg)
            LookupException(self.parent, msg=msg, exit=1)

    @classmethod
    def generateLoggingChannel(cls, name, parent):
        channel = logging.getLogger(name)
        return cls._ChannelHandler(channel, parent)

    def __init__(self):
        self.__name = str(' ' + self.__class__.__name__)
        self.notify = self.generateLoggingChannel(self.__name, self.__class__.__name__)