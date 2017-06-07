from src.base.globals import SERVER, CMD_LOGIN
from src.base.Datagram import Datagram
from src.userbase.Node import Node


class Client(Node):

    def __init__(self, interface, address, port):
        Node.__init__(self, address, port, None)
        self.interface = interface

    def start(self):
        Node.start(self)
        self.interface.connected_signal.emit()

    def stop(self):
        Node.stop(self)
        self.interface.stop()

    def startManagers(self):
        return NotImplemented

    def enter(self, tab, id_):
        return NotImplemented

    def exit(self, id_):
        return NotImplemented

    def __sendProtocolVersion(self):
        # log: INFO, 'using protocol version: {}'
        # send message
        return int(self.getResp()) # confirmation
