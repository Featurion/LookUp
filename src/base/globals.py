import os


BASE_PATH = os.getcwd()
LOG_PATH = BASE_PATH + '/logs'
DEFAULT_ADDR = '127.0.0.1'
DEFAULT_PORT = 1492
MAX_PORT_SIZE = 16 # no port larger than 2 bytes (0 <= n <= 65535)
PROTOCOL_VERSION = 'v1.0.0'
SERVER_ID = 'server'
MAX_NAME_LENGTH = 32

# User modes

USER_ADMIN = 0
USER_STANDARD = 1

# Name codes

VALID_NAME = 0
INVALID_EMPTY_NAME = 1
INVALID_NAME_CONTENT = 2
INVALID_NAME_LENGTH = 3

# Commands

COMMAND_END = 0
COMMAND_VERSION = 1
COMMAND_REGISTER = 2
COMMAND_REQ_ID = 3
COMMAND_REQ_NAME = 4
COMMAND_RELAY = 5
COMMAND_ERR = 6
COMMAND_REQ_SESSION = 7
COMMAND_HELO = 8
COMMAND_REDY = 9
COMMAND_REJECT = 10
COMMAND_PUBKEY = 11

RELAY_COMMANDS = [
    COMMAND_VERSION,
    COMMAND_REGISTER,
    COMMAND_REQ_ID,
    COMMAND_REQ_NAME,
    COMMAND_REQ_SESSION,
]

SESSION_COMMANDS = [
    COMMAND_HELO,
    COMMAND_REDY,
    COMMAND_REJECT,
    COMMAND_PUBKEY,
]

# Error codes

PROTOCOL_VERSION_MISMATCH = 0
MALFORMED_MESSAGE = 1
INVALID_COMMAND = 2
INVALID_ID = 3
CONN_CLOSED = 4
INVALID_NAME = 5
NAME_IN_USE = 6
RECV_ERROR = 7


# Notifier messages

DEBUG_END = 'ended session {0}'
DEBUG_END_REQ = '{0} requested to end session'
DEBUG_SYNC_WAIT = 'polling for response'
DEBUG_SYNC_DONE = 'received response'
DEBUG_SERVER_COMMAND = 'sending server command: {0}'
DEBUG_CLIENT_START = 'starting client'
DEBUG_CLIENT_CONNECTED = 'connected to server'
DEBUG_CLIENT_DISCONNECTED = 'disconnected from server'
DEBUG_SERVER_START = 'starting server'
DEBUG_SESSION_START = 'started session {0}'
DEBUG_SESSION_JOIN = 'joined session {0}'
DEBUG_CONN_CLOSED = 'connection unavailable'
DEBUG_RECV_CONN = 'got connection from {0}:{1}'
DEBUG_SEND_STOP = 'stopped sending messages'
DEBUG_RECV_STOP = 'stopped receiving messages'
DEBUG_RECV_PROTOCOL_VERION = 'received correct protocol version'
DEBUG_REGISTERED = 'client registered: {0}, {1}'
DEBUG_UNREGISTERED = 'client unregistered: {0}, {1}'
DEBUG_SERVER_STOP = 'stopping server'
DEBUG_DISCONNECT_WAIT = 'waiting for clean disconnect'
DEBUG_UNAVAILABLE = '{0} is unavailable'
DEBUG_CONNECTED_PRIVATE = 'already connected to {0}'
DEBUG_CONNECTED_GROUP = 'already connected to group'
DEBUG_HELO = 'received HELO from {0}'
DEBUG_REDY = 'received REDY from {0}'

ERR_NO_CONNECTION = 'could not connect to server'
ERR_INVALID_ADDR = 'received invalid address: {0}'
ERR_INVALID_PORT = 'received invalid port: {0}'
ERR_INVALID_SEND = 'tried sending invalid message to id: {0}'
ERR_INVALID_RECV = 'received invalid message from id: {0}'
ERR_INVALID_COMMAND = 'received message with invalid command from id: {0}'
ERR_INVALID_CLIENT = 'failed to get client by id: {0}'
ERR_SERVER_START = 'failed to start server'
ERR_MISSING_FIELD = 'received a command with missing field(s)'
ERR_SEND = 'error sending data with path ({0}, {1})'
ERR_RECV = 'error receiving'
ERR_EXPECTED_VERSION = 'received invalid command {0}. expected command {1}'
ERR_PROTOCOL_MISMATCH = 'received wrong protocol version'
ERR_CLIENT_UNREGISTERED = 'id {0} has not registered a name'
ERR_INVALID_NAME = 'id {0} tried to register an invalid name'
ERR_SESSION_END = 'error exiting sessions'
ERR_CONN_CLOSED = 'server closed the connection'

TITLE_INVALID_NAME = 'Invalid username'
TITLE_EMPTY_NAME = 'No username provided'
TITLE_SELF_CONNECT = 'Tried connecting to self'

EMPTY_NAME = 'Please enter a username'
NAME_LENGTH = 'Username is too long'
NAME_CONTENT = 'Username contains invalid characters'
SELF_CONNECT = "You cannot connect to yourself"

# Exceptions

class NetworkError(Exception):
    def __init__(self, err=0, msg=None):
        Exception.__init__(self)
        self.err = err
        self.msg = msg