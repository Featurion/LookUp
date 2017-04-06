from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from src.base.globals import TITLE_NAME_IN_USE, NAME_IN_USE
from src.gui.ChatWindow import ChatWindow
from src.gui.LoginWindow import LoginWindow


class ClientUI(QApplication):

    def __init__(self, client):
        QApplication.__init__(self, [])
        self.client = client
        self.running = False
        self.theme = self.palette().color(QPalette.Window)
        self.window = None
        self.waiting_dialog = None
        self.aboutToQuit.connect(self.__stop)

    def start(self):
        while True:
            lw = self.__login()
            if not lw.restart:
                del self._lw_widget
                break
        if lw.getName() and not self.running:
            try:
                self.client.register(lw.getName())
            except LookupError:
                QMessageBox.warning(QWidget(),
                                    TITLE_NAME_IN_USE,
                                    NAME_IN_USE)
                return
            self.window = ChatWindow(self.client)
            self.window.show()
            self.running = True
            self.exec_()

    def __login(self):
        if not hasattr(self, '_lw_widget'):
            self._lw_widget = QWidget()
        lw = LoginWindow(self._lw_widget, self.client.getName())
        lw.exec_()
        return lw

    def __stop(self):
        if self.client:
            self.client.stop()

    def stop(self):
        if self.window:
            self.window.close()
            self.window = None
