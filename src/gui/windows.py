from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QDialog, QMessageBox, QAction
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QSystemTrayIcon
from PyQt5.QtWidgets import QTabWidget, QToolButton, QToolBar, QMenu
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout

from src import constants, settings
from src.gui import widgets, utils


class LoginWindow(QDialog):

    def __init__(self, interface):
        super().__init__()

        self._interface = interface

        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(widgets.Connecting(self))

        self.input = widgets.Input(
            self,
            'images/splash_icon.png', 200,
            'Username:', 'Login',
            constants.MAX_NAME_LENGTH,
            self.__connect)
        self.widget_stack.addWidget(self.input)

        hbox = QHBoxLayout()
        hbox.addWidget(self.widget_stack)
        self.setLayout(hbox)

        self.setWindowTitle(settings.APP_NAME)
        self.setWindowIcon(QIcon('images/icon.png'))

        utils.resize_window(self, 500, 200)
        utils.center_window(self)

    def __connect(self, username):
        self.widget_stack.setCurrentIndex(0)
        self._interface._client._username = username


class ChatWindow(QMainWindow):

    def __init__(self, interface):
        super().__init__()

        self._interface = interface

        # window setup
        self.status_bar = self.statusBar()

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('images/icon.ico'))
        self.tray_icon.setToolTip(settings.APP_NAME)

        self.tray_menu = QMenu()
        _stop = QAction(
            'Exit', self,
            shortcut = 'Ctrl+Q', statusTip = 'Exit',
            triggered = self.close)
        _stop.setIcon(QIcon('images/exit.png'))
        self.tray_menu.addAction(_stop)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.setVisible(True)

        # widget setup
        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(widgets.Connecting(self))

        self.chat_tabs = QTabWidget(self)
        self.chat_tabs.setTabsClosable(True)
        self.chat_tabs.setMovable(True)
        self.chat_tabs.tabCloseRequested.connect(self.close_tab)
        self.chat_tabs.currentChanged.connect(self._tab_changed)
        self.widget_stack.addWidget(self.chat_tabs)

        self.widget_stack.setCurrentIndex(1)

        self.status_bar = self.statusBar()

        # menubar setup
        new_chat_icon = QIcon('images/new_chat.png')
        exit_icon = QIcon('images/exit.png')
        menu_icon = QIcon('images/menu.png')

        new_chat_action = QAction(new_chat_icon, '&New chat', self)
        auth_chat_action = QAction(new_chat_icon, '&Authenticate chat', self)
        exit_action = QAction(exit_icon, '&Exit', self)

        new_chat_action.triggered.connect(self.open_tab)
        auth_chat_action.triggered.connect(self._show_auth_dialog)
        exit_action.triggered.connect(self.close)

        new_chat_action.setShortcut('Ctrl+N')
        exit_action.setShortcut('Ctrl+Q')

        options_menu = QMenu()
        options_menu.addAction(new_chat_action)
        options_menu.addAction(auth_chat_action)
        options_menu.addAction(exit_action)

        options_menu_button = QToolButton()
        new_chat_button = QToolButton()
        exit_button = QToolButton()

        new_chat_button.clicked.connect(self.open_tab)
        exit_button.clicked.connect(self.close)

        options_menu_button.setIcon(menu_icon)
        new_chat_button.setIcon(new_chat_icon)
        exit_button.setIcon(exit_icon)

        options_menu_button.setMenu(options_menu)
        options_menu_button.setPopupMode(QToolButton.InstantPopup)

        toolbar = QToolBar(self)
        toolbar.addWidget(options_menu_button)
        toolbar.addWidget(new_chat_button)
        toolbar.addWidget(exit_button)

        self.addToolBar(Qt.LeftToolBarArea, toolbar)

        # window setup
        self.setWindowIcon(QIcon('images/icon.png'))

        vbox = QVBoxLayout()
        vbox.addWidget(self.widget_stack)

        _cw = QWidget()
        _cw.setLayout(vbox)
        self.setCentralWidget(_cw)

        utils.resize_window(self, 700, 400)
        utils.center_window(self)

    def open_tab(self, member_names = None):
        tab = widgets.ChatTab(self, member_names)

        if member_names:
            title = utils.oxford_comma(member_names)
        else:
            title = constants.BLANK_TAB_TITLE

        self.chat_tabs.addTab(tab, title)
        index = self.chat_tabs.indexOf(tab)
        self.chat_tabs.setTabText(index, title)
        tab.widget_stack.currentWidget().title = title

        self.chat_tabs.setCurrentWidget(tab)
        tab.setFocus()
        return tab

    def close_tab(self, index):
        tab = self.chat_tabs.widget(index)
        tab.stop()

        self.chat_tabs.removeTab(index)

        if not self.chat_tabs.count():
            self.open_tab()

    def _tab_changed(self):
        pass

    def _show_auth_dialog(self):
        pass
