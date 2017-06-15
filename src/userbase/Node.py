import json
import os

from src.base.globals import CMD_RESP, CMD_RESP_OK, CMD_RESP_NO
from src.base.globals import CMD_HELO, CMD_REDY
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

    def sendRedy(self, zone_id):
        datagram = Datagram()
        datagram.setCommand(CMD_REDY)
        datagram.setSender(self.getId())
        datagram.setRecipient(zone_id)
        datagram.setData(self.getKey())

        self.sendDatagram(datagram)
        self.notify.debug('redy in zone {0}'.format(zone_id))

    def _send(self):
        datagram = self.getDatagram()
        return datagram.toJSON()

    def _recv(self, data):
        datagram = Datagram.fromJSON(data)

        if datagram.getRecipient() != self.getId():
            self.notify.critical('received suspicious datagram: {0}'.format(datagram.toJSON()))

        if datagram.getCommand() == CMD_RESP:
            self.setResp(datagram.getData())
        elif datagram.getCommand() == CMD_RESP_OK:
            self.setResp(True)
        elif datagram.getCommand() == CMD_RESP_NO:
            self.setResp(False)
        elif datagram.getCommand() == CMD_HELO:
            zone_id = datagram.getSender()
            self.notify.debug('received helo from zone {0}'.format(zone_id))

            member_ids, member_names = json.loads(datagram.getData())

            if not self.zone_manager.getZoneById(zone_id):
                self.interface.getWindow().new_client_signal.emit(str(zone_id),
                                                                  member_ids,
                                                                  member_names)
            else:
                self.sendRedy(zone_id)
        elif datagram.getCommand() == CMD_REDY:
            zone = self.zone_manager.getZoneById(datagram.getSender())
            if zone:
                id_, key = json.loads(datagram.getData())
                zone.redy(id_, key)
        else:
            pass

        return data
