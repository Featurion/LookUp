from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QToolButton, QToolBar
from PyQt5.QtWidgets import QVBoxLayout, QSystemTrayIcon, QTabWidget, QWidget
from PyQt5.QtWidgets import QStackedWidget

from src.base import constants, utils
from src.gui.ChatTab import ChatTab
from src.gui.ConnectionDialog import ConnectionDialog
from src.gui.ConnectingWidget import ConnectingWidget
from src.zones.Zone import Zone


class ChatWindow(QMainWindow):

    new_client_signal = pyqtSignal(str, str, list, list, bool)

    def __init__(self, interface):
        QMainWindow.__init__(self)

        self.interface = interface

        self.new_client_signal.connect(self.newClient)

        # window setup

        self.status_bar = self.statusBar()
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(utils.getResourcePath('images/icon.ico')))
        self.tray_icon.setToolTip('LookUp')

        self.tray_menu = QMenu()
        _stop = QAction('Exit', self,
                        shortcut='Ctrl+Q', statusTip='Exit',
                        triggered=self.stop)
        _stop.setIcon(QIcon(utils.getResourcePath('images/exit.png')))
        self.tray_menu.addAction(_stop)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.setVisible(True)

        # widget setup

        self.widget_stack = QStackedWidget(self)
        self.widget_stack.addWidget(ConnectingWidget(self))

        self.chat_tabs = QTabWidget(self)
        self.chat_tabs.setTabsClosable(True)
        self.chat_tabs.setMovable(True)
        self.chat_tabs.tabCloseRequested.connect(self.closeTab)
        self.chat_tabs.currentChanged.connect(self._tabChanged)
        self.widget_stack.addWidget(self.chat_tabs)

        self.widget_stack.setCurrentIndex(1)

        # menubar setup

        new_chat_icon = QIcon(utils.getResourcePath('images/new_chat.png'))
        exit_icon = QIcon(utils.getResourcePath('images/exit.png'))
        menu_icon = QIcon(utils.getResourcePath('images/menu.png'))

        new_chat_action = QAction(new_chat_icon, '&New chat', self)
        new_group_chat_action = QAction(new_chat_icon, '&New group chat', self)
        auth_chat_action = QAction(new_chat_icon, '&Authenticate chat', self)
        exit_action = QAction(exit_icon, '&Exit', self)

        new_chat_action.triggered.connect(self.openTab)
        new_group_chat_action.triggered.connect(self.createGroupTab)
        auth_chat_action.triggered.connect(self.__showAuthDialog)
        exit_action.triggered.connect(self.stop)

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

        new_chat_button.clicked.connect(self.openTab)
        new_group_chat_button.clicked.connect(self.openGroupTab)
        exit_button.clicked.connect(self.stop)

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

        # window setup

        self.setWindowIcon(QIcon(utils.getResourcePath('images/icon.png')))

        vbox = QVBoxLayout()
        vbox.addWidget(self.widget_stack)

        _cw = QWidget()
        _cw.setLayout(vbox)
        self.setCentralWidget(_cw)

        utils.resizeWindow(self, 700, 400)
        utils.centerWindow(self)

    def start(self):
        name = self.interface.getClient().getName()
        self.setWindowTitle(constants.APP_TITLE + ': ' + name)
        self.show()

    def stop(self):
        self.close()

    def setTabTitle(self, tab, title):
        index = self.chat_tabs.indexOf(tab)
        self.chat_tabs.setTabText(index, title)

    def doConnecting(self, tab, title):
        tab.widget_stack.widget(2).setConnectingToName(title)
        tab.widget_stack.setCurrentIndex(2)

    def openTab(self, title=None):
        tab = ChatTab(self.interface, False)

        if title:
            self.chat_tabs.addTab(tab, title)
            self.doConnecting(tab, title)
        else:
            self.chat_tabs.addTab(tab, constants.BLANK_TAB_TITLE)

        self.chat_tabs.setCurrentWidget(tab)
        tab.setFocus()

        return tab

    def createGroupTab(self):
        tab = self.openGroupTab(None)
        tab.connect()

    def openGroupTab(self, title=None):
        tab = ChatTab(self.interface, True)

        if title:
            self.doConnecting(tab, title)
        else:
            self.chat_tabs.addTab(tab, constants.BLANK_GROUP_TAB_TITLE)

        self.chat_tabs.setCurrentWidget(tab)
        tab.setFocus()

        return tab

    def closeTab(self, index):
        tab = self.chat_tabs.widget(index)
        tab.exit()

        self.chat_tabs.removeTab(index)

        if self.chat_tabs.count() == 0:
            self.openTab()

    def _tabChanged(self):
        pass

    def __showAuthDialog(self):
        pass

    @pyqtSlot(str, str, list, list, bool)
    def newClient(self, zone_id, key, member_ids, member_names, is_group):
        if not is_group and not self.isActiveWindow():
            utils.showDesktopNotification(self.tray_icon,
                                          'Chat request from {0}'.format(member_names[0]),
                                          '')

        if is_group:
            tab = self.openGroupTab(utils.oxfordComma(member_names))
        elif ConnectionDialog.getAnswer(self, member_names):
            tab = self.openTab(utils.oxfordComma(member_names))
        else:
            return

        zone = Zone(tab, zone_id, int(key), member_ids, is_group)
        self.interface.getClient().enter(tab, zone)
        zone.sendRedy()
