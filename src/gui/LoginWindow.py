from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QStackedWidget, QHBoxLayout

from src.base import constants, settings
from src.gui import utils

from src.gui.misc.Connecting import Connecting
from src.gui.misc.Input import Input

class LoginWindow(QDialog):

    def __init__(self, interface):
        super().__init__()

        self.interface = interface

        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(Connecting(self))

        self.input = Input(
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

        utils.resizeWindow(self, 500, 200)
        utils.centerWindow(self)

    def __connect(self, username):
        self.widget_stack.setCurrentIndex(0)
        self.interface._client.synchronousSend(
            command = constants.CMD_LOGIN,
            data = username)
