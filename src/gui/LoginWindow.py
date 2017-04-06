from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QMessageBox
from src.base import utils
from src.base.globals import INVALID_EMPTY_NAME, INVALID_NAME_CONTENT
from src.base.globals import INVALID_NAME_LENGTH, VALID_NAME, MAX_NAME_LENGTH
from src.base.globals import TITLE_INVALID_NAME, TITLE_EMPTY_NAME
from src.base.globals import NAME_CONTENT, NAME_LENGTH, EMPTY_NAME
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
        _iw =InputWidget(self,
                         'images/splash_icon.png', 200,
                         'Username:', 'Login',
                         self.__connect)
        _iw.input.setMaxLength(MAX_NAME_LENGTH)
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(_iw)
        vbox.addStretch(1)
        self.setLayout(vbox)
        utils.resizeWindow(self, 500, 200)
        utils.centerWindow(self)

    def getName(self):
        return self.name

    def __connect(self, text):
        name = text.lower()
        status = utils.isNameInvalid(name)
        if status == VALID_NAME:
            self.connect(name)
            return
        elif status == INVALID_NAME_CONTENT:
            msg = (TITLE_INVALID_NAME, NAME_CONTENT)
        elif status == INVALID_NAME_LENGTH:
            msg = (TITLE_INVALID_NAME, NAME_LENGTH)
        elif status == INVALID_EMPTY_NAME:
            msg = (TITLE_EMPTY_NAME, EMPTY_NAME)
        else:
            pass
        QMessageBox.warning(self, *msg)

    def connect(self, name):
        self.name = name
        self.close()

    def restart(self):
        self.restart = True
