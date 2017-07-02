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

class SMPInitiateDialog(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.clicked_button = constants.BUTTON_CANCEL

        # Set the title and icon
        self.setWindowTitle("Authenticate Buddy")
        self.setWindowIcon(QIcon(utils.getResourcePath('images/icon.png')))

        smp_question_label = QLabel("Question:", self)
        self.smp_question_input = QLineEdit(self)

        smp_answer_label = QLabel("Answer (case sensitive):", self)
        self.smp_answer_input = QLineEdit(self)

        okay_button = QPushButton(QIcon.fromTheme('dialog-ok'), "OK", self)
        cancel_button = QPushButton(QIcon.fromTheme('dialog-cancel'), "Cancel", self)

        key_icon = QLabel(self)
        key_icon.setPixmap(QPixmap(utils.getResourcePath('images/fingerprint.png')).scaledToWidth(50, Qt.SmoothTransformation))

        help_label = QLabel("In order to ensure that no one is listening in on your conversation\n"
                           "it's best to verify the identity of your buddy by entering a question\n"
                           "that only your buddy knows the answer to.")

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
        vbox.addWidget(self.smp_question_input)
        vbox.addWidget(smp_answer_label)
        vbox.addWidget(self.smp_answer_input)
        vbox.addLayout(buttons)

        self.setLayout(vbox)

    def buttonClicked(self, button):
        self.smpQuestion = self.smp_question_input.text()
        self.smpAnswer = self.smp_answer_input.text()
        self.clickedButton = button
        self.close()

    @staticmethod
    def getQuestionAndAnswer():
        dialog = SMPInitiateDialog()
        dialog.exec_()
        return dialog.smp_question, dialog.smp_answer, dialog.clicked_button