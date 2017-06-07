from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from src.base import utils


class ConnectingWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        _gif = QMovie(utils.getResourcePath('images/waiting.gif'))
        _gif.start()
        self.connecting_image = QLabel(self)
        self.connecting_image.setMovie(_gif)
        self.connecting_label = QLabel(self)
        self.build()

    def build(self):
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.connecting_image, alignment=Qt.AlignCenter)
        hbox.addSpacing(10)
        hbox.addWidget(self.connecting_label, alignment=Qt.AlignCenter)
        hbox.addStretch(1)
        self.setLayout(hbox)

    def setConnectingToName(self, name):
        self.connecting_label.setText('Connecting to {0}...'.format(name))
