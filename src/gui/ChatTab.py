from threading import Thread

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QStackedWidget, QHBoxLayout, QMessageBox

from src.base import constants, utils
from src.gui.MultipleInputWidget import MultipleInputWidget
from src.gui.InputWidget import InputWidget
from src.gui.ConnectingWidget import ConnectingWidget
from src.gui.ChatWidget import ChatWidget


class ChatTab(QWidget):

    new_message_signal = pyqtSignal(str, float)
    zone_redy_signal = pyqtSignal()

    def __init__(self, interface, is_group: bool):
        QWidget.__init__(self)

        self.interface = interface
        self.is_group = is_group
        self.__zone = None
        self.__unread = 0

<<<<<<< HEAD
        self.setupWidgets()
=======
        self.input_widget = InputWidget(self,
                                        'images/new_chat.png', 150,
                                        'Username:',
                                        'LookUp',
                                        constants.MAX_NAME_LENGTH,
                                        self.connect)
        self.chat_widget = ChatWidget(self, self.is_group)

        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(self.input_widget)
        self.widget_stack.addWidget(ConnectingWidget(self))
        self.widget_stack.addWidget(self.chat_widget)
        self.widget_stack.addWidget(self.chat_widget.input_widget)

        if self.is_group:
            self.widget_stack.setCurrentIndex(1)
            self.connect()
        else:
            self.widget_stack.setCurrentIndex(0)
>>>>>>> 7382d566651d3388d44e39d2e1b81256307813ec

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
        else:
            self.notify.error('GUIError', 'attempted to change zone')

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

        if self.is_group and constants.WANT_BLANK_GROUPS:
            self.widget_stack.setCurrentIndex(2) # connecting
            self.connect()
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

        titled_names = utils.oxfordComma(names)
        window = self.interface.getWindow()
        window.doConnecting(self, titled_names)
        window.setTabTitle(self, titled_names)


        _t = Thread(target=self.interface.getClient().initiateHelo,
                    args=(self, names, self.is_group),
                    daemon=True).start()

        del names
        del titled_names
        del _t

    @pyqtSlot(str, float)
    def newMessage(self, msg, ts):
        self.chat_widget.log.addMessage(msg, ts)

        scrollbar = self.chat_widget.chat_log.verticalScrollBar()
        if scrollbar.value() == scrollbar.maximum():
            scrollbar.setValue(scrollbar.maximum())

        del msg
        del ts
        del scrollbar

    @pyqtSlot()
    def zoneRedy(self):
        self.widget_stack.setCurrentIndex(3)
