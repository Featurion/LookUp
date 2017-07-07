from threading import Thread

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QStackedWidget, QHBoxLayout, QMessageBox

from src.base import constants, utils
from src.gui.MultipleInputWidget import MultipleInputWidget
from src.gui.InputWidget import InputWidget
from src.gui.ConnectingWidget import ConnectingWidget
from src.gui.ChatWidget import ChatWidget


class ChatTab(QWidget):

    new_message_signal = pyqtSignal(int, tuple, int, str, bool)
    zone_redy_signal = pyqtSignal(list)

    def __init__(self, interface, is_group: bool):
        QWidget.__init__(self)

        self.interface = interface
        self.is_group = is_group
        self.__zone = None
        self.__unread = 0

        self.setupWidgets()

        self.new_message_signal.connect(self.newMessage)
        self.zone_redy_signal.connect(self.zoneRedy)

        _layout = QHBoxLayout()
        _layout.addWidget(self.widget_stack)
        self.setLayout(_layout)

        del _layout

    def cleanup(self):
        self.new_message_signal = None
        self.zone_redy_signal = None
        self.is_group = None
        self.__unread = None
        if self.__zone: # cleaned up in ZoneManager
            del self.__zone
            self.__zone = None
        if self.widget_stack:
            del self.widget_stack
            self.widget_stack = None
        if self.input_widget:
            self.input_widget.cleanup()
            del self.input_widget
            self.input_widget = None
        if self.chat_widget:
            self.chat_widget.cleanup()
            del self.chat_widget
            self.chat_widget = None

    def exit(self):
        return NotImplemented

    def getClient(self):
        return self.interface.getClient()

    def getZone(self):
        return self.__zone

    def setZone(self, zone):
        if self.getZone() is None:
            self.__zone = zone

        del zone

    def setupWidgets(self):
        self.input_widget = InputWidget(self,
                                        'images/new_chat.png', 150,
                                        'Username:', 'LookUp',
                                        constants.MAX_NAME_LENGTH,
                                        self.connect)
        self.multi_input = MultipleInputWidget(self,
                                               'images/new_chat.png', 150,
                                               'Usernames:', 'LookUp',
                                               constants.MAX_NAME_LENGTH,
                                               self.connect,
                                               self.addInput)
        self.chat_widget = ChatWidget(self)

        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(self.multi_input)
        self.widget_stack.addWidget(self.input_widget)
        self.widget_stack.addWidget(ConnectingWidget(self))
        self.widget_stack.addWidget(self.chat_widget)
        self.widget_stack.addWidget(self.chat_widget.input_widget)

        if self.is_group and constants.WANT_BLANK_GROUPS:
            self.widget_stack.setCurrentIndex(2) # connecting
        elif self.is_group:
            self.widget_stack.setCurrentIndex(0) # multi input
        else:
            self.widget_stack.setCurrentIndex(1) # single input

    def addInput(self):
        _iw = MultipleInputWidget(*self.multi_input._data,
                                  defaults=self.multi_input.getInputsText(),
                                  num_inputs=len(self.multi_input.inputs)+1)
        self.widget_stack.removeWidget(self.multi_input)
        self.multi_input = _iw
        self.widget_stack.insertWidget(0, self.multi_input)
        self.widget_stack.setCurrentIndex(0)

        del _iw

    def connect(self, *names):
        for name in set(names):
            status = utils.isNameInvalid(name)
            msg = None

            if name == self.interface.getClient().getName():
                msg = (constants.TITLE_SELF_CONNECT,
                       constants.SELF_CONNECT)
            elif status == constants.INVALID_NAME_CONTENT:
                msg = (constants.TITLE_INVALID_NAME,
                       constants.NAME_CONTENT)
            elif status == constants.INVALID_NAME_LENGTH:
                msg = (constants.TITLE_INVALID_NAME,
                       constants.NAME_LENGTH)
            elif status == constants.INVALID_EMPTY_NAME:
                msg = (constants.TITLE_EMPTY_NAME,
                       constants.EMPTY_NAME)
            else:
                pass

            if msg:
                QMessageBox.warning(self, *msg)
                return

        window = self.interface.getWindow()
        if names and not self.is_group:
            tab_name = utils.oxfordComma(names)
            window.doConnecting(self, tab_name)
        elif self.is_group:
            tab_name = constants.BLANK_GROUP_TAB_TITLE
            window.doConnecting(self, None)
        else:
            return # should not happen
        window.setTabTitle(self, tab_name)

        self.interface.getClient().initiateHelo(self, names, self.is_group)

        del names
        del tab_name

    @pyqtSlot(int, tuple, int, str, bool)
    def newMessage(self, command, data, src, name, loop):
        if command == constants.CMD_TYPING:
            status = int(*data[0])
            if status == constants.TYPING_START:
                self.interface.getWindow().status_bar.showMessage("%s is typing..." % name)
            elif status == constants.TYPING_STOP:
                self.interface.getWindow().status_bar.showMessage('')
            elif status == constants.TYPING_STOP_WITH_TEXT:
                self.interface.getWindow().status_bar.showMessage("%s has entered text" % name)
            elif status == constants.TYPING_DELETE_TEXT:
                self.interface.getWindow().status_bar.showMessage("%s is deleting text..." % name)
        elif command == constants.CMD_MSG:
            timestamp, text, id_ = data
            if not loop:
                self.chat_widget.appendMessage(text, timestamp, src, name, id_)
            else:
                self.chat_widget.confirmMessage(text, name, id_)
        else:
            self.notify.warning('received invalid command: {0}'.format(command))
            self.interface.error_signal.emit(constants.TITLE_INVALID_COMMAND, constants.INVALID_COMMAND)

        del command
        del data
        del src

    @pyqtSlot(list)
    def zoneRedy(self, member_names):
        member_names.remove(self.getClient().getName())
        if member_names:
            tab_name = utils.oxfordComma(member_names)
        elif self.is_group:
            tab_name = constants.BLANK_GROUP_TAB_TITLE
        else:
            return # should not happen

        self.interface.getWindow().setTabTitle(self, tab_name)
        self.widget_stack.setCurrentIndex(3)
