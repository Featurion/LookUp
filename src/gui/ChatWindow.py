from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QToolButton, QToolBar
from PyQt5.QtWidgets import QVBoxLayout, QSystemTrayIcon, QTabWidget, QWidget
from src.base import utils
from src.gui.ChatTab import ChatTab
from src.gui.ConnectionDialog import ConnectionDialog


class ChatWindow(QMainWindow):

    new_client_signal = pyqtSignal(str, str, list)

    def __init__(self, client):
        QMainWindow.__init__(self)
        self.client = client
        self.new_client_signal.connect(self.newClient)
        self.status_bar = self.statusBar()
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(utils.getResourcePath('images/icon.ico')))
        self.tray_icon.setToolTip('LookUp')
        self.tray_menu = QMenu()
        _exit = QAction('Exit', self,
                        shortcut='Ctrl+Q', statusTip='Exit',
                        triggered=self.exit)
        _exit.setIcon(QIcon(utils.getResourcePath('images/exit.png')))
        self.tray_menu.addAction(_exit)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.setVisible(True)
        self.chat_tabs = QTabWidget(self)
        self.chat_tabs.setTabsClosable(True)
        self.chat_tabs.setMovable(True)
        self.chat_tabs.tabCloseRequested.connect(self.closeTab)
        self.chat_tabs.currentChanged.connect(self._tabChanged)
        self.__setMenubar()
        self.setWindowTitle('LookUp')
        self.setWindowIcon(QIcon(utils.getResourcePath('images/icon.png')))
        self.build()

    def build(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.chat_tabs)
        _cw = QWidget()
        _cw.setLayout(vbox)
        self.setCentralWidget(_cw)
        utils.resizeWindow(self, 700, 400)
        utils.centerWindow(self)

    def __setMenubar(self):
        new_chat_icon = QIcon(utils.getResourcePath('images/new_chat.png'))
        exit_icon = QIcon(utils.getResourcePath('images/exit.png'))
        menu_icon = QIcon(utils.getResourcePath('images/menu.png'))

        new_chat_action = QAction(new_chat_icon, '&New chat', self)
        new_group_chat_action = QAction(new_chat_icon, '&New group chat', self)
        auth_chat_action = QAction(new_chat_icon, '&Authenticate chat', self)
        exit_action = QAction(exit_icon, '&Exit', self)

        new_chat_action.triggered.connect(self.addNewTab)
        new_group_chat_action.triggered.connect(self.addNewGroupTab)
        auth_chat_action.triggered.connect(self.__showAuthDialog)
        exit_action.triggered.connect(self.exit)

        new_chat_action.setShortcut('Ctrl+N')
        new_group_chat_action.setShortcut('Ctrl+M')
        exit_action.setShortcut('Ctrl+Q')

        options_menu = QMenu()
        options_menu.addAction(new_chat_action)
        options_menu.addAction(new_group_chat_action)
        options_menu.addAction(auth_chat_action)
        options_menu.addAction(exit_action)

        options_menu_button = QToolButton()
        new_chat_button = QToolButton()
        new_group_chat_button = QToolButton()
        exit_button = QToolButton()

        new_chat_button.clicked.connect(self.addNewTab)
        new_group_chat_button.clicked.connect(self.addNewGroupTab)
        exit_button.clicked.connect(self.exit)

        options_menu_button.setIcon(menu_icon)
        new_chat_button.setIcon(new_chat_icon)
        new_group_chat_button.setIcon(new_chat_icon)
        exit_button.setIcon(exit_icon)

        options_menu_button.setMenu(options_menu)
        options_menu_button.setPopupMode(QToolButton.InstantPopup)

        toolbar = QToolBar(self)
        toolbar.addWidget(options_menu_button)
        toolbar.addWidget(new_chat_button)
        toolbar.addWidget(new_group_chat_button)
        toolbar.addWidget(exit_button)

        self.addToolBar(Qt.LeftToolBarArea, toolbar)

    def addNewTab(self):
        _nt = ChatTab(self)
        self.chat_tabs.addTab(_nt, 'New Chat')
        self.chat_tabs.setCurrentWidget(_nt)
        _nt.setFocus()

    def addNewGroupTab(self):
        _nt = ChatTab(self)
        self.chat_tabs.addTab(_nt, "Group chat")
        self.chat_tabs.setCurrentWidget(_nt)
        _nt.setFocus()

    def closeTab(self):
        pass

    def _tabChanged(self):
        pass

    def __showAuthDialog(self):
        pass

    @pyqtSlot(str, str, list)
    def newClient(self, session_id, owner, members):
        if not self.isActiveWindow():
            utils.showDesktopNotification(self.tray_icon,
                                          'Chat request from {0}'.format(owner),
                                          '')
        resp = ConnectionDialog.getAnswer(self, owner, members[1])
        if resp:
            self.client.session_manager.joinSession(session_id,
                                                    set(members[0] + [owner]))
        else:
            pass

    def exit(self):
        self.close()
