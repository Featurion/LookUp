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
