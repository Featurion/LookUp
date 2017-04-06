from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from src.base import utils


class InputWidget(QWidget):

    def __init__(self, parent,
                 image, image_width,
                 label_text, button_text,
                 connector):
        QWidget.__init__(self, parent)
        _image = QPixmap(utils.getResourcePath(image))
        _image = _image.scaledToWidth(image_width, Qt.SmoothTransformation)
        self.image = QLabel(self)
        self.image.setPixmap(_image)
        self.input_label = QLabel(label_text, self)
        if hasattr(parent, 'name'):
            self.input = QLineEdit(parent.name, self)
        else:
            self.input = QLineEdit('', self)
        self.input.returnPressed.connect(lambda: connector(self.input.text()))
        self.connect_button = QPushButton(button_text, self)
        self.connect_button.resize(self.connect_button.sizeHint())
        self.connect_button.setAutoDefault(False)
        self.connect_button.clicked.connect(lambda: connector(self.input.text()))
        self.build()

    def build(self):
        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(self.input_label)
        hbox1.addWidget(self.input)
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
