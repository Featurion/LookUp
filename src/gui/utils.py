import os
import sys

from PyQt5.QtWidgets import QDesktopWidget

def centerWindow(window):
    geo = window.frameGeometry()
    geo.moveCenter(QDesktopWidget().availableGeometry().center())
    window.move(geo.topLeft())

def resizeWindow(window, width, height):
    window.setGeometry(0, 0, width, height)

def oxford_comma(strings : list):
    len_ = len(strings)

    if len_ == 0:
        return ''
    elif len_ == 1:
        return strings[0]
    elif len_ == 2:
        return ' and '.join(strings)
    else:
        str_ = ', '.join(strings[:-1] + [''])
        str_ += 'and ' + strings[-1]
        return str_
