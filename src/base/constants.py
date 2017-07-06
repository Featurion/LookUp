import os
import yaml

config = os.getcwd() + '/config/config.yml'

with open(config, "r") as f:
    settings = yaml.load(f)

APP_TITLE = settings['app-name']
BASE_PATH = os.getcwd()
LOG_PATH = BASE_PATH + settings['log-path']

DEFAULT_ADDRESS = settings['default-address']
DEFAULT_PORT = settings['default-port']
MAX_PORT_SIZE = 16 # no port larger than 2 bytes (0 <= n <= 65535)
PROTOCOL_VERSION = settings['version']
MAX_NAME_LENGTH = 32

TLS_ENABLED = settings['tls-enabled']
SOCKET_TIMEOUT = 1
DISCONNECT_DELAY = 2 # give threads time to wrap up
ACCEPTED = b'accepted'
BANNED = b'banned'

WANT_BLANK_GROUPS = settings['want-blank-groups']

# GUI

BUTTON_OKAY = 0
BUTTON_CANCEL = 1
BUTTON_FORGOT = 2

# Logging

DEBUG = 10
INFO = 20
WARNING = 30
EXCEPTION = 40

LOG_CONFIG = (None, None, INFO)
WANT_LOG_FORMATTING = settings.get('want-log-formatting', False)
LOG_FORMAT = settings.get('log-format', None)
LOG_LEVEL = INFO

MsgLevel2Name = {
    DEBUG: 'DEBUG',
    INFO: 'INFO',
    WARNING: 'WARNING',
    EXCEPTION: 'ERROR',
}

# Crypto

HMAC_KEY = bytes.fromhex(settings['hmac-key'])
CHALLENGE_PASSWORD = bytes.fromhex(settings['challenge-password'])

# Commands

CMD_ERR = 0
CMD_RESP = 1
CMD_RESP_OK = 2
CMD_RESP_NO = 3
CMD_REQ_CONNECTION = 4
CMD_REQ_LOGIN = 5
CMD_REQ_CHALLENGE = 6
CMD_REQ_CHALLENGE_VERIFY = 7
CMD_HELO = 8
CMD_REDY = 9
CMD_ZONE_MSG = 10
CMD_ZONE_ADD = 11
CMD_TYPING = 12
CMD_MSG = 13
CMD_SMP_0 = 14
CMD_SMP_1 = 15
CMD_SMP_2 = 16
CMD_SMP_3 = 17
CMD_SMP_4 = 18

# Users

SYSTEM = 0
USER_ADMIN = 1
USER_TEMP = 2
USER_LITE = 3
USER_PAID = 4

SENDER = 1
RECEIVER = 2

VALID_NAME = 0
INVALID_EMPTY_NAME = 1
INVALID_NAME_CONTENT = 2
INVALID_NAME_LENGTH = 3
SMP_CHECK = 16
SMP_MATCH = 17

TITLE_INVALID_NAME = 'Invalid username'
TITLE_EMPTY_NAME = 'No username provided'
TITLE_SELF_CONNECT = 'Tried connecting to self'
TITLE_NAME_IN_USE = 'Username is taken'
TITLE_NAME_DOESNT_EXIST = "Username doesn't exist"
TITLE_BANNED = "You have been banned"
TITLE_INVALID_COMMAND = "Received invalid command"
TITLE_SMP_MATCH_FAILED = "Eavesdropping detected"
TITLE_PROTOCOL_ERROR = "Invalid response"

CHOOSE = 'Please choose another'
EMPTY_NAME = 'Please enter a username.'
NAME_LENGTH = 'That username is too long. {0}.'.format(CHOOSE)
NAME_CONTENT = 'That username contains invalid characters. {0}.'.format(CHOOSE)
SELF_CONNECT = 'You cannot connect to yourself. {0} username.'.format(CHOOSE)
NAME_IN_USE = 'That username is taken. {0}.'.format(CHOOSE)
NAME_DOESNT_EXIST = "That username does not exist."
CLIENT_JOINED = '{0} is ready to chat.'
CLIENT_BANNED = 'You have been IP banned.'
SMP_MATCH_FAILED = "Chat authentication failed. Either your buddy provided the wrong answer to the question or someone may be attempting to eavesdrop on your conversation. Note that answers are case sensitive."
SMP_MATCH_FAILED_SHORT = "Chat authentication failed. Note that answers are case sensitive."
INVALID_COMMAND = 'A client has sent you an invalid command.'

# Chatting

URL_REGEX = r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?]))"
MSG_TEMPLATE = "<font color='{0}'>{1} <strong>{2}:</strong></font> {3}"
BLANK_TAB_TITLE = 'New Chat'
BLANK_GROUP_TAB_TITLE = 'New Group Chat'

TYPING_TIMEOUT = 1500
TYPING_START = 0
TYPING_STOP = 1
TYPING_STOP_WITH_TEXT = 2
TYPING_DELETE_TEXT = 3

# SMP

SMP_CALLBACK_REQUEST = 0
SMP_CALLBACK_COMPLETE = 1
SMP_CALLBACK_ERROR = 2
