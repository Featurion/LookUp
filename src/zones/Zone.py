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
            constants.CMD_SMP_0: self.doSMP, # Anyway to make these 'not ugly'?
            constants.CMD_SMP_1: self.doSMP,
            constants.CMD_SMP_2: self.doSMP,
            constants.CMD_SMP_3: self.doSMP,
            constants.CMD_SMP_4: self.doSMP,
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
        self.sendDatagram(datagram)

        self.pending_messages.append(datagram.getId())

        del command
        del data
        del datagram

    def sendChatMessage(self, text: str, id_: str):
        self.sendMessage(constants.CMD_MSG, (text, id_))

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
        text, id_ = datagram.getData()
        name = self.getClientNameById(datagram.getSender())

        if datagram.getId() in self.pending_messages:
            self.tab.new_message_signal.emit(constants.CMD_MSG, (utils.getTimestamp(), text, id_), constants.RECEIVER, name, True)
        else:
            self.tab.new_message_signal.emit(constants.CMD_MSG, (utils.getTimestamp(), text, id_), constants.RECEIVER, name, False)

        del text
        del name
        del datagram

    def doSMP(self, datagram):
        command = datagram.getCommand()
        data = datagram.getData().encode('latin-1')
        name = self.getClientNameById(datagram.getSender())

        if command == constants.CMD_SMP_0:
            # SMP callback with the given question
            self.tab.interface.getWindow().smp_request_signal.emit(constants.SMP_CALLBACK_REQUEST, name, self.getId(), data.decode('latin-1'), 0)
        elif command == constants.CMD_SMP_1:
            # If there's already an SMP object, go ahead to step 1.
            # Otherwise, save the data until we have an answer from the user to respond with
            if self.smp:
                self.__doSMPStep1(data)
            else:
                self.smp_step_1 = data
        elif command == constants.CMD_SMP_2:
            self.__doSMPStep2(data)
        elif command == constants.CMD_SMP_3:
            self.__doSMPStep3(data)
        elif command == constants.CMD_SMP_4:
            self.__doSMPStep4(data, name)
        else:
            self.notify.warning('suspicious invalid SMP command')

    def __doSMPStep1(self, data):
        buffer_ = self.smp.step2(data)
        self.sendMessage(constants.CMD_SMP_2, buffer_)

    def __doSMPStep2(self, data):
        buffer_ = self.smp.step3(data)
        self.sendMessage(constants.CMD_SMP_3, buffer_)

    def __doSMPStep3(self, data):
        buffer_ = self.smp.step4(data)
        self.sendMessage(constants.CMD_SMP_4, buffer_)

    def __doSMPStep4(self, data, name):
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
        self.__doSMPStep1(self.smp_step_1)