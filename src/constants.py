from jugg.constants import *


# System
MAX_NAME_LENGTH = 32

# Commands
CMD_HELLO = 3
CMD_READY = 4

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
TITLE_INVALID_NAME = 'Invalid username'
TITLE_EMPTY_NAME = 'No username provided'
TITLE_SELF_CONNECT = 'Tried connecting to self'
TITLE_NAME_IN_USE = 'Username is taken'
TITLE_NAME_DOESNT_EXIST = "Username doesn't exist"
TITLE_CLIENT_BANNED = "You have been banned"
TITLE_CLIENT_KICKED = "You have been kicked"
TITLE_CLIENT_KILLED = "You have been killed"
TITLE_INVALID_COMMAND = "Received invalid command"
TITLE_SMP_MATCH_FAILED = "Eavesdropping detected"
TITLE_PROTOCOL_ERROR = "Invalid response"
TITLE_HMAC_ERROR = "Invalid HMAC"

CHOOSE = 'Please choose another'
EMPTY_NAME = 'Please enter a username.'
NAME_LENGTH = 'That username is too long. {0}.'.format(CHOOSE)
NAME_CONTENT = 'That username contains invalid characters. {0}.'.format(CHOOSE)
SELF_CONNECT = 'You cannot connect to yourself. {0} username.'.format(CHOOSE)
NAME_IN_USE = 'That username is taken. {0}.'.format(CHOOSE)
NAME_DOESNT_EXIST = "That username does not exist."
CLIENT_JOINED = '{0} is ready to chat.'
CLIENT_BANNED = 'You have been banned from LookUp for {0}. Should this be an improper ban, you may contact the developers.'
CLIENT_KICKED = 'You have been kicked from LookUp for {0}. Should this be an improper kick, you may contact the developers. You can also log back into LookUp.'
CLIENT_KILLED = 'Your IP address has been disconnected from LookUp for {0}. Should this be improper, you may contact the developers. You can also log back into LookUp.'
SMP_MATCH_FAILED = "Chat authentication failed. Either your buddy provided the wrong answer to the question or someone may be attempting to eavesdrop on your conversation. Note that answers are case sensitive."
SMP_MATCH_FAILED_SHORT = "Chat authentication failed. Note that answers are case sensitive."
HMAC_ERROR = "You have been sent an invalid message. There may have been tampering."
SUSPICIOUS_DATAGRAM = "You have been sent a suspicious datagram. There may have been tampering."
INVALID_COMMAND = 'A client has sent you an invalid command.'

# Chatting
URL_REGEX = r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?]))"

BLANK_TAB_TITLE = 'New Chat'
BLANK_GROUP_TAB_TITLE = 'New Group Chat'

TYPING_TIMEOUT = 1500
TYPING_START = 0
TYPING_STOP = 1
TYPING_STOP_WITH_TEXT = 2
TYPING_DELETE_TEXT = 3
