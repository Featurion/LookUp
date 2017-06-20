import json
import srp

from src.base import utils
from src.base.constants import CMD_LOGIN, CMD_RESP, CMD_RESP_OK, CMD_RESP_NO, CMD_REQ_CHALLENGE, CMD_RESP_CHALLENGE, CMD_VERIFY_CHALLENGE
from src.base.constants import CMD_REQ_ZONE, CMD_ZONE_MSG
from src.base.constants import HMAC_KEY
from src.base.constants import SYSTEM
from src.base.Datagram import Datagram
from src.users.ClientBase import ClientBase


class ClientAI(ClientBase):

    def __init__(self, server, address, port, socket_):
        ClientBase.__init__(self, address, port)
        self.server = server
        self.setupSocket(socket_)

    def start(self):
        """Handle startup of the client"""
        ClientBase.start(self)
        self.initiateHandshake()

    def stop(self):
        """Handle stopping of the client"""
        self.server.cm.removeClient(self)
        ClientBase.stop(self)

    def initiateHandshake(self):
        self.sendKey()
        self.receiveKey()

    def sendResp(self, data):
        datagram = Datagram()
        datagram.setCommand(CMD_RESP)
        datagram.setRecipient(self.getId())
        datagram.setData(data)

        self.sendDatagram(datagram)

    def sendOK(self):
        datagram = Datagram()
        datagram.setCommand(CMD_RESP_OK)
        datagram.setRecipient(self.getId())

        self.sendDatagram(datagram)

    def sendNo(self):
        datagram = Datagram()
        datagram.setCommand(CMD_RESP_NO)
        datagram.setRecipient(self.getId())

        self.sendDatagram(datagram)

    def _recv(self, data):
        datagram = Datagram.fromJSON(data)

        if datagram.getCommand() == CMD_LOGIN:
            name, mode = json.loads(datagram.getData())
            client_hmac = datagram.getHMAC()
            server_hmac = self.generateHmac(name.encode(), HMAC_KEY, True)
            if server_hmac == client_hmac: # valid hmac
                pass
            else:
                self.notify.warning('received suspicious improper hmac')
                self.sendNo()
                return
            if not utils.isNameInvalid(name): # valid name
                self.setName(name)
                self.setMode(mode)
                self.server.cm.addClient(self)
                self.sendResp('')
            else:
                self.sendNo()
        elif datagram.getCommand() == CMD_REQ_CHALLENGE:
            uname, A = datagram.getData()
            uname = uname.encode('latin-1')
            A = A.encode('latin-1')
            salt, vkey = srp.create_salted_verification_key(self.getName().encode(), HMAC_KEY)
            self.svr = srp.Verifier(uname, salt, vkey, A)
            s, B = self.svr.get_challenge()

            if s is None or B is None:
                self.notify.warning('suspicious challenge failure')
                self.sendNo()
                return

            datagram.setCommand(CMD_RESP_CHALLENGE)
            datagram.setData((s.decode('latin-1'), B.decode('latin-1')))
            self.sendDatagram(datagram)
        elif datagram.getCommand() == CMD_RESP_CHALLENGE:
            M = datagram.getData()
            M = M.encode('latin-1')

            HAMK = self.svr.verify_session(M)

            if HAMK is None:
                self.notify.warning('suspicious challenge failure')
                self.sendNo()
                return

            if self.svr.authenticated():
                pass # authenticated
            else:
                self.notify.warning('suspicious challenge failure')
                self.sendNo()
                return

            datagram.setCommand(CMD_VERIFY_CHALLENGE)
            datagram.setData(HAMK.decode('latin-1'))
            self.sendDatagram(datagram)
        elif datagram.getCommand() == CMD_REQ_ZONE:
            ai = self.server.zm.addZone(self, json.loads(datagram.getData()))
            ai.sendHelo()
        elif datagram.getCommand() == CMD_ZONE_MSG:
            ai = self.server.zm.getZoneById(datagram.getRecipient())
            ai.recvDatagram(datagram)
        else:
            self.notify.warning('received suspicious datagram')

        return datagram
