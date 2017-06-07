import re
from threading import Thread
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QWidget, QTextBrowser, QTextEdit, QPushButton
from PyQt5.QtWidgets import QHBoxLayout, QSplitter
from src.base import utils
from src.base.globals import URL_REGEX


class ChatWidget(QWidget):

    class _MessageLog(list):

        def __init__(self, widget, *args):
            list.__init__(self, args)
            self.sort()
            self.widget = widget

        def sort(self):
            list.sort(self, key=lambda i: i[0])

        def addMessage(self, msg, ts):
            list.append(self, (ts, msg))
            self.sort()
            self.update()

        def update(self):
            full_text = '<br>'.join(msg for ts, msg in self)
            self.widget.chat_log.setText(full_text)

    def __init__(self, tab):
        QWidget.__init__(self, tab)

        self.tab = tab

        self.disabled = False
        self.cleared = False
        self.url_regex = re.compile(URL_REGEX)
        self.log = ChatWidget._MessageLog(self)

        self.chat_log = QTextBrowser()
        self.chat_log.setOpenExternalLinks(True)

        self.input = QTextEdit()
        self.input.textChanged.connect(self.chatInputTextChanged)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send)

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
        splitter.addWidget(self.chat_log)
        splitter.addWidget(input_wrapper)
        splitter.setSizes([int(self.tab.height()), 1])

        hbox = QHBoxLayout()
        hbox.addWidget(splitter)
        self.setLayout(hbox)

    def getClient(self):
        return self.__tab.getClient()

    def getTab(self):
        return self.__tab

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
