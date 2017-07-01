import sys
import threading

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox

from src.base.Notifier import Notifier
from src.gui.ChatWindow import ChatWindow
from src.gui.LoginWindow import LoginWindow
from src.users.Client import Client


class ClientUI(QApplication, Notifier):

    error_signal = pyqtSignal(str, str)
    stall_signal = pyqtSignal()
    connected_signal = pyqtSignal()
    login_signal = pyqtSignal(str)

    def __init__(self, address: str, port: int):
        QApplication.__init__(self, [])
        Notifier.__init__(self)

        self.__client = Client(self, address, port)
        self.__window = None
        self.running = False

        self.error_signal.connect(self.__showError)
        self.stall_signal.connect(self.__showConnecting)
        self.connected_signal.connect(self.__connectingDone)
        self.login_signal.connect(self.__loginDone)

        self.aboutToQuit.connect(self.stop)

    @pyqtSlot()
    def start(self):
        self.__window = LoginWindow(self)
        self.__window.start()
        self.exec_()

    def stop(self):
        if self.getClient():
            self.getClient().stop()
            del self.__client
            self.__client = None
        if self.getWindow():
            self.getWindow().stop()
            del self.__window
            self.__window = None
        sys.exit(0)

    def getClient(self):
        return self.__client

    def getWindow(self):
        return self.__window

    def __showError(self, title, err):
        QMessageBox.warning(QWidget(), title, err)

    @pyqtSlot()
    def __showConnecting(self):
        self.getWindow().widget_stack.setCurrentIndex(0)

    @pyqtSlot()
    def __connectingDone(self):
        self.getWindow().widget_stack.setCurrentIndex(1)

    @pyqtSlot(str)
    def __loginDone(self, resp):
        if resp:
            self.notify.info('failed to login; trying again')
            self.__showError('Login error', resp)
            self.__window.widget_stack.setCurrentIndex(1)
        else:
            self.notify.info('successfully logged in')
            self.__nowChatting()

    def __nowChatting(self):
        self.__window.stop()
        del self.__window

        self.running = True
        self.__window = ChatWindow(self)
        self.__window.start()
