import base64
import json

from src.base import utils
from src.base.globals import CMD_LOGIN, CMD_RESP_OK, CMD_RESP_NO, CMD_REQ_ZONE
from src.base.Datagram import Datagram
from src.userbase.NodeBase import NodeBase


class NodeAI(NodeBase):

    def __init__(self,
                 client_manager, zone_manager,
                 address, port, socket_, id_):
        NodeBase.__init__(self, address, port, socket_, id_)
        self.client_manager = client_manager
        self.zone_manager = zone_manager

    def start(self):
        """Begin node connection"""
        NodeBase.start(self)
        self.initiateHandshake()

    def stop(self):
        """Close node connection"""
        self.client_manager.removeClient(self)
        NodeBase.stop(self)

    def setName(self, name):
        NodeBase.setName(self, name)
        self.client_manager.name2owner[name] = self

    def _send(self):
        datagram = self.getDatagram()
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
                self.setName(name)
                self.sendOK()
            else:
                self.sendNo()
        elif datagram.getCommand() == CMD_REQ_ZONE:
            members = json.loads(datagram.getData())
            ai = self.zone_manager.addZone(members)
            self.sendResp(ai.getId())
        else:
            pass

        return datagram
