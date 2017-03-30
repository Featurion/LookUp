from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from src.base import utils
from src.gui.InputWidget import InputWidget


class LoginWindow(QDialog):

    def __init__(self, parent, name):
        QDialog.__init__(self, parent)
        self.name = name
        self.restart = False
        self.setWindowTitle('LookUp')
        self.setWindowIcon(QIcon(utils.getResourcePath('images/icon.png')))
        self.build()

    def build(self):
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(InputWidget(self,
                                   'images/splash_icon.png', 200,
                                   'Username:'))
        vbox.addStretch(1)
        self.setLayout(vbox)
        utils.resizeWindow(self, 500, 200)
        utils.centerWindow(self)

    def connect(self, name):
        self.name = name
        self.close()

    def restart(self):
        self.restart = True
