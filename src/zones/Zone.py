import base64
import queue

from src.base import constants, utils
from src.base.Datagram import Datagram
from src.zones.ZoneBase import ZoneBase
from src.base.SMP import SMP

class Zone(ZoneBase):

    def __init__(self, tab, zone_id, key, member_ids, is_group):
        ZoneBase.__init__(self, tab.getClient(), zone_id, member_ids, is_group)
        self.tab = tab
        self.id2member = {id_: tuple() for id_ in member_ids}
        self.__alt_key = key
        self.pending_messages = []
        self.smp = None
        self.smp_step_1 = None

        self.COMMAND_MAP.update({
            constants.CMD_REDY: self.doRedy,
            constants.CMD_TYPING: self.doTyping,
            constants.CMD_MSG: self.doMsg,
            constants.CMD_SMP_0: self.doSMP0,
            constants.CMD_SMP_1: self.doSMP1,
            constants.CMD_SMP_2: self.doSMP2,
            constants.CMD_SMP_3: self.doSMP3,
            constants.CMD_SMP_4: self.doSMP4,
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

    def __checkSMP(self):
        if not self.smp.match:
            self.notify.error('SMPError', 'SMP match failed')
        else:
            return True

    def sendMessage(self, command, data=None):
        datagram = Datagram()
        datagram.setCommand(command)
        datagram.setSender(self.getClient().getId())
        datagram.setRecipient(self.getId())
        datagram.setData(data)
        if self.isSecure:
            hmac = self.generateHMAC(data)
            datagram.setHMAC(base64.b85encode(hmac)) # Generate and set the HMAC for the message

        self.sendDatagram(datagram)

        self.pending_messages.append(datagram.getId())

        del command
        del data
        del datagram

    def sendChatMessage(self, text: str, id_: str):
        self.sendMessage(constants.CMD_MSG, [text, id_, utils.getTimestamp()])

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
        text, id_, timestamp = datagram.getData()
        name = self.getClientNameById(datagram.getSender())

        if datagram.getId() in self.pending_messages:
            self.tab.new_message_signal.emit(constants.CMD_MSG, (timestamp, text, id_), constants.RECEIVER, name, True)
        else:
            self.tab.new_message_signal.emit(constants.CMD_MSG, (timestamp, text, id_), constants.RECEIVER, name, False)

        del text
        del name
        del datagram

    def doSMP0(self, datagram):
        data = datagram.getData()
        name = self.getClientNameById(datagram.getSender())

        # SMP callback with the given question
        self.tab.interface.getWindow().smp_request_signal.emit(constants.SMP_CALLBACK_REQUEST, name, self.getId(), data, 0)

    def doSMP1(self, datagram):
        if isinstance(datagram, bytes):
            data = datagram
        else:
            data = datagram.getData().encode('latin-1')

        # If there's already an SMP object, go ahead to step 1.
        # Otherwise, save the data until we have an answer from the user to respond with
        if self.smp:
            buffer_ = self.smp.step2(data)
            self.sendMessage(constants.CMD_SMP_2, buffer_)
        else:
            self.smp_step_1 = data

    def doSMP2(self, datagram):
        data = datagram.getData().encode('latin-1')

        buffer_ = self.smp.step3(data)
        self.sendMessage(constants.CMD_SMP_3, buffer_)

    def doSMP3(self, datagram):
        data = datagram.getData().encode('latin-1')

        buffer_ = self.smp.step4(data)
        self.sendMessage(constants.CMD_SMP_4, buffer_)

    def doSMP4(self, datagram):
        data = datagram.getData().encode('latin-1')
        name = self.getClientNameById(datagram.getSender())

        self.smp.step5(data)
        if self.__checkSMP():
            self.tab.interface.getWindow().smp_request_signal.emit(constants.SMP_CALLBACK_COMPLETE, name, '', '', 0)
        self.smp = None

    def initiateSMP(self, question, answer):
        self.sendMessage(constants.CMD_SMP_0, question)
        self.smp = SMP(answer)
        buffer_ = self.smp.step1()
        self.sendMessage(constants.CMD_SMP_1, buffer_)

    def respondSMP(self, answer):
        self.smp = SMP(answer)
        self.doSMP1(self.smp_step_1)

    def handleHMACFailure(self):
        self.getClient().interface.error_signal.emit(constants.TITLE_HMAC_ERROR, constants.HMAC_ERROR)