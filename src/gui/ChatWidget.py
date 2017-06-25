import re
from threading import Thread

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QWidget, QTextBrowser, QTextEdit, QPushButton
from PyQt5.QtWidgets import QHBoxLayout, QSplitter

from src.base import constants, utils
from src.gui.MultipleInputWidget import MultipleInputWidget

class ChatWidget(QWidget):

    URL_REGEX = re.compile(constants.URL_REGEX)

    def __init__(self, tab):
        QWidget.__init__(self, tab)

        self.__tab = tab

        self.disabled = False
        self.cleared = False

        self.chat_log = QTextBrowser()
        self.chat_log.setOpenExternalLinks(True)

        self.chat_input = QTextEdit()
        self.chat_input.textChanged.connect(self.chatInputTextChanged)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.sendMessage)

        font_metrics = QFontMetrics(self.chat_input.font())
        self.chat_input.setMinimumHeight(font_metrics.lineSpacing() * 3)
        self.send_button.setFixedHeight(font_metrics.lineSpacing() * 3)

        hbox = QHBoxLayout()
        hbox.addWidget(self.chat_input)
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

        self.input_widget = MultipleInputWidget(self,
                                                'images/new_chat.png', 150,
                                                'Usernames:', 'Add',
                                                32, self.addUser,
                                                self.addInput)

        self.add_user_button = QPushButton('Add', self)
        self.add_user_button.setGeometry(584, 8, 31, 23)
        self.add_user_button.clicked.connect(self.enterAddScreen)
        self.add_user_button.show()

        self.cancel_button = QPushButton('Cancel', self.input_widget)
        self.cancel_button.setGeometry(570, 8, 45, 23)
        self.cancel_button.clicked.connect(self.exitAddScreen)
        self.cancel_button.show()

        self.typing_timer = QTimer()
        self.typing_timer.setSingleShot(True)
        self.typing_timer.timeout.connect(self.stoppedTyping)

        del font_metrics
        del hbox
        del input_wrapper
        del splitter

    def cleanup(self):
        self.__tab = None # cleaned up in ZoneManager
        self.disabled = None
        self.cleared = None
        del self.chat_log
        self.chat_log = None
        del self.chat_input
        self.chat_input = None
        del self.send_button
        self.send_button = None
        self.input_widget = None
        del self.add_user_button
        self.add_user_button = None

    def getClient(self):
        return self.__tab.getClient()

    def getTab(self):
        return self.__tab

    def enterAddScreen(self):
        self.getTab().widget_stack.setCurrentIndex(4)

    def exitAddScreen(self):
        self.getTab().widget_stack.setCurrentIndex(3)

    def addInput(self):
        _iw = MultipleInputWidget(*self.input_widget._data,
                                  self.input_widget.getInputsText(),
                                  len(self.input_widget.inputs) + 1)
        self.cancel_button.setParent(_iw)
        self.getTab().widget_stack.removeWidget(self.input_widget)
        self.input_widget = _iw
        self.getTab().widget_stack.insertWidget(4, self.input_widget)
        self.getTab().widget_stack.setCurrentIndex(4)

    def addUser(self, *names):
        for name in set(names):
            # Validate the given name
            name_status = utils.isNameInvalid(name)
            if name_status == constants.VALID_NAME:
                self.getTab().getZone().addUser(name)
            elif name_status == constants.INVALID_NAME_CONTENT:
                self.getTab().interface.error_signal.emit(constants.TITLE_INVALID_NAME, constants.INVALID_NAME_CONTENT)
            elif name_status == constants.INVALID_NAME_LENGTH:
                self.getTab().interface.error_signal.emit(constants.TITLE_INVALID_NAME, constants.INVALID_NAME_LENGTH)
            elif name_status == constants.INVALID_EMPTY_NAME:
                self.getTab().interface.error_signal.emit(constants.TITLE_EMPTY_NAME, constants.EMPTY_NAME)

    def sendMessage(self):
        if self.disabled:
            return
        else:
            pass

        self.typing_timer.stop()

        text = str(self.chat_input.toPlainText())[:-1]

        # Don't send empty messages
        if text == '':
            return

        # Clear the chat input
        self.cleared = True
        self.chat_input.clear()

        # Convert URLs into clickable links
        text = self.__linkify(text)

        # Add the message to the message queue to be sent
        _t = Thread(target=self.getTab().getZone().sendChatMessage,
                    args=(text,),
                    daemon=True).start()
        del _t

        self.appendMessage(text, utils.getTimestamp(), constants.SENDER, self.getClient().getName())

        del text

    def sendTypingStatus(self, status):
        _t = Thread(target=self.getTab().getZone().sendTypingMessage,
                    args=(status,),
                    daemon=True).start()
        del _t

    def disable(self):
        self.disabled = True
        self.chat_input.setReadOnly(True)

    def enable(self):
        self.disabled = False
        self.chat_input.setReadOnly(False)

    def appendMessage(self, message: str, timestamp: float, source: int, name: str):
        color = self.__getColor(source)

        timestamp = utils.formatTimestamp(timestamp)

        timestamp = '<font color="' + str(color) + '">(' + str(timestamp) + ') <strong>' + \
                    name + ':</strong></font> '

        message = timestamp + message

        # If the user has scrolled up (current value != maximum), do not move the scrollbar
        # to the bottom after appending the message
        should_scroll = True
        scrollbar = self.chat_log.verticalScrollBar()
        if scrollbar.value() != scrollbar.maximum() and source != constants.SENDER:
            should_scroll = False

        self.chat_log.append(message)

        # Move the vertical scrollbar to the bottom of the chat log
        if should_scroll:
            scrollbar.setValue(scrollbar.maximum())

    def __linkify(self, text):
        matches = self.URL_REGEX.findall(text)
        for match in matches:
            text = text.replace(match[0],
                                '<a href="{0}">{0}</a>'.format(match[0]))

        del matches

        return text

    def __getColor(self, source):
        if source == constants.SENDER:
            if utils.isLightTheme:
                return '#0000CC'
            else:
                return '#6666FF'
        elif source == constants.RECEIVER:
            if utils.isLightTheme:
                return '#CC0000'
            else:
                return '#CC3333'
        else:
            if utils.isLightTheme:
                return '#000000'
            else:
                return '#FFFFFF'

    def chatInputTextChanged(self):
        if self.cleared:
            self.cleared = False
            return
        if str(self.chat_input.toPlainText())[-1:] == '\n':
            self.sendMessage()
        else:
            # Start a timer to check for the user stopping typing
            self.typing_timer.start(constants.TYPING_TIMEOUT)
            self.sendTypingStatus(constants.TYPING_START)

    def stoppedTyping(self):
        self.typing_timer.stop()
        if str(self.chat_input.toPlainText()) == '':
            self.sendTypingStatus(constants.TYPING_STOP_WITHOUT_TEXT)
        else:
            self.sendTypingStatus(constants.TYPING_STOP_WITH_TEXT)