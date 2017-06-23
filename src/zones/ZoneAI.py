import base64
import queue

from src.base import constants
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase


class ZoneAI(ZoneBase):

    def __init__(self, client, zone_id, members, is_group):
        ZoneBase.__init__(self, client, zone_id, members, is_group)
        self.__id2key = {ai.getId(): None for ai in members}

        self.COMMAND_MAP.update({
            constants.CMD_REDY: self.clientRedy,
        })

    def cleanup(self):
        ZoneBase.cleanup(self)
        if hasattr(self, '__id2key') and self.__id2key:
            self.__id2key.clear()
            del self.__id2key
            self.__id2key = Non

    def getMemberIds(self):
        return [ai.getId() for ai in self.getMembers()]

    def getMemberById(self, id_):
        for ai in self.getMembers():
            if ai.getId() == id_:
                return ai
        return None

    def getWorkingKey(self, id_):
        return self.__id2key.get(id_)

    def emitMessage(self, command, data=None):
        for ai in self.getMembers():
            datagram = Datagram()
            datagram.setCommand(command)
            datagram.setSender(self.getClient().getId())
            datagram.setRecipient(ai.getId())
            datagram.setData(data)
            self.sendDatagram(datagram)
            del datagram

        del command
        del data

    def _send(self):
        try:
            datagram = self.getDatagramFromOutbox()
            dg = self.encrypt(datagram)
            ai = self.getMemberById(datagram.getRecipient())

            if ai:
                ai.sendDatagram(dg) # send through client
            else:
                return False # unsuccessful

            del datagram
            del dg
            del ai

            return True # successful
        except queue.Empty:
            return True # successful
        except Exception as e:
            self.notify.error('ZoneError', str(e))
            return False # unsuccessful

    def sendHelo(self):
        self.notify.debug('sending helo'.format(self.getId()))
        self.emitMessage(constants.CMD_HELO,
                         [self.getId(),
                          self.getKey(),
                          [ai.getId() for ai in self.getMembers()],
                          [ai.getName() for ai in self.getMembers()],
                          self.isGroup])

    def sendRedy(self):
        self.notify.debug('sending redy'.format(self.getId()))
        self.emitMessage(constants.CMD_REDY, self.__id2key)

    def clientRedy(self, datagram):
        id_, key = datagram.getSender(), datagram.getData()

        if id_ in self.__id2key:
            self.__id2key[id_] = key
            self.notify.debug('client {0} is redy'.format(id_, self.getId()))
        else:
            self.notify.error('ZoneError', '{0} not in zone'.format(id_))

        if all(self.__id2key.values()):
            self.setSecure(True)
            self.sendRedy()

        del id_
        del key
        del datagram
