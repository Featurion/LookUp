import os
from Crypto import Random
from Crypto.Hash import *
from Crypto.Cipher import AES
from src.crypto import dh


class CryptoUtils(object):

    def __init__(self):
        self.aes_key = None
        self.aes_iv = None
        self.aes_salt = None
        self.dh = None
        self.aes_mode = AES.MODE_CBC

    def getRandomBytes(self, n_bytes=128):
        return Random.get_random_bytes(192)

    def generateDHKey(self):
        self.dh = dh.DiffieHellman()
        self.dh.generateKeys()

    def computeDHSecret(self, public_key):
        self.dh_secret = self.dh.computeKey(public_key)
        new_hash = self.generateHash(str(self.dh_secret).encode())
        self.aes_key = new_hash[0:32]
        self.aes_iv = new_hash[16:32]

    def aesEncrypt(self, message):
        raw = self._pad(message, AES.block_size)
        cipher = self.__aesGetCipher()
        enc_msg = cipher.encrypt(raw)
        return enc_msg

    def aesDecrypt(self, message):
        cipher = self.__aesGetCipher()
        dec_msg = self._unpad(cipher.decrypt(message))
        return dec_msg

    def __aesGetCipher(self):
        return AES.new(self.aes_key, self.aes_mode, self.aes_iv)

    def generateHmac(self, message):
        hmac = HMAC.HMAC(self.aes_key, message).digest()
        return hmac

    def generateHash(self, message):
        if hasattr(message, "encode"):
            message = message.encode()
        new_hash = SHA256.new(message).digest()
        return new_hash

    def stringHash(self, message):
        digest = self.generateHash(message)
        hex_val = hex(self.__octx_to_num(digest))[2:-1].upper()
        return hex_val

    def mapStringToInt(self, string):
        num = shift = 0
        for char in reversed(string):
            num |= ord(char) << shift
            shift += 8
        return num

    def __octx_to_num(self, data):
        converted = 0
        length = len(data)
        for i in range(length):
            converted = converted + data[i] * (256 ** (length - i - 1))
        return converted

    def getDHPubKey(self):
        return self.dh.pub_key

    def _pad(self, msg, bs):
        if hasattr(msg, "encode"):
            msg = msg.encode()
        return msg + (bs - len(msg) % bs) * bytes([bs - len(msg) % bs])

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


def binToDec(binval):
    import binascii
    return int(binascii.hexlify(binval), 16)
