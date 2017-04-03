from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QPushButton


class ConnectionDialog(QMessageBox):

    def __init__(self, parent, name, members):
        QMessageBox.__init__(self, parent)
        self.accepted = None
        self.setWindowTitle('Incoming Connection')
        if members:
            self.setText('Received group request from '
                         + name
                         + ' and '
                         + ', '.join(members))
        else:
            self.setText('Received connection request from ' + name)
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
    def getAnswer(parent, name, members):
        acceptDialog = ConnectionDialog(parent, name, members)
        acceptDialog.exec_()
        return acceptDialog.accepted
