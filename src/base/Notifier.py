import logging


def formatter(func):
    def wrapper(self, string, *args):
        return func(self, ' ' + string.format(*args))
    return wrapper


class Notifier(object):

    class _ChannelHandler(object):

        def __init__(self, channel):
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

        @formatter
        def error(self, msg):
            self.__channel.error(msg)

        @formatter
        def critical(self, msg):
            self.__channel.critical(msg)
            raise Exception(msg)

    @classmethod
    def generateLoggingChannel(cls, name):
        channel = logging.getLogger(name)
        return cls._ChannelHandler(channel)

    def __init__(self):
        self.__name = self.__class__.__name__
        self.notify = self.generateLoggingChannel(self.__name)
