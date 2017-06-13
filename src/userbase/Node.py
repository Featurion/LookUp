import os

from src.base.globals import CMD_RESP, CMD_RESP_OK, CMD_RESP_NO
from src.base.Datagram import Datagram
from src.userbase.NodeBase import NodeBase


class Node(NodeBase):

    def start(self):
        """Begin managing node requests"""
        NodeBase.start(self)
        self.doHandshake()
        self.notify.info('secured connection to server')

    def stop(self):
        if NodeBase.stop(self):
            self.notify.debug('stopped client')
        else:
            self.terminate()

    def terminate(self):
        self.notify.info('failed to quit, force quitting')
        os.kill(os.getpid(), 9)

    def _send(self):
        datagram = self.getDatagram()
        return datagram.toJSON()

    def _recv(self, data):
        datagram = Datagram.fromJSON(data)

        if datagram.getCommand() == CMD_RESP:
            self.setResp(datagram.getData())
        elif datagram.getCommand() == CMD_RESP_OK:
            self.setResp(True)
        elif datagram.getCommand() == CMD_RESP_NO:
            self.setResp(False)
        else:
            pass

        return data
