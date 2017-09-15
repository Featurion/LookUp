from jugg.constants import *


# System
MAX_NAME_LENGTH = 32

# Commands
CMD_HELLO = 3
CMD_READY = 4
CMD_LEAVE = 5
CMD_MSG = 6
CMD_UPDATE = 7

# Users
ERR_BANNED = 5
ERR_KICKED = 6
ERR_SMP = 7

ERROR_CODES.update({
    ERR_BANNED,
    ERR_KICKED,
    ERR_SMP,
})

ERROR_INFO_MAP.update({
    ERR_BANNED: 'banned',
    ERR_KICKED: 'kicked',
    ERR_SMP: 'failed smp',
})

# GUI
BLANK_TAB_TITLE = 'New Chat'

# Chatting
URL_REGEX = r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?]))"

TYPING_TIMEOUT = 1500
TYPING_START = 0
TYPING_STOP = 1
TYPING_STOP_WITH_TEXT = 2
TYPING_DELETE_TEXT = 3
