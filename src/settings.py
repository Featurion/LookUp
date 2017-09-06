import os
import yaml


MAIN_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = 'config/dev.yml'

APP_TITLE = 'LookUp'
VERSION = ''

HOST = '127.0.0.1'
PORT = 1492
WANT_TLS = False
KEY_PATH = ''
CERT_PATH = ''

HMAC_KEY = ''
CHALLENGE_KEY = ''

LOG_PATH = 'logs'


if CONFIG_PATH:
    with open(os.path.join(MAIN_DIR, CONFIG_PATH), 'r') as config:
        data = yaml.load(config)
        for key, value in data.items():
            globals()[key.upper()] = value


HMAC_KEY = HMAC_KEY.encode()
CHALLENGE_KEY = CHALLENGE_KEY.encode()


__all__ = [
    APP_TITLE,
    VERSION,

    HOST,
    PORT,
    WANT_TLS,
    KEY_PATH,
    CERT_PATH,

    HMAC_KEY,
    CHALLENGE_KEY,

    LOG_PATH,
]
