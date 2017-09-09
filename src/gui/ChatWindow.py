from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QStackedWidget
from PyQt5.QtWidgets import QTabWidget, QMenu, QAction
from PyQt5.QtWidgets import QToolButton, QTabWidget, QMenu
from PyQt5.QtWidgets import QToolBar, QVBoxLayout, QWidget

from src.base import constants, settings
from src.gui import utils

from src.gui.ChatTab import ChatTab
from src.gui.misc.Connecting import Connecting

class ChatWindow(QMainWindow):

    new_zone_signal = pyqtSignal(str)

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
            shortcut = 'Ctrl+Q', statusTip = 'Exit',
            triggered = self.close)
        _stop.setIcon(QIcon('images/exit.png'))
        self.tray_menu.addAction(_stop)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.setVisible(True)

        # widget setup
        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(Connecting(self))

        self.chat_tabs = QTabWidget(self)
        self.chat_tabs.setTabsClosable(True)
        self.chat_tabs.setMovable(True)
        self.chat_tabs.tabCloseRequested.connect(self.closeTab)
        self.chat_tabs.currentChanged.connect(self._tabChanged)
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

        new_chat_action.triggered.connect(self.openTab)
        auth_chat_action.triggered.connect(self._showAuthDialog)
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

        new_chat_button.clicked.connect(self.openTab)
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

        utils.resizeWindow(self, 700, 400)
        utils.centerWindow(self)

    @pyqtSlot(str)
    def newZone(self, id_):
        tab = self.open_tab()
        client = self._interface._client

        zone = client.LookUpZone(tab, client, id_)
        client._zones.add(zone)

    def openTab(self, member_names = None):
        tab = ChatTab(self, member_names)

        if member_names:
            title = utils.oxford_comma(member_names)
        else:
            title = constants.BLANK_TAB_TITLE

        self.chat_tabs.addTab(tab, title)
        tab._updateTitle(title)

        self.chat_tabs.setCurrentWidget(tab)
        tab.setFocus()
        return tab

    def closeTab(self, index):
        tab = self.chat_tabs.widget(index)
        tab.stop()

        self.chat_tabs.removeTab(index)

        if not self.chat_tabs.count():
            self.open_tab()

    def _tabChanged(self):
        pass

    def _showAuthDialog(self):
        pass
