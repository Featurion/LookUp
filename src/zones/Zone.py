import base64
import queue

from src.base import constants
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase
from src.base import utils

class Zone(ZoneBase):

    def __init__(self, tab, zone_id, key, member_ids, is_group):
        ZoneBase.__init__(self, tab.getClient(), zone_id, member_ids, is_group)
        self.tab = tab
        self.id2member = {id_: tuple() for id_ in member_ids}
        self.__alt_key = key
        self.pending_messages = []

        self.COMMAND_MAP.update({
            constants.CMD_REDY: self.doRedy,
            constants.CMD_TYPING: self.doTyping,
            constants.CMD_MSG: self.doMsg,
        })

    def cleanup(self):
        ZoneBase.cleanup(self)
        self.__alt_key = None
        if self.tab:
            self.tab.cleanup()
            del self.tab
            self.tab = None
        if self.id2member:
            self.id2member.clear()
            del self.id2member
            self.id2member = None

    def getWorkingKey(self, id_):
        del id_
        return self.__alt_key

    def getClientNameById(self, id_):
        member = self.id2member.get(id_)
        if member:
            return member[1]
        else:
            return None

    def sendMessage(self, command, data=None):
        datagram = Datagram()
        datagram.setCommand(command)
        datagram.setSender(self.getClient().getId())
        datagram.setRecipient(self.getId())
        datagram.setData(data)
        self.sendDatagram(datagram)

        self.pending_messages.append(datagram.getId())

        del command
        del data
        del datagram

    def sendChatMessage(self, text: str):
        self.sendMessage(constants.CMD_MSG, text)

    def sendTypingMessage(self, status):
        self.sendMessage(constants.CMD_TYPING, str(status))

    def _send(self):
        try:
            datagram = self.getDatagramFromOutbox()
            dg = self.encrypt(datagram)
            self.getClient().sendDatagram(dg) # send through client

            if datagram.getCommand() == constants.CMD_REDY:
                self.setSecure(True)

            del datagram
            del dg

            return True # successful
        except queue.Empty:
            return True # successful
        except Exception as e:
            self.notify.error('ZoneError', str(e))
            return False # unsuccessful

    def sendRedy(self):
        self.notify.debug('sending redy'.format(self.getId()))
        self.sendMessage(constants.CMD_REDY, self.getKey())

    def doRedy(self, datagram):
        self.notify.debug('redy')

        self.id2member = datagram.getData()
        self.tab.zone_redy_signal.emit([n for k, n in self.id2member.values()])
        del datagram

    def addUser(self, name):
        self.sendMessage(constants.CMD_ZONE_ADD, name)

    def doTyping(self, datagram):
        status = datagram.getData()
        name = self.getClientNameById(datagram.getSender())

        self.tab.new_message_signal.emit(constants.CMD_TYPING, (status,), constants.RECEIVER, name, False)

        del status
        del name
        del datagram

    def doMsg(self, datagram):
        text = datagram.getData()
        name = self.getClientNameById(datagram.getSender())

        if datagram.getId() in self.pending_messages:
            self.tab.new_message_signal.emit(constants.CMD_MSG, (utils.getTimestamp(), text), constants.RECEIVER, name, True)
        else:
            self.tab.new_message_signal.emit(constants.CMD_MSG, (utils.getTimestamp(), text), constants.RECEIVER, name)

        del text
        del name
        del datagram
