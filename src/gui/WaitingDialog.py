from PyQt5.QtWidgets import QDialog, QLabel
from PyQt5.QtGui import QMovie
from src.base.globals import getAbsoluteImagePath


class WaitingDialog(QDialog):

    def __init__(self, parent, text=''):
        QDialog.__init__(self, parent)
        spinner = QMovie(getAbsoluteImagePath('waiting.gif'))
        spinner.start()
        waiting_image_label = QLabel(self)
        waiting_image_label.setMovie(spinner)
        waiting_label = QLabel(text, self)
        self.build()

    def build(self):
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(waiting_image_label)
        hbox.addSpacing(10)
        hbox.addWidget(waiting_label)
        hbox.addStretch(1)
        self.setLayout(hbox)
