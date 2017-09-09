from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout

class Input(QWidget):

    def __init__(self, parent,
                 image, image_width,
                 label_text, button_text,
                 max_chars,
                 connector):
        super().__init__(parent)

        _image = QPixmap(image)
        _image = _image.scaledToWidth(image_width, Qt.SmoothTransformation)
        self.image = QLabel(self)
        self.image.setPixmap(_image)

        self.label = QLabel(label_text, self)
        self.input = QLineEdit('', self)
        self.input.returnPressed.connect(lambda: connector(self.text))

        if max_chars is not None:
            self.input.setMaxLength(max_chars)

        self.button = QPushButton(button_text, self)
        self.button.resize(self.button.sizeHint())
        self.button.setAutoDefault(False)
        self.button.clicked.connect(lambda: connector(self.text))

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

    @property
    def text(self):
        return self.input.text()

    @text.setter
    def text(self, text):
        self.input.setText(text)
