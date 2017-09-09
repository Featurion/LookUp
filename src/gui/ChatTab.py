from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QStackedWidget, QHBoxLayout, QWidget

from src.base import constants
from src.gui import utils

from src.gui.ChatWidget import ChatWidget
from src.gui.misc.Input import Input
from src.node.Client import LookUpClient

class ChatTab(QWidget):

    update_title_signal = pyqtSignal(str)

    def __init__(self, parent, member_names):
        super().__init__(parent)

        self.update_title_signal.connect(self._updateTitle)

        if member_names:
            self.__member_data = {name: None for name in member_names}
        else:
            self.__member_data = {}

        self._zone = None
        self.__unread = 0

        self.input_widget = Input(
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
        cli = self.window().interface._client

        self._zone = LookUpClient.LookUpZone(self, cli)
        cli._zones.add(zone)

        cli.synchronousSend(
            command = constants.CMD_HELLO,
            recipient = zone.id,
            data = [name])
        self.widget_stack.setCurrentIndex(1)

    @pyqtSlot(str)
    def _updateTitle(self, title):
        index = self.window().chat_tabs.indexOf(self)
        self.window().chat_tabs.setTabText(index, title)
        self.widget_stack.currentWidget().title = title
