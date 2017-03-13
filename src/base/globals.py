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
INVALID_NAME_EMPTY = 1
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

RELAY_COMMANDS = [
    COMMAND_VERSION,
    COMMAND_REGISTER,
    COMMAND_REQ_ID,
    COMMAND_REQ_NAME,
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

DEBUG_END = 'ended connection to {0}'
DEBUG_END_REQ = '{0} requested to end session'
DEBUG_SYNC_WAIT = 'polling for response'
DEBUG_SYNC_DONE = 'received response'
DEBUG_SERVER_COMMAND = 'sending server command: {0}'
DEBUG_CLIENT_START = 'starting client'
DEBUG_CLIENT_CONNECTED = 'connected to server'
DEBUG_CLIENT_DISCONNECTED = 'disconnected from server'
DEBUG_SERVER_START = 'starting server'
DEBUG_CONN_CLOSED = 'connection unavailable'
DEBUG_RECV_CONN = 'got connection from {0}:{1}'
DEBUG_SEND_STOP = 'stopped sending messages'
DEBUG_RECV_STOP = 'stopped receiving messages'
DEBUG_RECV_PROTOCOL_VERION = 'received correct protocol version'
DEBUG_REGISTERED = 'client registered: {0}, {1}'
DEBUG_UNREGISTERED = 'client unregistered: {0}, {1}'
DEBUG_SERVER_STOP = 'stopping server'
DEBUG_DISCONNECT_WAIT = 'waiting for clean disconnect'

ERR_INVALID_ADDR = 'received invalid address: {0}'
ERR_INVALID_PORT = 'received invalid port: {0}'
ERR_INVALID_SEND = 'tried sending invalid message to id: {0}'
ERR_INVALID_RECV = 'received invalid message from id: {0}'
ERR_INVALID_COMMAND = 'received message with invalid command from id: {0}'
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

EMPTY_NAME = 'Please enter a nickname'

# Exceptions

class GenericError(Exception):

    def __init__(self, err=0, msg=None):
        Exception.__init__(self)
        self.err = err
        self.msg = msg


class NetworkError(GenericError):
    pass
