import json

from src.base import utils
from src.base.globals import CMD_LOGIN, CMD_RESP, CMD_RESP_OK, CMD_RESP_NO
from src.base.globals import CMD_REQ_ZONE, CMD_ZONE_MSG
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
        datagram.setCommand(CMD_RESP_OK)
        datagram.setRecipient(self.getId())

        self.sendDatagram(datagram)

    def _recv(self, data):
        datagram = Datagram.fromJSON(data)

        if datagram.getCommand() == CMD_LOGIN:
            name, mode = json.loads(datagram.getData())
            if not utils.isNameInvalid(name): # valid name
                self.setName(name)
                self.setMode(mode)
                self.server.cm.addClient(self)
                self.sendOK()
            else:
                self.sendNo()
        elif datagram.getCommand() == CMD_REQ_ZONE:
            ai = self.server.zm.addZone(self, json.loads(datagram.getData()))
            ai.sendHelo()
        elif datagram.getCommand() == CMD_ZONE_MSG:
            # send to zone inbox
            pass
        else:
            self.notify.warning('received suspicious datagram')

        return datagram
