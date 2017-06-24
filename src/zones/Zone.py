import base64
import queue

from src.base import constants
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase


class Zone(ZoneBase):

    def __init__(self, tab, zone_id, key, member_ids, is_group):
        ZoneBase.__init__(self, tab.getClient(), zone_id, member_ids, is_group)
        self.tab = tab
        self.id2key = {id_: None for id_ in member_ids}
        self.__alt_key = key

        self.COMMAND_MAP.update({
            constants.CMD_REDY: self.doRedy,
        })

    def cleanup(self):
        ZoneBase.cleanup(self)
        self.__alt_key = None
        if self.tab:
            self.tab.cleanup()
            del self.tab
            self.tab = None
        if self.id2key:
            self.id2key.clear()
            del self.id2key
            self.id2key = None

    def getWorkingKey(self, id_):
        del id_
        return self.__alt_key

    def sendMessage(self, command, data=None):
        datagram = Datagram()
        datagram.setCommand(command)
        datagram.setSender(self.getClient().getId())
        datagram.setRecipient(self.getId())
        datagram.setData(data)
        self.sendDatagram(datagram)

        del command
        del data
        del datagram

    def sendTypingMessage(self, status):
        # TODO Messaging
        pass

    def sendChatMessage(self, message):
        # TODO Messaging
        pass

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

        member_names, key_map = datagram.getData()
        self.id2key = key_map
        self.tab.zone_redy_signal.emit(member_names)
        del datagram

    def addUser(self, name):
        self.sendMessage(constants.CMD_ZONE_ADD, name)
