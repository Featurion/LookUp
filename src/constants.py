from jugg.constants import *


# System
MAX_NAME_LENGTH = 32

# Commands
CMD_HELLO = 3
CMD_READY = 4
CMD_LEAVE = 5
CMD_UPDATE = 6

CMD_MSG = 7
CMD_MSG_DEL = 8
CMD_MSG_EDIT = 9
CMD_MSG_TYPING = 10

ZONE_CMDS = [
    CMD_MSG,
    CMD_MSG_DEL,
    CMD_MSG_TYPING,
]

CMD_2_NAME.update({
    CMD_HELLO: 'hello',
    CMD_READY: 'ready',
    CMD_LEAVE: 'leave',
    CMD_UPDATE: 'update',
    # Zone commands
    CMD_MSG: 'message',
    CMD_MSG_DEL: 'message_delete',
    CMD_MSG_EDIT: 'message_edit',
    CMD_MSG_TYPING: 'message_typing',
})

# Users
ERR_BANNED = 5
ERR_KICKED = 6
ERR_SMP = 7

ERROR_INFO_MAP.update({
    ERR_BANNED: 'banned',
    ERR_KICKED: 'kicked',
    ERR_SMP: 'failed smp',
})

# GUI
BLANK_TAB_TITLE = 'New Chat'
MSG_DELETED_TEXT = '<font color="#BBBBBB">&lt;deleted&gt;</font>'

TYPING_TIMEOUT = 10

URL_REGEX = r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?]))"
