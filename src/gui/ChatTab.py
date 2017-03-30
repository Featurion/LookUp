from threading import Thread
from PyQt5.QtWidgets import QWidget, QStackedWidget, QHBoxLayout, QMessageBox
from src.base import utils
from src.base.globals import INVALID_EMPTY_NAME, INVALID_NAME_CONTENT
from src.base.globals import INVALID_NAME_LENGTH, VALID_NAME, MAX_NAME_LENGTH
from src.base.globals import TITLE_INVALID_NAME, TITLE_EMPTY_NAME, EMPTY_NAME
from src.base.globals import TITLE_SELF_CONNECT, SELF_CONNECT, NAME_CONTENT
from src.base.globals import NAME_CONTENT
from src.gui.InputWidget import InputWidget
from src.gui.ConnectingWidget import ConnectingWidget
from src.gui.ChatWidget import ChatWidget


class ChatTab(QWidget):

    def __init__(self, window):
        QWidget.__init__(self)
        self.window = window
        self.client = window.client
        self.unread = 0
        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(InputWidget(self,
                                                'images/new_chat.png', 150,
                                                'Username:', self.connect))
        self.widget_stack.addWidget(ConnectingWidget(self))
        self.widget_stack.addWidget(ChatWidget(self))
        self.widget_stack.setCurrentIndex(0)
        self.build()

    def build(self):
        _layout = QHBoxLayout()
        _layout.addWidget(self.widget_stack)
        self.setLayout(_layout)

    def connect(self, name):
        status = utils.isNameInvalid(name)
        if name == self.client.name:
            msg = (TITLE_SELF_CONNECT, SELF_CONNECT)
        elif status == VALID_NAME:
            self.widget_stack.widget(1).setConnectingToName(name)
            self.widget_stack.setCurrentIndex(1)
            connect_thread = Thread(target=self.client.openSession,
                                    args=([name],), # temporary
                                    daemon=True)
            connect_thread.start()
            return
        elif status == INVALID_NAME_CONTENT:
            msg = (TITLE_INVALID_NAME, NAME_CONTENT)
        elif status == INVALID_NAME_LENGTH:
            msg = (TITLE_INVALID_NAME, NAME_LENGTH)
        elif status == INVALID_EMPTY_NAME:
            msg = (TITLE_EMPTY_NAME, EMPTY_NAME)
        else:
            pass
        QMessageBox.warning(self, *msg)

    def restart(self):
        pass
