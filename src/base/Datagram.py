import json

class Datagram(object):

    def __init__(self):
        self.__id = str()
        self.__command = int()
        self.__sender = int()
        self.__recipient = int()
        self.__data = None
        self.__hmac = str()

    def getId(self):
        return self.__id

    def _setId(self, id_):
        self.__id = id_

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

    @staticmethod
    def fromJSON(str_):
        obj = json.loads(str_)

        datagram = Datagram()
        datagram._setId(obj['id'])
        datagram.setCommand(obj['command'])
        datagram.setSender(obj['sender'])
        datagram.setRecipient(obj['recipient'])
        datagram.setData(obj['data'])
        datagram.setHMAC(obj['hmac'])

        return datagram

    def toJSON(self):
        data = self.getData()
        hmac = self.getHMAC()
        if isinstance(data, bytes):
            data = data.decode('latin-1')
        if isinstance(hmac, bytes):
            hmac = hmac.decode('latin-1')
        return json.dumps({
            'id': self.getId(),
            'command': self.getCommand(),
            'sender': self.getSender(),
            'recipient': self.getRecipient(),
            'data': data,
            'hmac': hmac,
        })
