from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMainWindow, QMenu, QSystemTrayIcon
from PyQt5.QtWidgets import QStackedWidget, QTabWidget, QToolButton, QToolBar
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from src import constants, settings
from src.gui import utils
from src.gui.widgets.ChatTabWidget import ChatTabWidget
from src.gui.widgets.ConnectingWidget import ConnectingWidget


class ChatWindow(QMainWindow):

    def __init__(self, interface):
        super().__init__()

        self.interface = interface

        # window setup
        self.status_bar = self.statusBar()

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('images/icon.ico'))
        self.tray_icon.setToolTip(settings.APP_NAME)

        self.tray_menu = QMenu()
        _stop = QAction(
            'Exit', self,
            shortcut='Ctrl+Q', statusTip='Exit',
            triggered=self.close)
        _stop.setIcon(QIcon('images/exit.png'))
        self.tray_menu.addAction(_stop)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.setVisible(True)

        # widget setup
        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(ConnectingWidget(self))

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
        exit_button.clicked.connect(self.interface.stop)

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

    def open_tab(self, zone=None):
        tab = ChatTabWidget(self)
        tab._zone = zone

        self.chat_tabs.addTab(tab, constants.BLANK_TAB_TITLE)
        self.chat_tabs.setCurrentWidget(tab)

        tab.setFocus()
        return tab

    def close_tab(self, index):
        tab = self.chat_tabs.widget(index)

        if tab._zone:
            conn.synchronous_send(
                command = constants.CMD_LEAVE,
                recipient = tab._zone.id)
            conn._zones.remove(tab._zone)
        else:
            # Can't leave nonexistent zone
            pass

        self.chat_tabs.removeTab(index)

    def _tab_changed(self):
        self.status_bar.showMessage('')

    def _show_auth_dialog(self):
        pass
