import asyncio
import jugg
import sys
import threading

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox

from src import client, constants
from src.gui import utils, windows


class LookUpInterface(QApplication):

    error_signal = pyqtSignal(int)
    connected_signal = pyqtSignal()
    login_signal = pyqtSignal()
    hello_signal = pyqtSignal(str, list)

    def __init__(self, host: str, port: int):
        QApplication.__init__(self, [])

        self._address = (host, port)
        self._client = None
        self._window = None

        self.error_signal.connect(self.__error)
        self.connected_signal.connect(self.__connected)
        self.login_signal.connect(self.__logged_in)
        self.hello_signal.connect(self.__hello)

        self.aboutToQuit.connect(self.stop)

    def start(self):
        self._window = windows.LoginWindow(self)
        self._window.show()

        connection = threading.Thread(
            target = self.open_connection,
            daemon = True)
        connection.start()

        self.exec_()

    def open_connection(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            self._client = client.LookUpClient(self, *self._address)
        except ConnectionRefusedError:
            self.error_signal.emit(constants.ERR_NO_CONNECTION)
            return

        jugg.utils.reactive_event_loop(
            loop,
            self._client.start(), self._client.stop())

    def stop(self):
        self._window.close()

    @pyqtSlot(int)
    def __error(self, errno):
        info = constants.ERROR_INFO_MAP.get(errno, '').title()
        QMessageBox.warning(QWidget(), info, info)
        self.stop()

    @pyqtSlot()
    def __connected(self):
        self._window.widget_stack.setCurrentIndex(1)

    @pyqtSlot()
    def __logged_in(self):
        self._window.close()
        self._window = windows.ChatWindow(self)
        self._window.show()

    @pyqtSlot(str, list)
    def __hello(self, id_, member_names):
        action = windows.ConnectionDialog.getAnswer(
            self._window, utils.oxford_comma(member_names))

        if action:
            self._client.synchronous_send(
                command = constants.CMD_READY,
                recipient = id_)

            self._window.open_tab(member_names)
            self._window.widget_stack.setCurrentIndex(1)
        else:
            self._client.synchronous_send(
                command = constants.CMD_REJECT,
                recipient = id_)
