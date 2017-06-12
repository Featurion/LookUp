import json

from src.base.globals import CMD_LOGIN, CMD_REQ_ZONE
from src.base.Datagram import Datagram
from src.userbase.Node import Node


class Client(Node):

    def __init__(self, interface, address, port):
        Node.__init__(self, address, port, None)
        self.interface = interface

    def start(self):
        Node.start(self)
        self.interface.connected_signal.emit()

    def connect(self, name, callback):
        datagram = Datagram()
        datagram.setCommand(CMD_LOGIN)
        datagram.setRecipient(self.getId())
        datagram.setData(name)

        # log: 'logging in as {name}'
        self.sendMessage(datagram)

        if self.getResp():
            self.setName(name)
            callback('')
        else:
            callback('placeholder rejection message') # replace

    def requestNewZone(self, tab, members):
        datagram = Datagram()
        datagram.setCommand(CMD_REQ_ZONE)
        datagram.setRecipient(self.getId())
        datagram.setData(json.dumps([self.getName()] + members))

        # log: 'requesting new zone'
        self.sendMessage(datagram)

        zone = self.getResp()
        if zone:
            tab.setZone(zone)
        else:
            # log: 'new zone rejected'
            pass

    def __sendProtocolVersion(self):
        # log: INFO, 'using protocol version: {}'
        # send message
        return int(self.getResp()) # confirmation
