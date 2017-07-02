import os
import signal

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout

from src.gui.QLine import QLine
from src.base import constants, utils

class SMPRespondDialog(QDialog):

    def __init__(self, name, question, parent=None):
        QDialog.__init__(self, parent)

        self.clicked_button = constants.BUTTON_CANCEL

        # Set the title and icon
        self.setWindowTitle("Authenticate %s" % name)
        self.setWindowIcon(QIcon(utils.getResourcePath('images/icon.png')))

        smp_question_label = QLabel("Question: <b>%s</b>" % question, self)

        smp_answer_label = QLabel("Answer (case sensitive):", self)
        self.smp_answer_input = QLineEdit(self)

        okay_button = QPushButton(QIcon.fromTheme('dialog-ok'), "OK", self)
        cancel_button = QPushButton(QIcon.fromTheme('dialog-cancel'), "Cancel", self)

        key_icon = QLabel(self)
        key_icon.setPixmap(QPixmap(utils.getResourcePath('images/fingerprint.png')).scaledToWidth(60, Qt.SmoothTransformation))

        help_label = QLabel("%s has requested to authenticate your conversation by asking you a\n"
                           "question only you should know the answer to. Enter your answer below\n"
                           "to authenticate your conversation.\n\n"
                           "You may wish to ask your buddy a question as well." % name)

        okay_button.clicked.connect(lambda: self.buttonClicked(constants.BUTTON_OKAY))
        cancel_button.clicked.connect(lambda: self.buttonClicked(constants.BUTTON_CANCEL))

        help_layout = QHBoxLayout()
        help_layout.addStretch(1)
        help_layout.addWidget(key_icon)
        help_layout.addSpacing(15)
        help_layout.addWidget(help_label)
        help_layout.addStretch(1)

        # Float the buttons to the right
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(okay_button)
        buttons.addWidget(cancel_button)

        vbox = QVBoxLayout()
        vbox.addLayout(help_layout)
        vbox.addWidget(QLine())
        vbox.addWidget(smp_question_label)
        vbox.addWidget(smp_answer_label)
        vbox.addWidget(self.smp_answer_input)
        vbox.addLayout(buttons)

        self.setLayout(vbox)

    def buttonClicked(self, button):
        self.smp_answer = self.smp_answer_input.text()
        self.clicked_button = button
        self.close()

    @staticmethod
    def getAnswer(name, question):
        dialog = SMPRespondDialog(name, question)
        dialog.exec_()
        return dialog.smp_answer, dialog.clicked_button