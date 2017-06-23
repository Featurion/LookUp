import re
from threading import Thread

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QWidget, QTextBrowser, QTextEdit, QPushButton
from PyQt5.QtWidgets import QHBoxLayout, QSplitter

from src.base import constants, utils


class ChatWidget(QWidget):

    URL_REGEX = re.compile(constants.URL_REGEX)

    class _MessageLog(list):

        def __init__(self, widget, *args):
            list.__init__(self, args)
            self.sort()
            self.widget = widget

            del widget

        def sort(self):
            list.sort(self, key=lambda i: i[0])

        def addMessage(self, msg, ts):
            list.append(self, (ts, msg))
            self.sort()
            self.update()

            del ts
            del msg

        def update(self):
            full_text = '<br>'.join(msg for ts, msg in self)
            self.widget.chat_log.setText(full_text)

            del ts
            del msg
            del full_text

    def __init__(self, tab):
        QWidget.__init__(self, tab)

        self.__tab = tab

        self.disabled = False
        self.cleared = False
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
        splitter.setSizes([int(self.__tab.height()), 1])

        hbox = QHBoxLayout()
        hbox.addWidget(splitter)
        self.setLayout(hbox)

        del font_metrics
        del hbox
        del input_wrapper
        del splitter

    def cleanup(self):
        self.__tab = None # cleaned up in ZoneManager
        self.disabled = None
        self.cleared = None
        del self.log
        self.log = None
        del self.chat_log
        self.chat_log = None
        del self.input
        self.input = None
        del self.send_button
        self.send_button = None

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

                _t = Thread(target=self.getTab().getSession().sendChatMessage,
                            args=(text,),
                            daemon=True).start()
                del _t

            del text

    def disable(self):
        self.disabled = True
        self.input.setReadOnly(True)

    def enable(self):
        self.disabled = False
        self.input.setReadOnly(False)

    def __linkify(self, text):
        matches = self.URL_REGEX.findall(text)
        for match in matches:
            text = text.replace(match[0],
                                '<a href="{0}">{0}</a>'.format(match[0]))

        del match
        del matches

        return text

    def chatInputTextChanged(self):
        if self.cleared:
            self.cleared = False
            return
        if str(self.input.toPlainText())[-1:] == '\n':
            self.send()
