import base64
import queue
from src.base.utils import secureStrCmp
from src.base.Message import Message
from src.base.Notifier import Notifier
from src.crypto.CryptoUtils import CryptoUtils
from src.base.globals import *

class Session(Notifier):

    def __init__(self, session_id, client, *partners):
        Notifier.__init__(self)
        self.client = client
        self.__id = session_id
        self.__members = partners
        self.message_queue = queue.Queue()
        self.incoming_message_num = 0
        self.outgoing_message_num = 0
        self.crypto = CryptoUtils()
        self.crypto.generateDHKey()
        self.encrypted = False

    @property
    def id(self):
        return self.__id

    def __verifyHmac(self, hmac, data):
        generated_hmac = self.crypto.generateHmac(data)
        return secureStrCmp(generated_hmac, base64.b64decode(hmac))

    def getDecryptedData(self, message):
        if self.encrypted:
            data = message.getEncryptedDataAsBinaryString()
            enc_num = message.getMessageNumAsBinaryString()
            if not self.__verifyHmac(message.hmac, data): # check hmac
                self.notify.error(ERR_INVALID_HMAC)
            else:
                try:
                    num = int(self.crypto.aesDecrypt(enc_num))
                    if self.incoming_message_num > num:
                        self.notify.error(ERR_MESSAGE_REPLAY)
                    elif self.incoming_message_num < num:
                        self.notify.error(ERR_MESSAGE_DELETION)
                    self.incoming_message_num += 1
                    data = self.crypto.aesDecrypt(data)
                except:
                    self.notify.error(ERR_DECRYPT_FAILURE)
        else:
            return message.data
