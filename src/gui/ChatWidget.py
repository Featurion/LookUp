import re
from threading import Thread
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QWidget, QTextBrowser, QTextEdit, QPushButton
from PyQt5.QtWidgets import QHBoxLayout, QSplitter
from src.base import utils
from src.base.globals import URL_REGEX


class ChatWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.tab = parent
        self.client = self.tab.client

        self.disabled = False
        self.cleared = False
        self.url_regex = re.compile(URL_REGEX)

        self.log = QTextBrowser()
        self.log.setOpenExternalLinks(True)

        self.input = QTextEdit()
        self.input.textChanged.connect(self.chatInputTextChanged)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send)

        self.build()

    def build(self):
        font_metrics = QFontMetrics(self.input.font())
        self.input.setMinimumHeight(font_metrics.lineSpacing() * 3)
        self.send_button.setFixedHeight(font_metrics.lineSpacing() * 3)

        hbox = QHBoxLayout()
        hbox.addWidget(self.input)
        hbox.addWidget(self.send_button)

        input_wrapper = QWidget()
        input_wrapper.setLayout(hbox)
        input_wrapper.setMinimumHeight(font_metrics.lineSpacing() * 3.7)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.log)
        splitter.addWidget(input_wrapper)
        splitter.setSizes([int(self.tab.height()), 1])

        hbox = QHBoxLayout()
        hbox.addWidget(splitter)
        self.setLayout(hbox)

    def getTab(self):
        return self.tab

    def send(self):
        if self.disabled:
            return
        else:
            text = str(self.input.toPlainText())[:-1]
            if not text:
                return
            else:
                self.cleared = True
                self.input.clear()

                Thread(target=self.getTab().getSession().sendChatMessage,
                       args=(text,),
                       daemon=True).start()

    def disable(self):
        self.disabled = True
        self.input.setReadOnly(True)

    def enable(self):
        self.disabled = False
        self.input.setReadOnly(False)

    def __linkify(self, text):
        matches = self.url_regex.findall(text)
        for match in matches:
            text = text.replace(match[0],
                                '<a href="{0}">{0}</a>'.format(match[0]))
        return text

    def chatInputTextChanged(self):
        if self.cleared:
            self.cleared = False
            return
        if str(self.input.toPlainText())[-1:] == '\n':
            self.send()
