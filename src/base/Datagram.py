import json

from src.base import utils


class Datagram(object):

    def __init__(self):
        self.__command = int()
        self.__sender = int()
        self.__recipient = int()
        self.__data = str()
        self.__hmac = str()
        self.__errno = int()
        self.__ts = utils.getTimestamp()

    def getCommand(self):
        return self.__command

    def setCommand(self, command):
        self.__command = command

    def getSender(self):
        return self.__sender

    def setSender(self, id_):
        self.__sender = id_

    def getRecipient(self):
        return self.__recipient

    def setRecipient(self, id_):
        self.__recipient = id_

    def getData(self):
        return self.__data

    def setData(self, data):
        self.__data = data

    def getHMAC(self):
        return self.__hmac

    def setHMAC(self, hmac):
        self.__hmac = hmac

    def getErrno(self):
        return self.__errno

    def setErrno(self, errno):
        self.__errno = errno

    def getTimestamp(self):
        return self.__ts

    def setTimestamp(self, ts):
        self.__ts = ts

    @staticmethod
    def fromJSON(str_):
        obj = json.loads(str_)

        datagram = Datagram()
        datagram.setCommand(obj['command'])
        datagram.setSender(obj['sender'])
        datagram.setRecipient(obj['recipient'])
        datagram.setData(obj['data'])
        datagram.setHMAC(obj['hmac'])
        datagram.setErrno(obj['errno'])
        datagram.setTimestamp(obj['time'])

        return datagram

    def toJSON(self):
        return json.dumps({
            'command': self.getCommand(),
            'sender': self.getSender(),
            'recipient': self.getRecipient(),
            'data': self.getData(),
            'hmac': self.getHMAC(),
            'errno': self.getErrno(),
            'time': self.getTimestamp(),
        })
