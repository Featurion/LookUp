import base64
import queue
import threading

from src.base import constants
from src.base.Datagram import Datagram
from src.base.KeyHandler import KeyHandler
from src.base.Node import Node


class ZoneBase(Node):

    def __init__(self, client, zone_id, members):
        Node.__init__(self)
        self.__client = client
        self.__members = members
        self.id2key = {} # overwrite in subclass
        self.is_secure = False

        self.setId(zone_id)
        self.start() # zones start on creation

    def getClient(self):
        """Getter for client"""
        return self.__client

    def getMembers(self):
        """Getter for zone members"""
        return self.__members

    def encrypt(self, datagram):
        key = self.getWorkingKey(datagram.getRecipient())
        if key and self.is_secure:
            self.generateSecret(key)

            data = Node.encrypt(self, datagram.toJSON())
            data = base64.b85encode(data).decode()

            datagram = Datagram()
            datagram.setCommand(constants.CMD_ZONE_MSG)
            datagram.setSender(self.getId())
            datagram.setRecipient(self.getId())
            datagram.setData(data)

        return datagram

    def decrypt(self, datagram):
        key = self.getWorkingKey(datagram.getSender())
        if key:
            self.generateSecret(key)

            data = base64.b85decode(datagram.getData())
            data = Node.decrypt(self, data)
            return Datagram.fromJSON(data)

        return datagram

    def buildZoneDatagram(self, command, id_, data=None):
        datagram = Datagram()
        datagram.setCommand(command)
        datagram.setSender(self.getClient().getId())
        datagram.setRecipient(id_)
        datagram.setData(data)

        return self.encrypt(datagram)

    def _send(self):
        try:
            datagram = self.getDatagramFromOutbox()
            Node.sendDatagram(self.client, datagram)
            return None
        except Exception as e:
            self.notify.error('ZoneError', str(e))
            return False

    def _recv(self):
        try:
            datagram = self.getDatagramFromInbox()
            self.handleReceivedDatagram(datagram)
            return None
        except Exception as e:
            self.notify.error('ZoneError', str(e))
            return False

    def sendDatagram(self, datagram):
        self.getClient().sendDatagram(datagram)
