from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QPushButton

from src.base import utils


class ConnectionDialog(QMessageBox):

    def __init__(self, parent, member_names):
        QMessageBox.__init__(self, parent)
        self.accepted = False
        self.setWindowTitle('Incoming Connection')
        if len(member_names) > 1: # client name not included
            self.setText('Received group request from '
                         + utils.oxfordComma(member_names))
        else:
            self.setText('Received connection request from ' + member_names[0])
        self.setIcon(QMessageBox.Question)
        self.acceptButton = QPushButton(QIcon.fromTheme('dialog-ok'),
                                        'Accept')
        self.rejectButton = QPushButton(QIcon.fromTheme('dialog-cancel'),
                                        'Reject')
        self.addButton(self.acceptButton, QMessageBox.YesRole)
        self.addButton(self.rejectButton, QMessageBox.NoRole)
        self.buttonClicked.connect(self.answered)

    def answered(self, button):
        if button is self.acceptButton:
            self.accepted = True
        else:
            self.accepted = False
        self.close()

    @staticmethod
    def getAnswer(parent, member_names):
        acceptDialog = ConnectionDialog(parent, member_names)
        acceptDialog.exec_()
        return acceptDialog.accepted
