import base64

import hmac
import hashlib

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random.random import randint
from Crypto.Util.number import long_to_bytes
from src.base.Notifier import Notifier

DEF_P = 0x00a53d56c30fe79d43e3c9a0b678e87c0fcd2e78b15c676838d2a2bd6c299b1e7fdb286d991f62e8f366b0067ae71d3d91dac4738fd744ee180b16c97a54215236d4d393a4c85d8b390783566c1b0d55421a89fca20b85e0faecded7983d038821778b6504105f455d8655953d0b62841e9cc1248fa21834bc9f3e3cc1c080cfcb0b230fd9a2059f5f637395dfa701981fad0dbeb545e2e29cd20f7b6baee9314039e16ef19f604746fe596d50bb3967da51b948184d8d4511f2c0b8e4b4e3abc44144ce1f5968aadd053600a40430ba97ad9e0ad26fe4c444be3f48434a68aa132b1677d8442454fe4c6ae9d3b7164e6603f1c8a8f5b5235ba0b9f5b5f86278e4f69eb4d5388838ef15678535589516a1d85d127da8f46f150613c8a49258be2ed53c3e161d0049cabb40d15f9042a00c494746753b9794a9f66a93b67498c7c59b8253a910457c10353fa8e2edcafdf6c9354a3dc58b5a825c353302d686596c11e4855e86f3c6810f9a4abf917f69a6083330492aedb5621ebc3fd59778a40e0a7fa8450c8b2c6fe3923775419b2ea35cd19abe62c50020df991d9fc772d16dd5208468dc7a9b51c6723495fe0e72e818ee2b2a8581fab2caf6bd914e4876573b023862286ec88a698be2dd34c03925ab5ca0f50f0b2a246ab852e3779f0cf9d3e36f9ab9a50602d5e9216c3a29994e81e151accd88ea346d1be6588068e873

class KeyHandler(Notifier):

    @staticmethod
    def _pad(bytes_, bs):
        return bytes_ + (bs - len(bytes_) % bs) * bytes([bs - len(bytes_) % bs])

    @staticmethod
    def _unpad(str_):
        return str_[:-ord(str_[len(str_)-1:])]

    @staticmethod
    def hashToString(hash_):
        return hex(KeyHandler.octxToNum(hash_))[2:-1].upper()

    @staticmethod
    def octxToNum(data):
        converted, length = 0, len(data)
        for i in range(length):
            converted += data[i] * (256 ** (length - i - 1))
        return converted

    @staticmethod
    def mapStringToInt(str_):
        num = shift = 0
        for char in reversed(str_):
            num |= ord(char) << shift
            shift += 8
        return num

    def __init__(self):
        Notifier.__init__(self)
        self.__aes_mode = AES.MODE_CBC
        self.__aes_key = None
        self.__aes_iv = None
        self.__pub_key = None
        self.__priv_key = None
        self.generateKey()

    def getKey(self):
        if self.__pub_key is None:
            self.generateKey()
        return self.__pub_key

    def generateKey(self):
        if len(str(DEF_P)) < 1028:
            self.notify.critical('suspicious attempt to generate keys')
            return
        if self.__pub_key:
            self.notify.critical('suspicious attempt to generate public key')
            return
        else:
            if not self.__priv_key:
                self.__priv_key = randint(1, DEF_P - 1)
                self.notify.debug('generated private key')
            else:
                self.notify.critical('suspicious attempt to generate private key')
                return
            self.__pub_key = pow(2, self.__priv_key, DEF_P)
            self.notify.debug('generated keys')

    def generateSecret(self, key):
        if self.__priv_key:
            self.notify.debug('generating DH secret')
            self.__dh_secret = long_to_bytes(pow(key, self.__priv_key, DEF_P))
            hash_ = self.generateHash(str(self.__dh_secret).encode())
            self.__aes_key = hash_[0:32]
            self.__aes_iv = hash_[16:32]
        else:
            self.notify.error('CryptoError', 'no private key exists')
            return

    def __generateCipher(self):
        return AES.new(self.__aes_key, self.__aes_mode, self.__aes_iv)

    def generateHmac(self, message, key, hex_digest=False):
        if not hex_digest:
            return hmac.new(key, msg=message, digestmod=hashlib.sha512).digest()
        else:
            return hmac.new(key, msg=message, digestmod=hashlib.sha512).hexdigest()

    def generateHash(self, data):
        return SHA256.new(data).digest()

    def encrypt(self, data: str):
        try:
            data = base64.b85encode(data.encode())
            data = KeyHandler._pad(data, AES.block_size)
            data = self.__generateCipher().encrypt(data)
            return data
        except Exception as e:
            self.notify.error('CryptoError', 'error encrypting data')

    def decrypt(self, data: bytes):
        try:
            data = self.__generateCipher().decrypt(data)
            data = KeyHandler._unpad(data)
            data = base64.b85decode(data).decode()
            return data
        except Exception as e:
            self.notify.error('CryptoError', 'error decrypting data')
