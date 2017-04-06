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
                                                'Username:', 'LookUp',
                                                self.connect))
        self.widget_stack.addWidget(ConnectingWidget(self))
        self.widget_stack.addWidget(ChatWidget(self))
        self.widget_stack.setCurrentIndex(0)
        self.build()

    def build(self):
        _layout = QHBoxLayout()
        _layout.addWidget(self.widget_stack)
        self.setLayout(_layout)

    def connect(self, input_):
        names = set(n.strip() for n in input_.split(','))
        for name in names:
            status = utils.isNameInvalid(name)
            msg = None
            if name == self.client.getName():
                msg = (TITLE_SELF_CONNECT, SELF_CONNECT)
            elif status == INVALID_NAME_CONTENT:
                msg = (TITLE_INVALID_NAME, NAME_CONTENT)
            elif status == INVALID_NAME_LENGTH:
                msg = (TITLE_INVALID_NAME, NAME_LENGTH)
            elif status == INVALID_EMPTY_NAME:
                msg = (TITLE_EMPTY_NAME, EMPTY_NAME)
            else:
                pass
            if msg:
                QMessageBox.warning(self, *msg)
                names.remove(name)
        self.widget_stack.widget(1).setConnectingToName(name)
        self.widget_stack.setCurrentIndex(1)
        connect_thread = Thread(target=self.client.openSession,
                                args=(names,), # temporary
                                daemon=True)
        connect_thread.start()

    def restart(self):
        pass
