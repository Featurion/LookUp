import asyncio
import builtins
import jugg
import sys
import threading

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox

from src import client, constants
from src.gui import utils, windows


class Interface(QApplication):

    error_signal = pyqtSignal(int)
    connected_signal = pyqtSignal()
    login_signal = pyqtSignal()
    hello_signal = pyqtSignal(str, dict)

    def __init__(self, *args, **kwargs):
        QApplication.__init__(self, [])

        self._args = (args, kwargs)
        self._window = None

        self.error_signal.connect(self.__error)
        self.connected_signal.connect(self.__connected)
        self.login_signal.connect(self.__logged_in)
        self.hello_signal.connect(self.__hello)

        self.aboutToQuit.connect(self.stop)

    def start(self):
        self._window = windows.LoginWindow(self)
        self._window.show()

        threading.Thread(
            target = self.open_connection,
            daemon = True).start()

        self.exec_()

    def open_connection(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Much easier than finding the window -> interface -> client, etc.
            builtins.conn = client.Client(
                self,
                *self._args[0],
                **self._args[1])
        except ConnectionRefusedError:
            self.error_signal.emit(constants.ERR_NO_CONNECTION)
            return

        jugg.utils.reactive_event_loop(
            loop,
            conn.start(), conn.stop())

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

    @pyqtSlot(str, dict)
    def __hello(self, id_, participants):
        action = windows.ConnectionDialog.getAnswer(
            self._window, utils.oxford_comma(list(participants.keys())))

        if action:
            participants[conn.name] = conn.id

            self._window.new_zone(id_, participants)
            self._window.widget_stack.setCurrentIndex(1)

            conn.synchronous_send(
                command = constants.CMD_READY,
                recipient = id_)
        else:
            pass
