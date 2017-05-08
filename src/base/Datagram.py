import base64
import json
from src.base.globals import SERVER_ID

class Datagram(object):

    def __init__(self):
        self.__command = int()
        self.__from_id = str()
        self.__to_id = str()
        self.__data = str()
        self.__hmac = str()
        self.__err = str()
        self.__time = str()

    def toJson(self):
        return json.dumps({
            'command': self.__command,
            'from_id': self.__from_id,
            'to_id': self.__to_id,
            'data': self.__data,
            'hmac': self.__hmac,
            'err': self.__err,
            'time': self.__time,
        })

    @staticmethod
    def fromJson(s):
        js = json.loads(s)

        # Initialize a Datagram object
        datagram = Datagram()

        # Set all of the args to the contents of the json
        datagram.setCommand(js['command'])
        datagram.setFromId(js['from_id'])
        datagram.setToId(js['to_id'])
        datagram.setErr(js['err'])
        datagram.setTime(js['time'])

        # Then, add the data and the hmac
        datagram.addData(js['data'])
        datagram.addHmac(js['hmac'])

        # Finally, return the datagram
        return datagram

    def setCommand(self, command):
        self.__command = command

    def setFromId(self, from_id):
        self.__from_id = from_id

    def setToId(self, to_id):
        self.__to_id = to_id

    def setErr(self, err):
        self.__err = err

    def setTime(self, time):
        self.__time = time

    def addData(self, data, enc=False):
        if enc:
            self.__data = base64.b64encode(data).decode()
        else:
            self.__data = data

    def addHmac(self, hmac, enc=False):
        if enc:
            self.__hmac = base64.b64encode(hmac).decode()
        else:
            self.__hmac = hmac

    def getCommand(self):
        return self.__command

    def getFromId(self):
        return self.__from_id

    def getToId(self):
        return self.__to_id

    def getData(self, raw=False):
        if raw:
            return base64.b64decode(self.__data)
        else:
            return self.__data

    def getHmac(self, raw=False):
        if raw:
            return base64.b64decode(self.__hmac)
        else:
            return self.__hmac