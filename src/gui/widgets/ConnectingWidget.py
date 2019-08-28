from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget


class ConnectingWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        _gif = QMovie('images/waiting.gif')
        _gif.start()

        self.connecting_image = QLabel(self)
        self.connecting_image.setMovie(_gif)

        self.connecting_label = QLabel(self)
        self.title = ''

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.connecting_image, alignment=Qt.AlignCenter)
        hbox.addSpacing(1)
        hbox.addWidget(self.connecting_label, alignment=Qt.AlignCenter)
        hbox.addStretch(1)
        self.setLayout(hbox)

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, name: str):
        self._title = name

        if self._title:
            self.connecting_label.setText('Connecting to ' + self._title)
        else:
            self.connecting_label.setText('Connecting')
