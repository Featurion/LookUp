import json
from src.base.Message import Message
from src.base.Notifier import Notifier
from src.base.globals import COMMAND_HELO, COMMAND_REDY
from src.base.globals import ERR_CONN_REJECTED, ERR_BAD_HANDSHAKE
from src.sessions.Session import Session


class PrivateSession(Session, Notifier):

    def __init__(self, session_id, client, partner_id):
        Session.__init__(self, session_id, client, partner_id)
        Notifier.__init__(self)
        self.partner = partner_id
        self.handshake_done = False
        self.smp = None
        self.smp_step_1 = None

    def start(self):
        data = json.dumps([self.client.id], ensure_ascii=True)
        self.sendMessage(COMMAND_HELO, data)
        self.__getHandshakeMessageData(COMMAND_REDY)

    def join(self):
        self.sendMessage(COMMAND_REDY)

    def __getHandshakeMessageData(self, expected):
        message = self.message_queue.get()
        if message.command != expected:
            # Client ended
            if message.command == COMMAND_END:
                self.stop() # TODO: Zach
            # Client rejected connection
            elif message.command == COMMAND_REJECT:
                self.notify.error(ERR_CONN_REJECTED)
            # Handshake failed
            else:
                self.notify.error(ERR_BAD_HANDSHAKE, message.from_id)
        else:
            _data = self.getDecryptedData(message)
            self.message_queue.task_done()
            return _data

    def sendMessage(self, command, data=None):
        message = Message(command, self.id, self.partner)
        if (data is not None) and self.encrypted:
            enc_data = self.crypto.aesEncrypt(data)
            num = self.crypto.aesEncrypt(str(self.outgoing_message_num).encode())
            hmac = self.crypto.generateHmac(enc_data)
            message.setEncryptedData(enc_data)
            message.setBinaryHmac(hmac)
            message.setBinaryMessageNum(num)
            self.outgoing_message_num += 1
        elif data is not None:
            message.data = data
        else:
            pass
        self.client.sendMessage(message)

    def stop(self): # TODO
        pass
