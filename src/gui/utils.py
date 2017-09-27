import os
import sys

from PyQt5.QtWidgets import QDesktopWidget


def center_window(window):
    geo = window.frameGeometry()
    geo.moveCenter(QDesktopWidget().availableGeometry().center())
    window.move(geo.topLeft())


def resize_window(window, width, height):
    window.setGeometry(0, 0, width, height)


def oxford_comma(iterable_of_strings: list):
    lst = list(iterable_of_strings)
    len_ = len(lst)

    if len_ == 0:
        return ''
    elif len_ == 1:
        return lst[0]
    elif len_ == 2:
        return ' and '.join(lst)
    else:
        str_ = ', '.join(lst[:-1] + [''])
        str_ += 'and ' + lst[-1]
        return str_
