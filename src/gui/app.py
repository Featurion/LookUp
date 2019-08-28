import asyncio
import builtins
import jugg
import sys
import threading

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox

from src import client, constants
from src.gui import utils
from src.gui.windows.ChatWindow import ChatWindow
from src.gui.windows.ConnectionDialog import ConnectionDialog
from src.gui.windows.LoginWindow import LoginWindow


class Interface(QApplication):

    error_signal = pyqtSignal(int)
    connected_signal = pyqtSignal()
    login_signal = pyqtSignal()
    hello_signal = pyqtSignal(str, bool, dict)

    def __new__(cls, *args, **kwargs):
        builtins.interface = super().__new__(cls, *args, **kwargs)
        return builtins.interface

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
        self._window = LoginWindow(self)
        self._window.show()

        threading.Thread(
            target = self.open_connection,
            daemon = True).start()

        self.exec_()

    def open_connection(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            builtins.conn = client.Client(*self._args[0], **self._args[1])
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
        self._window = ChatWindow(self)
        self._window.show()

    @pyqtSlot(str, bool, dict)
    def __hello(self, id_, is_group, participants):
        if not is_group:
            if conn.name not in participants:
                if not ConnectionDialog.getAnswer(
                    self._window,
                    utils.oxford_comma(participants.values())):
                    return

        tab = self._window.open_tab()
        zone = conn.new_zone(tab, id_)
        zone.participants = dict(participants)

        tab.update_title()
        tab.widget_stack.setCurrentIndex(1)

        conn.synchronous_send(
            command = constants.CMD_READY,
            recipient = id_)
