import base64
import queue

from src.base import constants
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase


class ZoneAI(ZoneBase):

    def __init__(self, client, zone_id, members, is_group):
        ZoneBase.__init__(self, client, zone_id, members, is_group)
        self.__id2member = {ai.getId(): tuple() for ai in members}

        self.COMMAND_MAP.update({
            constants.CMD_REDY: self.clientRedy,
            constants.CMD_ZONE_ADD: self.addUser,
            constants.CMD_TYPING: self.clientTyping,
            constants.CMD_MSG: self.clientMsg,
        })

    def cleanup(self):
        ZoneBase.cleanup(self)
        if self.__id2member:
            self.__id2member.clear()
            del self.__id2member
            self.__id2member = None

    def getMemberIds(self):
        return [ai.getId() for ai in self.getMembers()]

    def getMemberNames(self):
        return [ai.getName() for ai in self.getMembers()]

    def getMemberById(self, id_):
        for ai in self.getMembers():
            if ai.getId() == id_:
                return ai
        return None

    def getZoneData(self):
        return [self.getId(),
                self.getKey(),
                self.getMemberIds(),
                self.getMemberNames(),
                self.isGroup]

    def getWorkingKey(self, id_):
        member = self.__id2member.get(id_)
        if member:
            return member[0]
        else:
            return None

    def emitMessage(self, command, data=None, sender=None):
        for ai in self.getMembers():
            if sender:
                if ai.getId() == sender:
                    return
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

    def __sendHelo(self, id_):
        datagram = Datagram()
        datagram.setCommand(constants.CMD_HELO)
        datagram.setSender(self.getClient().getId())
        datagram.setRecipient(id_)
        datagram.setData(self.getZoneData())
        self.sendDatagram(datagram)

        del id_
        del datagram

    def emitHelo(self):
        self.notify.debug('sending helo'.format(self.getId()))
        self.emitMessage(constants.CMD_HELO, self.getZoneData())

    def emitRedy(self):
        self.notify.debug('sending redy'.format(self.getId()))
        self.emitMessage(constants.CMD_REDY, self.__id2member)

    def clientRedy(self, datagram):
        id_, key = datagram.getSender(), datagram.getData()
        name = self.getClient().server.cm.getClientById(id_).getName()

        if id_ in self.__id2member:
            self.__id2member[id_] = (key, name)
            self.notify.debug('client {0}-{1} is redy'.format(name, id_))
        else:
            self.notify.error('ZoneError', '{0} not in zone'.format(id_))

        if all(self.__id2member.values()):
            self.setSecure(True)
            self.emitRedy()

        del id_
        del key
        del name
        del datagram

    def clientTyping(self, datagram):
        status = datagram.getData()

        self.emitMessage(constants.CMD_TYPING, status, datagram.getSender())

    def clientMsg(self, datagram):
        text = datagram.getData()

        self.emitMessage(constants.CMD_MSG, text)

    def addUser(self, datagram):
        name = datagram.getData()
        ai = self.getClient().server.cm.getClientByName(name)

        if ai is None:
            self.getClient().sendError(constants.TITLE_NAME_DOESNT_EXIST,
                                       constants.NAME_DOESNT_EXIST)
            return
        else:
            self.notify.debug('adding user {0}'.format(name))
            self.addMember(ai)
            self.__id2member[ai.getId()] = tuple()
            self.__sendHelo(ai.getId())

        del name
        del ai
        del datagram
