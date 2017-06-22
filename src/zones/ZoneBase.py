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

        self.setId(zone_id)
        self.start() # zones start on creation

        del client
        del zone_id
        del members

    def cleanup(self):
        Node.cleanup()
        if self.__client:
            del self.__client
            self.__client = None
        if self.__members:
            del self.__members[:]
            del self.__members
            self.__members = None

    def getClient(self):
        """Getter for client"""
        return self.__client

    def getMembers(self):
        """Getter for zone members"""
        return self.__members

    def encrypt(self, datagram):
        key = self.getWorkingKey(datagram.getRecipient())
        if key and self.isSecure:
            self.generateSecret(key)

            data = Node.encrypt(self, datagram.toJSON())
            data = base64.b85encode(data).decode()

            datagram = Datagram()
            datagram.setCommand(constants.CMD_ZONE_MSG)
            datagram.setSender(self.getId())
            datagram.setRecipient(self.getId())
            datagram.setData(data)

            del data
        del key

        return datagram

    def decrypt(self, datagram):
        key = self.getWorkingKey(datagram.getSender())
        if key:
            self.generateSecret(key)

            data = base64.b85decode(datagram.getData())
            data = Node.decrypt(self, data)
            return Datagram.fromJSON(data)
        del key

        return datagram

    def buildZoneDatagram(self, command, id_, data=None):
        datagram = Datagram()
        datagram.setCommand(command)
        datagram.setSender(self.getClient().getId())
        datagram.setRecipient(id_)
        datagram.setData(data)

        del command
        del id_
        del data

        return self.encrypt(datagram)

    def _send(self):
        try:
            datagram = self.getDatagramFromOutbox()
            Node.sendDatagram(self.client, datagram)
            del datagram
            return None
        except Exception as e:
            self.notify.error('ZoneError', str(e))
            return False

    def _recv(self):
        try:
            datagram = self.getDatagramFromInbox()
            self.handleReceivedDatagram(datagram)
            del datagram
            return None
        except Exception as e:
            self.notify.error('ZoneError', str(e))
            return False

    def handleReceivedDatagram(self, datagram):
        if self.isSecure:
            return self.decrypt(datagram)
        else:
            return datagram

    def sendDatagram(self, datagram):
        self.getClient().sendDatagram(datagram)
