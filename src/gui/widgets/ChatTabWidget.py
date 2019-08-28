import time

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QStackedWidget, QWidget

from src import constants
from src.gui import utils
from src.gui.widgets.ChatWidget import ChatWidget
from src.gui.widgets.InputWidget import InputWidget


class ChatTabWidget(QWidget):

    update_title_signal = pyqtSignal()
    add_message_signal = pyqtSignal(float, str, str)
    del_message_signal = pyqtSignal(float, str)
    typing_message_signal = pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__(parent)

        self.update_title_signal.connect(self.update_title)
        self.add_message_signal.connect(self.add_message)
        self.del_message_signal.connect(self.del_message)
        self.typing_message_signal.connect(self.update_typing)

        self._zone = None
        self._chat_log = {}
        self.__unread = 0

        self.input_widget = InputWidget(
            self,
            'images/new_chat.png', 150,
            'Username:', 'LookUp',
            constants.MAX_NAME_LENGTH,
            self.connect)
        self.chat_widget = ChatWidget(self)

        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(self.input_widget)
        self.widget_stack.addWidget(self.chat_widget)

        _layout = QHBoxLayout()
        _layout.addWidget(self.widget_stack)
        self.setLayout(_layout)

    def connect(self, name):
        self.widget_stack.setCurrentIndex(1)

        if not name or name == conn.name:
            # Cannot invite yourself
            return

        if not self._zone:
            self._zone = conn.new_zone(self)
            self.update_title()

        conn.synchronous_send(
            command = constants.CMD_HELLO,
            recipient = self._zone.id,
            # This sends a list to keep the possibility of sending multiple
            # invitations open.
            data = [name])

    @pyqtSlot()
    def update_title(self):
        title = utils.oxford_comma(self._zone.participants.values())
        index = self.window().chat_tabs.indexOf(self)
        self.window().chat_tabs.setTabText(index, title)
        self.widget_stack.currentWidget().title = title

    @pyqtSlot(dict)
    def update_typing(self, typing):
        # Only show typing for the current tab
        if self is not self.window().chat_tabs.currentWidget():
            return

        # Remove ourself from the notification
        typing.pop(conn.id, None)

        names = []
        for id_, ts in typing.items():
            if (time.time() - ts) < constants.TYPING_TIMEOUT:
                names.append(self._zone.participants[id_])

        if names:
            text = utils.oxford_comma(names)
            text += ' '
            text += 'is' if len(names) == 1 else 'are'
            text += ' typing'
        else:
            text = ''

        self.window().status_bar.showMessage(text)

    @pyqtSlot(float, str, str)
    def add_message(self, ts, sender, msg):
        self._chat_log[ts, sender] = msg
        self.chat_widget.update_chat()

    @pyqtSlot(float, str)
    def del_message(self, ts, sender):
        if (ts, sender) in self._chat_log:
            self._chat_log[ts, sender] = constants.MSG_DELETED_TEXT
            self.chat_widget.update_chat()
