from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QMovie, QPixmap, QFontMetrics
from PyQt5.QtWidgets import QLabel, QTextEdit, QLineEdit, QPushButton
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QTextBrowser
from PyQt5.QtWidgets import QStackedWidget, QWidget, QSplitter

from src import constants, client
from src.gui import utils


class Connecting(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        _gif = QMovie('images/waiting.gif')
        _gif.start()

        self.connecting_image = QLabel(self)
        self.connecting_image.setMovie(_gif)

        self.connecting_label = QLabel(self)
        self.title = ''

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.connecting_image, alignment = Qt.AlignCenter)
        hbox.addSpacing(1)
        hbox.addWidget(self.connecting_label, alignment = Qt.AlignCenter)
        hbox.addStretch(1)
        self.setLayout(hbox)

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, name : str):
        self._title = name

        if self._title:
            self.connecting_label.setText('Connecting to ' + self._title)
        else:
            self.connecting_label.setText('Connecting')


class Input(QWidget):

    def __init__(self, parent,
                 image, image_width,
                 label_text, button_text,
                 max_chars,
                 connector):
        super().__init__(parent)

        _image = QPixmap(image)
        _image = _image.scaledToWidth(image_width, Qt.SmoothTransformation)
        self.image = QLabel(self)
        self.image.setPixmap(_image)

        self.label = QLabel(label_text, self)
        self.input = QLineEdit('', self)
        self.input.returnPressed.connect(lambda: connector(self.text))

        if max_chars is not None:
            self.input.setMaxLength(max_chars)

        self.button = QPushButton(button_text, self)
        self.button.resize(self.button.sizeHint())
        self.button.setAutoDefault(False)
        self.button.clicked.connect(lambda: connector(self.text))

        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(self.label)
        hbox1.addWidget(self.input)
        hbox1.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox1)
        vbox.addWidget(self.button)
        vbox.addStretch(1)

        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(self.image)
        hbox2.addSpacing(10)
        hbox2.addLayout(vbox)
        hbox2.addStretch(1)
        self.setLayout(hbox2)

    @property
    def text(self):
        return self.input.text()

    @text.setter
    def text(self, text):
        self.input.setText(text)


class ChatWidget(QWidget):

    def __init__(self, tab):
        QWidget.__init__(self, tab)

        self._tab = tab

        self.chat_log = QTextBrowser()
        self.chat_log.setOpenExternalLinks(True)

        self.chat_input = QTextEdit()
        self.chat_input.installEventFilter(self)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)

        self.invite_button = QPushButton('Invite')
        self.invite_button.clicked.connect(self.send_invite)

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
        splitter.addWidget(self.chat_log)
        splitter.addWidget(input_wrapper)
        splitter.setSizes([int(self.parent().height()), 1])

        hbox = QHBoxLayout()
        hbox.addWidget(splitter)
        self.setLayout(hbox)

    def send_message(self):
        if self._tab._zone:
            self.window().interface._client.synchronous_send(
                command = constants.CMD_MSG,
                recipient = self._tab._zone.id,
                data = self.chat_input.toPlainText())
        else:
            # Can't send message without zone
            pass

    def send_invite(self):
        self._tab.input_widget.text = ''
        self._tab.widget_stack.setCurrentIndex(0)


class ChatTab(QWidget):

    update_title_signal = pyqtSignal(str)

    def __init__(self, parent, member_names):
        super().__init__(parent)

        self.update_title_signal.connect(self._update_title)

        if member_names:
            self.__member_data = {name: None for name in member_names}
        else:
            self.__member_data = {}

        self._zone = None
        self.__unread = 0

        self.input_widget = Input(
            self,
            'images/new_chat.png', 150,
            'Username:', 'LookUp',
            constants.MAX_NAME_LENGTH,
            self.connect)
        self.chat_widget = ChatWidget(self)

        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(self.input_widget)
        self.widget_stack.addWidget(self.chat_widget)

        _layout = QHBoxLayout()
        _layout.addWidget(self.widget_stack)
        self.setLayout(_layout)

    def connect(self, name):
        self._zone = client.LookUpZone(
            self, self.window().interface._client)
        self.window().interface._client._zones.add(self._zone)

        self.window().interface._client.synchronous_send(
            command = constants.CMD_HELLO,
            recipient = self._zone.id,
            data = [name])
        self.widget_stack.setCurrentIndex(1)

    @pyqtSlot(str)
    def _update_title(self, title):
        index = self.window().chat_tabs.indexOf(self)
        self.window().chat_tabs.setTabText(index, title)
        self.widget_stack.currentWidget().title = title
