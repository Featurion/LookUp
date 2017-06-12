import threading

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QDialog, QHBoxLayout, QMessageBox
from PyQt5.QtWidgets import QStackedWidget

from src.base import utils
from src.base.globals import APP_TITLE
from src.base.globals import INVALID_EMPTY_NAME, INVALID_NAME_CONTENT
from src.base.globals import INVALID_NAME_LENGTH, VALID_NAME, MAX_NAME_LENGTH
from src.base.globals import TITLE_INVALID_NAME, TITLE_EMPTY_NAME
from src.base.globals import NAME_CONTENT, NAME_LENGTH, EMPTY_NAME
from src.gui.ConnectingWidget import ConnectingWidget
from src.gui.InputWidget import InputWidget


class LoginWindow(QDialog):

    stop_signal = pyqtSignal()

    def __init__(self, interface):
        QDialog.__init__(self)

        self.interface = interface

        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(ConnectingWidget(self))

        self.input = InputWidget(self,
                                 'images/splash_icon.png', 200,
                                 'Username:', 'Login',
                                 MAX_NAME_LENGTH,
                                 self.__connect)
        self.widget_stack.addWidget(self.input)

        hbox = QHBoxLayout()
        hbox.addWidget(self.widget_stack)
        self.setLayout(hbox)

        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(utils.getResourcePath('images/icon.png')))
        utils.resizeWindow(self, 500, 200)
        utils.centerWindow(self)

        self.stop_signal.connect(self.stop)

    def start(self):
        self.show()
        self.widget_stack.setCurrentIndex(0)
        threading.Thread(target=self.interface.getClient().start).start()

    def stop(self):
        self.close()

    def __login(self, name):
        threading.Thread(target=self.interface.getClient().connect,
                         args=(name, self.interface.login_signal.emit)).start()

    def __connect(self, name: str):
        if name is None:
            self.notify.info('client closed login window')
            self.interface.stop()

        status = self.__getNameStatus(name)

        if status is True:
            self.widget_stack.setCurrentIndex(0)
            self.__login(name)
        elif status:
            self.interface.notify.info('invalid username; trying again')
            QMessageBox.warning(self, *status)
        else:
            self.interface.notify.error('unknown error validating username')
            self.interface.stop()

    def __getNameStatus(self, name: str):
        status = utils.isNameInvalid(name)
        if status == VALID_NAME:
            return True
        elif status == INVALID_NAME_CONTENT:
            return (TITLE_INVALID_NAME, NAME_CONTENT)
        elif status == INVALID_NAME_LENGTH:
            return (TITLE_INVALID_NAME, NAME_LENGTH)
        elif status == INVALID_EMPTY_NAME:
            return (TITLE_EMPTY_NAME, EMPTY_NAME)
        else:
            return None
