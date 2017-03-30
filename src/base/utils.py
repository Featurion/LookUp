import os
from PyQt5.QtWidgets import QDesktopWidget
from src.base.globals import INVALID_EMPTY_NAME, INVALID_NAME_CONTENT
from src.base.globals import INVALID_NAME_LENGTH, VALID_NAME, MAX_NAME_LENGTH


def isNameInvalid(name):
    if not name:
        return INVALID_EMPTY_NAME
    elif not name.isalnum():
        return INVALID_NAME_CONTENT
    elif len(name) > MAX_NAME_LENGTH:
        return INVALID_NAME_LENGTH
    else:
        return VALID_NAME


def getTimestamp():
    return time.strftime('%H:%M:%S', time.localtime())


def getResourcePath(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        try:
            base_path = os.path.dirname(sys.modules[''].__file__)
        except Exception:
            base_path = ''
        if not os.path.exists(os.path.join(base_path, relative_path)):
            base_path = ''
    path = os.path.join(base_path, relative_path)
    if not os.path.exists(path):
        return None
    else:
        return path


def secureStrCmp(left, right):
    equal = True
    if len(left) != len(right):
        equal = False
    for i in range(0, min(len(left), len(right))):
        if left[i] != right[i]:
            equal = False
    return equal


def centerWindow(window):
    centerPoint = QDesktopWidget().availableGeometry().center()
    geo = window.frameGeometry()
    geo.moveCenter(centerPoint)
    window.move(geo.topLeft())


def resizeWindow(window, width, height):
    window.setGeometry(0, 0, width, height)
