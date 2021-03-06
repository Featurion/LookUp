from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QStackedWidget

from src import constants, settings
from src.gui import utils
from src.gui.widgets.ConnectingWidget import ConnectingWidget
from src.gui.widgets.InputWidget import InputWidget


class LoginWindow(QDialog):

    def __init__(self, interface):
        super().__init__()

        self.interface = interface

        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(ConnectingWidget(self))

        self.input = InputWidget(
            self,
            'images/splash_icon.png', 200,
            'Username:', 'Login',
            constants.MAX_NAME_LENGTH,
            self.__connect)
        self.widget_stack.addWidget(self.input)

        hbox = QHBoxLayout()
        hbox.addWidget(self.widget_stack)
        self.setLayout(hbox)

        self.setWindowTitle(settings.APP_NAME)
        self.setWindowIcon(QIcon('images/icon.png'))

        utils.resize_window(self, 500, 200)
        utils.center_window(self)

    def __connect(self, username):
        self.widget_stack.setCurrentIndex(0)
        conn.synchronous_send(
            command = constants.CMD_AUTH,
            data = username)
