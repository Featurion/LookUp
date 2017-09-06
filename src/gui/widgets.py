from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout

from src.gui import utils


class Connecting(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        _gif = QMovie('images/waiting.gif')
        _gif.start()

        self.connecting_image = QLabel(self)
        self.connecting_image.setMovie(_gif)
        self.connecting_label = QLabel(self)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.connecting_image, alignment = Qt.AlignCenter)
        hbox.addSpacing(10)
        hbox.addWidget(self.connecting_label, alignment = Qt.AlignCenter)
        hbox.addStretch(1)
        self.setLayout(hbox)

    def setConnectingToName(self, name):
        if name:
            self.connecting_label.setText('Connecting to ' + name)
        else:
            self.connecting_label.setText('Connecting')


class Input(QWidget):

    def __init__(self, parent,
                 image, image_width,
                 label_text, button_text,
                 max_chars,
                 connector):
        QWidget.__init__(self, parent)

        _image = QPixmap(image)
        _image = _image.scaledToWidth(image_width, Qt.SmoothTransformation)
        self.image = QLabel(self)
        self.image.setPixmap(_image)

        self.label = QLabel(label_text, self)
        self.input = QLineEdit('', self)
        self.input.returnPressed.connect(lambda: connector(self.getText()))

        if max_chars is not None:
            self.input.setMaxLength(max_chars)

        self.button = QPushButton(button_text, self)
        self.button.resize(self.button.sizeHint())
        self.button.setAutoDefault(False)
        self.button.clicked.connect(lambda: connector(self.getText()))

        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(self.label)
        hbox1.addWidget(self.input)
        hbox1.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox1)
        vbox.addWidget(self.button)
        vbox.addStretch(1)

        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(self.image)
        hbox2.addSpacing(10)
        hbox2.addLayout(vbox)
        hbox2.addStretch(1)
        self.setLayout(hbox2)

    def getText(self):
        return self.input.text()

    def setText(self, text):
        self.input.setText(text)
