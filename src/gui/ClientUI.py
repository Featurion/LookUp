from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QWidget
from src.gui.ChatWindow import ChatWindow
from src.gui.LoginWindow import LoginWindow


class ClientUI(QApplication):

    def __init__(self, client):
        QApplication.__init__(self, [])
        self.client = client
        self.running = False
        self.theme = self.palette().color(QPalette.Window)
        self.chat_window = None
        self.waiting_dialog = None
        self.aboutToQuit.connect(self.__stop)

    def start(self):
        while True:
            lw = self.__login()
            if not lw.restart:
                del self._lw_widget
                break
        self.client.register(lw.name)
        self.chat_window = ChatWindow(self)
        self.chat_window.show()
        if not self.running:
            self.running = True
            self.exec_()

    def __login(self):
        if not hasattr(self, '_lw_widget'):
            self._lw_widget = QWidget()
        lw = LoginWindow(self._lw_widget, self.client.name)
        lw.exec_()
        return lw

    def __stop(self):
        if self.client:
            self.client.stop()

    def stop(self):
        if self.chat_window:
            self.chat_window.close()
            self.chat_window = None
