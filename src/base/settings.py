import os
import yaml

CONFIG_PATH = os.getcwd() + '/config/dev.yml'

with open(CONFIG_PATH, "r") as config:
    settings = yaml.load(config)

APP_NAME = settings['app-name']
VERSION = settings['version']

HOST = settings['host']
PORT = settings['port']
WANT_TLS = settings['want-tls']
KEY_PATH = settings['key-path']
CERT_PATH = settings['cert-path']

HMAC_KEY = settings['hmac-key'].encode()
CHALLENGE_KEY = settings['challenge-key'].encode()

LOG_PATH = os.getcwd() + settings['log-path']

WANT_INJECTOR = settings['want-injector']
WANT_LOG_FORMATTING = settings['want-log-formatting']
LOG_FORMAT = settings['log-format']