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

        self.notify.info('logging in as {0}'.format(name))
        self.sendDatagram(datagram)

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

        self.notify.debug('requesting new zone')
        self.sendDatagram(datagram)

        zone = self.getResp()
        if zone:
            tab.setZone(zone)
        else:
            self.notify.info('new zone rejected')

    def __sendProtocolVersion(self):
        self.notify.info('using protocol version {0}'.format(self.getResp()))
        # send message
        return int(self.getResp()) # confirmation
