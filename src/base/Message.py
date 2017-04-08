import base64
import json
from src.base.globals import SERVER_ID


class Message(object):

    def __init__(self, command, from_id=SERVER_ID, to_id=SERVER_ID, data='',
                 hmac='', err='', num=''):
        self.command = int(command)
        self.from_id = str(from_id)
        self.to_id = str(to_id)
        self.data = str(data)
        self.hmac = str(hmac)
        self.err = str(err)

    def toJson(self):
        return json.dumps({
            'command': self.command,
            'from_id': self.from_id,
            'to_id': self.to_id,
            'data': self.data,
            'hmac': self.hmac,
            'err': self.err,
        })

    @staticmethod
    def fromJson(s):
        js = json.loads(s)
        return Message(
            js['command'],
            js['from_id'],
            js['to_id'],
            js['data'],
            js['hmac'],
            js['err'],
        )

    def getEncryptedDataAsBinaryString(self):
        return base64.b64decode(self.data)

    def setEncryptedData(self, data):
        self.data = base64.b64encode(data).decode()

    def getHmacAsBinaryString(self):
        return base64.b64decode(self.hmac)

    def setBinaryHmac(self, hmac):
        self.hmac = base64.b64encode(hmac).decode()
