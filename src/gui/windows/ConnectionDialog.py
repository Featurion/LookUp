from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QPushButton


class ConnectionDialog(QMessageBox):

    def __init__(self, parent, msg):
        QMessageBox.__init__(self, parent)
        self.accepted = False

        self.setWindowTitle('Incoming Connection')
        self.setText('Received connection request from ' + msg)
        self.setIcon(QMessageBox.Question)

        self.accept_button = QPushButton(
            QIcon.fromTheme('dialog-ok'), 'Accept')
        self.addButton(self.accept_button, QMessageBox.YesRole)

        self.reject_button = QPushButton(
            QIcon.fromTheme('dialog-cancel'), 'Reject')
        self.addButton(self.reject_button, QMessageBox.NoRole)

        self.buttonClicked.connect(self.answered)

    def answered(self, button):
        if button is self.accept_button:
            self.accepted = True
        else:
            self.accepted = False

        self.close()

    @staticmethod
    def getAnswer(parent, msg):
        accept_dialog = ConnectionDialog(parent, msg)
        accept_dialog.exec_()
        return accept_dialog.accepted
