import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QTextEdit, QPushButton
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QTextBrowser
from PyQt5.QtWidgets import QWidget, QSplitter

from src import constants


class ChatWidget(QWidget):

    def __init__(self, tab):
        QWidget.__init__(self, tab)

        self._tab = tab

        self.chat_browser = QTextBrowser()
        self.chat_browser.setOpenExternalLinks(True)

        self.chat_input = QTextEdit()
        self.chat_input.installEventFilter(self)
        self.chat_input.textChanged.connect(self.send_typing_message)
        self.typing_stamp = -1

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)

        self.invite_button = QPushButton('Invite')
        self.invite_button.clicked.connect(self.goto_invite)

        font_metrics = QFontMetrics(self.chat_input.font())
        self.chat_input.setMinimumHeight(font_metrics.lineSpacing() * 3)
        self.send_button.setFixedHeight(font_metrics.lineSpacing() * 2)
        self.invite_button.setFixedHeight(font_metrics.lineSpacing() * 2)

        hbox = QHBoxLayout()
        hbox.addWidget(self.chat_input)
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.send_button)
        vbox.addStretch(1)
        vbox.addWidget(self.invite_button)
        vbox.addStretch(1)
        hbox.addLayout(vbox)

        input_wrapper = QWidget()
        input_wrapper.setLayout(hbox)
        input_wrapper.setMinimumHeight(font_metrics.lineSpacing() * 3.7)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.chat_browser)
        splitter.addWidget(input_wrapper)
        splitter.setSizes([int(self.parent().height()), 1])

        hbox = QHBoxLayout()
        hbox.addWidget(splitter)
        self.setLayout(hbox)

    def send_typing_message(self):
        is_typing = bool(self.chat_input.toPlainText())
        timer = time.time() - self.typing_stamp

        if is_typing:
            if not self.typing_stamp:
                # Exceeded timer, don't notify
                return
            if self.typing_stamp == -1:
                # Started typing
                self.typing_stamp = time.time()
            elif timer > constants.TYPING_TIMEOUT:
                # Done notifying
                self.typing_stamp = 0
            else:
                # Still typing
                return
        else:
            # Not typing
            self.typing_stamp = -1

        if self._tab._zone:
            conn.synchronous_send(
                command = constants.CMD_MSG_TYPING,
                recipient = self._tab._zone.id,
                timestamp = self.typing_stamp)
        else:
            # Can't send message without zone
            pass

    def send_message(self, ts = None):
        msg = self.chat_input.toPlainText()

        if msg and self._tab._zone:
            conn.synchronous_send(
                command = constants.CMD_MSG,
                recipient = self._tab._zone.id,
                data = msg,
                timestamp = ts or None)
        else:
            # There's no zone, so these messages don't actually go anywhere,
            # but they do get added to the chat log.
            self._tab.add_message(time.time(), conn.name, msg)

        self.chat_input.clear()

    def delete_message(self, ts):
        if self._tab._zone:
            conn.synchronous_send(
                command = constants.CMD_MSG_DEL,
                recipient = self._tab._zone.id,
                timestamp = ts)
        else:
            # Can't delete message without zone
            pass

    def goto_invite(self):
        self._tab.input_widget.text = ''
        self._tab.widget_stack.setCurrentIndex(0)

    def update_chat(self):
        full_log = ''

        for (ts, sender), message in sorted(self._tab._chat_log.items()):
            if sender == 'server':
                color = '#000000'
            elif sender == conn.name:
                color = '#0000CC'
            else:
                color = '#CC0000'

            full_log += (
                '<body style="white-space: pre">'
                '<font color="{0}">'
                '({1}) '
                '<strong>{2}</strong>: '
                '</font>'
                '{3}</body>').format(
                    color,
                    time.strftime('%H:%M:%S', time.localtime(ts)),
                    sender,
                    message)

        scrollbar = self.chat_browser.verticalScrollBar()

        if scrollbar.value() != scrollbar.maximum() \
           and sender != conn.name:
            should_scroll = False
        else:
            should_scroll = True

        self.chat_browser.setText(full_log)

        if should_scroll:
            scrollbar.setValue(scrollbar.maximum())
