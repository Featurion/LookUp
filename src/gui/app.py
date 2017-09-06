import sys
import threading

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox

from src import client
from src.gui import windows


class LookUpInterface(QApplication):

    error_signal = pyqtSignal(int)
    connected_signal = pyqtSignal()
    login_signal = pyqtSignal()

    def __init__(self, host: str, port: int):
        QApplication.__init__(self, [])

        self._address = (host, port)
        self._client = None
        self._window = None

        self.error_signal.connect(self.__error)
        self.connected_signal.connect(self.__connected)
        self.login_signal.connect(self.__logged_in)

        self.aboutToQuit.connect(self.stop)

    def start(self):
        self._client = client.LookUpClient(self, *self._address)

        connection = threading.Thread(
            target = self._client.start,
            daemon = True)
        connection.start()

        self._window = windows.LoginWindow(self)
        self._window.show()

        self.exec_()

    def stop(self):
        self._window.close()

    @pyqtSlot(int)
    def __error(self, errno):
        # QMessageBox.warning(QWidget(), title, err)
        pass

    @pyqtSlot()
    def __connected(self):
        self._window.widget_stack.setCurrentIndex(1)

    @pyqtSlot()
    def __logged_in(self):
        self._window.close()
        self._window = windows.ChatWindow(self)
        self._window.show()
