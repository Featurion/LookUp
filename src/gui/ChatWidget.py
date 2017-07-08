import re
from threading import Thread

from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QWidget, QTextBrowser, QTextEdit, QPushButton
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QSplitter

from src.base import constants, utils
from src.base.UniqueIDManager import UniqueIDManager
from src.gui.MultipleInputWidget import MultipleInputWidget

class ChatWidget(QWidget):

    class _MessageLog(list):

        def __init__(self, widget, *args):
            list.__init__(self, args)
            self.sort()
            self.widget = widget

        def sort(self):
            try:
                list.sort(self, key=lambda i: i[2])
            except IndexError: # This can be (shouldn't be) caused by the only message in the chat being deleted, no harm done if it happens
                pass

        def addMessage(self, id_, msg, ts):
            list.append(self, [id_, msg, ts])
            self.sort()
            self.update()

        def editMessage(self, msg, new_msg, text_only=False, delete=False):
            for message in self:
                if msg in message[1]:
                    index = self.index(message)
            message_text = self[index][1]

            if text_only:
                split = msg.rsplit(' ', 1)
                split[1] = new_msg
                new_msg = split[0] + split[1]

            edit_text = message_text.replace(msg, new_msg)

            if delete:
                self.remove(msg)
            else:
                self[index][1] = edit_text

            self.sort()
            self.update()

            del message_text
            del delete
            del edit_text
            del msg
            del new_msg

        def delMessage(self, msg):
            self.editMessage(msg, '', True)

            del msg

        def getMessage(self, id_: str):
            for message in self:
                if message[0] == id_:
                    return message[1]

        def update(self):
            full_text = '<br>'.join(msg[1] for msg in self)
            self.widget.chat_log.setText(full_text)

            del full_text

    URL_REGEX = re.compile(constants.URL_REGEX)

    def __init__(self, tab):
        QWidget.__init__(self, tab)

        self.__tab = tab

        self.disabled = False
        self.cleared = False

        self.deleting = False
        self.typing = False

        self.chat_log = QTextBrowser()
        self.chat_log.setOpenExternalLinks(True)

        self.log = ChatWidget._MessageLog(self)

        self.chat_input = QTextEdit()
        self.chat_input.textChanged.connect(self.chatInputTextChanged)
        self.chat_input.installEventFilter(self)

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

        self.last_text_size = 0

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

        self.typing_timer.stop()

        text = str(self.chat_input.toPlainText()) + '\n'

        # Don't send empty messages
        if text == '':
            return

        # Clear the chat input
        self.cleared = True
        self.chat_input.clear()

        # Convert URLs into clickable links
        text = self.__linkify(text)

        # Append the message to the log and get the message ID
        id_ = self.appendMessage(text,
                                 utils.getTimestamp(),
                                 constants.SENDER,
                                 self.getClient().getName(),
                                 '')

        # Add the message to the message queue to be sent
        self.getTab().getZone().sendChatMessage(text, id_)

        del text
        del id_

    def sendTypingStatus(self, status):
        self.getTab().getZone().sendTypingMessage(status)

    def disable(self):
        self.disabled = True
        self.chat_input.setReadOnly(True)

    def enable(self):
        self.disabled = False
        self.chat_input.setReadOnly(False)

    def appendMessage(self, message: str, timestamp: float, source: int, name: str, id_: str):
        color = self.__getColor(source, True)

        formatted_timestamp = utils.formatTimestamp(timestamp)

        if not id_:
            id_ = str(UniqueIDManager().generateId()) # Generate a unique ID for the message

        message = '<font color="' + color + '">' \
                  + '(' + formatted_timestamp + ')' \
                  + ' <strong>' + name + ':</strong>' \
                  + '</font> ' + message

        # If the user has scrolled up (current value != maximum), do not move the scrollbar
        # to the bottom after appending the message
        should_scroll = True
        scrollbar = self.chat_log.verticalScrollBar()
        if scrollbar.value() != scrollbar.maximum() and source != constants.SENDER:
            should_scroll = False

        self.log.addMessage(id_, message, timestamp)

        # Move the vertical scrollbar to the bottom of the chat log
        if should_scroll:
            scrollbar.setValue(scrollbar.maximum())

        return id_

    def confirmMessage(self, text: str, name: str, id_: str):
        message = self.log.getMessage(id_)

        transparent_color = self.__getColor(constants.SENDER, True)
        confirm_color = self.__getColor(constants.SENDER)

        new_message = message.replace(transparent_color, confirm_color, 1)

        self.log.editMessage(message, new_message)

    def __linkify(self, text):
        matches = self.URL_REGEX.findall(text)
        for match in matches:
            text = text.replace(match[0],
                                '<a href="{0}">{0}</a>'.format(match[0]))

        del matches

        return text

    def __getColor(self, source, transparent=False):
        if source == constants.SENDER:
            if not transparent:
                return '#0000CC'
            else:
                return '#8787a8'
        elif source == constants.RECEIVER:
            return '#CC0000'
        else:
            return '#000000'

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress: # Check if this is a keypress
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return: # Check if enter (both regular and keypad) is being pressed
                modifiers = QApplication.keyboardModifiers()
                if modifiers: # Check if someone is using a key combination (for example Shift+Enter)
                    return QWidget.eventFilter(self, source, event)
                else: # Must be trying to send a message!
                    self.sendMessage()
                    return True
            else:
                return QWidget.eventFilter(self, source, event)
        return QWidget.eventFilter(self, source, event)

    def chatInputTextChanged(self):
        if self.cleared:
            self.cleared = False
            return

        plain_text = str(self.chat_input.toPlainText())
        size = len(plain_text)

        if size < self.last_text_size and self.last_text_size > 0 and not self.deleting:
            # User must be deleting text
            self.sendTypingStatus(constants.TYPING_DELETE_TEXT)
            self.deleting = True
            return
        elif size == 0:
            # Forget the timer, the user deleted all the text
            self.stoppedTyping()
        else:
            # Start a timer to check for the user stopping typing
            self.typing_timer.start(constants.TYPING_TIMEOUT)

            if not self.typing:
                self.sendTypingStatus(constants.TYPING_START)
                self.typing = True

            return

        self.deleting = False
        self.typing = False

    def stoppedTyping(self):
        self.typing_timer.stop()
        if str(self.chat_input.toPlainText()) == '':
            self.sendTypingStatus(constants.TYPING_STOP)
        else:
            self.sendTypingStatus(constants.TYPING_STOP_WITH_TEXT)
