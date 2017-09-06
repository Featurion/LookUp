# System
NAME_REGEX = r'\w{1,32}'

# Commands
CMD_ERR = 0
CMD_RESP = 1
CMD_LOGIN = 2

# Error codes
ERR_DISCONNECT = 0
ERR_CREDENTIALS = 1
ERR_HMAC = 2
ERR_CHALLENGE = 3
ERR_VERIFICATION = 4

ERROR_CODES = {
    ERR_DISCONNECT,
    ERR_CREDENTIALS,
    ERR_HMAC,
    ERR_CHALLENGE,
    ERR_VERIFICATION,
}

ERROR_INFO_MAP = {
    ERR_DISCONNECT: 'disconnected by server',
    ERR_CREDENTIALS: 'invalid credentials',
    ERR_HMAC: 'invalid hmac',
    ERR_CHALLENGE: 'failed challenge',
    ERR_VERIFICATION: 'failed verification',
}


__all__ = [
    # System
    NAME_REGEX,
    # Commands
    CMD_ERR, CMD_RESP, CMD_LOGIN,
    # Error codes
    ERR_DISCONNECT, ERR_CREDENTIALS, ERR_HMAC, ERR_CHALLENGE, ERR_VERIFICATION,
    ERROR_CODES, ERROR_INFO_MAP,
]
