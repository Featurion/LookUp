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

# Logging
DEBUG = 10
INFO = 20
WARNING = 30
EXCEPTION = 40

LOG_CONFIG = (None, None, INFO)
LOG_FORMAT = settings['log-format']

# Crypto

HMAC_KEY = settings['hmac-key'].encode()

# Commands

CMD_ERR = 0
CMD_RESP = 1
CMD_RESP_OK = 2
CMD_RESP_NO = 3
CMD_LOGIN = 4
CMD_REQ_CHALLENGE = 5
CMD_RESP_CHALLENGE = 6
CMD_VERIFY_CHALLENGE = 7
CMD_REQ_ZONE = 8
CMD_ZONE_MSG = 9
CMD_HELO = 10
CMD_REDY = 11

# Users

SYSTEM = 0
USER_ADMIN = 1
USER_TEMP = 2
USER_LITE = 3
USER_PAID = 4

VALID_NAME = 0
INVALID_EMPTY_NAME = 1
INVALID_NAME_CONTENT = 2
INVALID_NAME_LENGTH = 3

TITLE_INVALID_NAME = 'Invalid username'
TITLE_EMPTY_NAME = 'No username provided'
TITLE_SELF_CONNECT = 'Tried connecting to self'
TITLE_NAME_IN_USE = 'Username is taken'

CHOOSE = 'Please choose another'
EMPTY_NAME = 'Please enter a username.'
NAME_LENGTH = 'That username is too long. {0}.'.format(CHOOSE)
NAME_CONTENT = 'That username contains invalid characters. {0}.'.format(CHOOSE)
SELF_CONNECT = 'You cannot connect to yourself. {0} username.'.format(CHOOSE)
NAME_IN_USE = 'That username is taken. {0}.'.format(CHOOSE)
CLIENT_JOINED = '{0} is ready to chat.'

# Chatting

URL_REGEX = r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?]))"
MSG_TEMPLATE = "<font color='{0}'>{1} <strong>{2}:</strong></font> {3}"
BLANK_TAB_TITLE = 'New Chat'
