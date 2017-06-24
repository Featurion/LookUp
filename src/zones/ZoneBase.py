import base64
import queue
import threading
import uuid

from src.base import constants
from src.base.Datagram import Datagram
from src.base.KeyHandler import KeyHandler
from src.base.Node import Node


class ZoneBase(Node):

    def __init__(self, client, zone_id: str, members: list, is_group: bool):
        Node.__init__(self)
        self.__client = client
        self.__members = members
        self.__group = is_group

        self.setId(uuid.UUID(hex=zone_id))
        self.start() # zones start on creation

    def start(self):
        Node.start(self)
        self.startThreads()

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

    def addMember(self, ai):
        """Add a member"""
        if self.isGroup:
            self.__members.append(ai)

    @property
    def isGroup(self):
        return self.__group

    def encrypt(self, datagram):
        key = self.getWorkingKey(datagram.getRecipient())

        if not key and datagram.getCommand() == constants.CMD_REDY:
            return datagram

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

    def _recv(self):
        try:
            datagram = self.getDatagramFromInbox()

            if self.isSecure:
                datagram = self.decrypt(datagram)

            self.handleReceivedDatagram(datagram)
            del datagram
            return True # successful
        except queue.Empty:
            return True # successful
        except Exception as e:
            self.notify.error('ZoneError', str(e))
            return False # unsuccessful
