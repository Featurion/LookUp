import os

from src.base.globals import SERVER, CMD_LOGIN, CMD_RESP_OK, CMD_RESP_NO
from src.base.Datagram import Datagram
from src.userbase.NodeBase import NodeBase


class Node(NodeBase):

    def start(self):
        """Begin managing node requests"""
        NodeBase.start(self)
        self.doHandshake()
        # log: 'secured connection to server'

    def stop(self):
        if NodeBase.stop(self):
            # log: DEBUG, 'done'
            pass
        else:
            self.terminate()

    def terminate(self):
        # log: INFO, 'force quitting'
        os.kill(os.getpid(), 9)

    def connect(self, name, callback):
        datagram = Datagram()
        datagram.setCommand(CMD_LOGIN)
        datagram.setRecipient(SERVER)
        datagram.setData(name)

        # log: 'logging in as {name}'
        self.sendMessage(datagram)

        success = self.getResp()
        if success:
            self._NodeBase__setName(name)
            callback('')
        else:
            callback('placeholder rejection message') # replace

    def _send(self):
        datagram = self.getMessage()
        return datagram.toJSON()

    def _recv(self, data):
        datagram = Datagram.fromJSON(data)

        if datagram.getCommand() == CMD_RESP_OK:
            self.setResp(True)
        elif datagram.getCommand() == CMD_RESP_NO:
            self.setResp(False)
        else:
            pass

        return data
