from PyQt5.QtWidgets import QMainWindow


class ChatWindow(QMainWindow):

    def __init__(self, client):
        QMainWindow.__init__(self)
        self.client = client
