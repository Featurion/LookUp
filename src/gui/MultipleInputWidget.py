from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from src.base import utils


class MultipleInputWidget(QWidget):

    def __init__(self, parent,
                 image, image_width,
                 label_text, button_text,
                 max_chars,
                 connector, addField,
                 defaults=[], num_inputs=1):
        QWidget.__init__(self, parent)
        self._data = (parent,
                      image, image_width,
                      label_text, button_text,
                      max_chars,
                      connector, addField)
        _image = QPixmap(utils.getResourcePath(image))
        _image = _image.scaledToWidth(image_width, Qt.SmoothTransformation)
        self.image = QLabel(self)
        self.image.setPixmap(_image)
        self.input_label = QLabel(label_text, self)
        self.inputs = [QLineEdit('', self) for _ in range(num_inputs)]

        if max_chars is not None:
            for _i in self.inputs:
                _i.setMaxLength(max_chars)

        self.connect_button = QPushButton(button_text, self)
        self.connect_button.resize(self.connect_button.sizeHint())
        self.connect_button.setAutoDefault(False)
        self.connect_button.clicked.connect(lambda: connector(*self.getInputsText()))
        self.build(defaults[:num_inputs])

    def build(self, _defaults):
        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(self.input_label)
        hbox1.addStretch(1)
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox1)
        for i in range(len(self.inputs)):
            _hb = QHBoxLayout()
            _hb.addWidget(self.inputs[i])
            if i == len(self.inputs) - 1:
                _button = QPushButton('+', self)
                _button.clicked.connect(self._data[-1])
                _hb.addWidget(_button)
            else:
                self.inputs[i].setText(_defaults[i])
            vbox.addLayout(_hb)
        vbox.addWidget(self.connect_button)
        vbox.addStretch(1)
        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(self.image)
        hbox2.addSpacing(10)
        hbox2.addLayout(vbox)
        hbox2.addStretch(1)
        self.setLayout(hbox2)

    def getInputs(self):
        return self.inputs

    def getInputsText(self):
        return [i.text() for i in self.getInputs()]
