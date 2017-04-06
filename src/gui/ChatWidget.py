import re

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QWidget

from src.base.globals import URL_REGEX
from src.base.globals import TYPING_TIMEOUT, TYPING_START
from src.base.globals import TYPING_STOP_WITHOUT_TEXT, TYPING_STOP_WITH_TEXT
from src.base.globals import SENDER, RECEIVER, SERVICE

from src.base import utils

class ChatWidget(QWidget):

    def __init__(self, client, parent):
        QWidget.__init__(self, parent)

        self.__members = {} # TODO: Zach

        self.client = client
        self.is_disabled = False
        self.was_cleared = False

        self.url_regex = re.compile(URL_REGEX)

        self.chat_log = QTextBrowser()
        self.chat_log.setOpenExternalLinks(True)

        self.chat_input = QTextEdit()
        self.chat_input.textChanged.connect(self.chatInputTextChanged)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.sendMessage)

        # Set the min height for the chatlog and a matching fixed height for the send button
        chat_input_font_metrics = QFontMetrics(self.chat_input.font())
        self.chat_input.setMinimumHeight(chat_input_font_metrics.lineSpacing() * 3)
        self.send_button.setFixedHeight(chat_input_font_metrics.lineSpacing() * 3)

        hbox = QHBoxLayout()
        hbox.addWidget(self.chat_input)
        hbox.addWidget(self.send_button)

        # Put the chatinput and send button in a wrapper widget so they may be added to the splitter
        chat_input_wrapper = QWidget()
        chat_input_wrapper.setLayout(hbox)
        chat_input_wrapper.setMinimumHeight(chat_input_font_metrics.lineSpacing() * 3.7)

        # Put the chat log and chat input into a splitter so the user can resize them at will
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.chat_log)
        splitter.addWidget(chat_input_wrapper)
        splitter.setSizes([int(parent.height()), 1])

        hbox = QHBoxLayout()
        hbox.addWidget(splitter)
        self.setLayout(hbox)

        self.typing_timer = QTimer()
        self.typing_timer.setSingleShot(True)
        self.typing_timer.timeout.connect(self.stoppedTyping)

    def chatInputTextChanged(self):
        # Check if the text changed was the text box being cleared to avoid sending an invalid typing status
        if self.was_cleared:
            self.was_cleared = False
            return

        if str(self.chat_input.toPlainText())[-1:] == '\n':
            self.sendMessage()
        else:
            # Start a timer to check for the user stopping typing
            self.typing_timer.start(TYPING_TIMEOUT)
            self.sendTypingStatus(TYPING_START)

    def stoppedTyping(self):
        self.typing_timer.stop()
        if str(self.chat_input.toPlainText()) == '':
            self.sendTypingStatus(TYPING_STOP_WITHOUT_TEXT)
        else:
            self.sendTypingStatus(TYPING_STOP_WITH_TEXT)

    def sendMessage(self):
        if self.is_disabled:
            return

        self.typing_timer.stop()

        text = str(self.chat_input.toPlainText())[:-1]

        # Don't send empty messages
        if text == '':
            return

        # Convert URLs into clickable links
        text = self.__linkify(text)

        # Add the message to the message queue to be sent
        # self.client.session_manager.getSessionById().sendChatMessage(text) - TODO: Zach

        # Clear the chat input
        self.was_cleared = True
        self.chat_input.clear()

        self.appendMessage(text, SENDER)

    def sendTypingStatus(self, status):
        pass
        # self.client.session_manager.getSessionById().sendTypingMessage(status)

    def showNowChattingMessage(self, nick):
        self.appendMessage("You are now securely chatting with " + self.__members + " :)",
                           SERVICE, show_timestamp_and_name=False)

        self.appendMessage("It's a good idea to verify the communcation is secure by selecting "
                           "\"authenticate buddy\" in the options menu.", SERVICE, show_timestamp_and_name=False)

        self.addNickButton = QPushButton('Add', self)
        self.addNickButton.setGeometry(584, 8, 31, 23)
        self.addNickButton.clicked.connect(parent.addInput)
        self.addNickButton.show()

    def appendMessage(self, message, source, show_timestamp_and_name=True):
        color = self.__getColor(source)

        # if show_timestamp_and_name: - TODO: Zach
        #     timestamp = '<font color="' + color + '">(' + utils.getTimestamp() + ') <strong>' + \
        #                 (self.client.getName() if source == SENDER else self.__members.getName()) + \
        #                 ':</strong></font> '
        # else:
        #     timestamp = ''

        # If the user has scrolled up (current value != maximum), do not move the scrollbar
        # to the bottom after appending the message
        should_scroll = True
        scrollbar = self.chat_log.verticalScrollBar()
        if scrollbar.value() != scrollbar.maximum() and source != SENDER:
            should_scroll = False

        # self.chat_log.append(timestamp + message) # TODO: Zach
        self.chat_log.append(message)

        # Move the vertical scrollbar to the bottom of the chat log
        if should_scroll:
            scrollbar.setValue(scrollbar.maximum())

    def __linkify(self, text):
        matches = self.url_regex.findall(text)

        for match in matches:
            text = text.replace(match[0], '<a href="%s">%s</a>' % (match[0], match[0]))

        return text

    def __getColor(self, source):
        if source == SENDER:
            if utils.isLightTheme:
                return '#0000CC'
            else:
                return '#6666FF'
        elif source == RECEIVER:
            if utils.isLightTheme:
                return '#CC0000'
            else:
                return '#CC3333'
        else:
            if utils.isLightTheme:
                return '#000000'
            else:
                return '#FFFFFF'

    def disable(self):
        self.is_disabled = True
        self.chat_input.setReadOnly(True)

    def enable(self):
        self.is_disabled = False
        self.chat_input.setReadOnly(False)