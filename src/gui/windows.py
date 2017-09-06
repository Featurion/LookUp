from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QDialog, QHBoxLayout, QMessageBox
from PyQt5.QtWidgets import QStackedWidget

from src import constants, settings
from src.gui import widgets, utils


class LoginWindow(QDialog):

    def __init__(self, interface):
        QDialog.__init__(self)

        self._interface = interface

        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(widgets.Connecting(self))

        self.input = widgets.Input(
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
        self._interface._client._username = username
