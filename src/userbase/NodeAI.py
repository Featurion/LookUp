import base64

from src.base import utils
from src.base.globals import CMD_LOGIN, CMD_RESP_OK, CMD_RESP_NO
from src.base.Datagram import Datagram
from src.userbase.NodeBase import NodeBase


class NodeAI(NodeBase):

    def start(self):
        """Begin node connection"""
        NodeBase.start(self)
        self.initiateHandshake()

    def _send(self):
        datagram = self.getMessage()
        return datagram.toJSON()

    def _recv(self, data):
        datagram = Datagram.fromJSON(data)

        if datagram.getCommand() == CMD_RESP_OK:
            self.setResp(True)
        elif datagram.getCommand() == CMD_RESP_NO:
            self.setResp(False)
        elif datagram.getCommand() == CMD_LOGIN:
            name = datagram.getData()
            if not utils.isNameInvalid(name): # valid name
                self.sendOK()
            else:
                self.sendNo()
        else:
            pass

        return datagram
