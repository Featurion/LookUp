import os
import sys


def center_window(window):
    from PyQt5.QtWidgets import QDesktopWidget

    geo = window.frameGeometry()
    geo.moveCenter(QDesktopWidget().availableGeometry().center())
    window.move(geo.topLeft())


def resize_window(window, width, height):
    window.setGeometry(0, 0, width, height)
