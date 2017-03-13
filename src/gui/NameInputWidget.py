from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QMessageBox
from src.base import utils
from src.base.globals import INVALID_NAME_EMPTY, INVALID_NAME_CONTENT
from src.base.globals import INVALID_NAME_LENGTH, VALID_NAME, MAX_NAME_LENGTH
from src.base.globals import TITLE_INVALID_NAME, TITLE_EMPTY_NAME, EMPTY_NAME


class NameInputWidget(QWidget):

    def __init__(self, parent, image, image_width):
        QWidget.__init__(self, parent)
        self._connect = parent.connect
        self._restart = parent.restart
        self.name = parent.name
        _image = QPixmap(utils.getResourcePath(image))
        _image = _image.scaledToWidth(image_width, Qt.SmoothTransformation)
        self.image = QLabel(self)
        self.image.setPixmap(_image)
        self.name_input_label = QLabel('Username:', self)
        self.name_input = QLineEdit(self.name, self)
        self.name_input.setMaxLength(MAX_NAME_LENGTH)
        self.name_input.returnPressed.connect(self.__connect)
        self.connect_button = QPushButton('Connect', self)
        self.connect_button.resize(self.connect_button.sizeHint())
        self.connect_button.setAutoDefault(False)
        self.connect_button.clicked.connect(self.__connect)
        self.build()

    def build(self):
        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(self.name_input_label)
        hbox1.addWidget(self.name_input)
        hbox1.addStretch(1)
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox1)
        vbox.addWidget(self.connect_button)
        vbox.addStretch(1)
        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(self.image)
        hbox2.addSpacing(10)
        hbox2.addLayout(vbox)
        hbox2.addStretch(1)
        self.setLayout(hbox2)

    def __connect(self):
        name = str(self.name_input.text()).lower()
        status = utils.isNameInvalid(name)
        if status == VALID_NAME:
            self._connect(name)
            return
        elif status == INVALID_NAME_CONTENT:
            msg = (TITLE_INVALID_NAME, INVALID_NAME_CONTENT)
        elif status == INVALID_NAME_LENGTH:
            msg = (TITLE_INVALID_NAME, INVALID_NAME_LENGTH)
        elif status == INVALID_NAME_EMPTY:
            msg = (TITLE_EMPTY_NAME, EMPTY_NAME)
        else:
            pass
        QMessageBox.warning(self, *msg)
