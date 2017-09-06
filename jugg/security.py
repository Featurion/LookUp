import base64
import hashlib
import hmac
import random

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.number import long_to_bytes

from . import core


_DEF_P = int(
    '6741187748806620932576983646169579908388179173131896217634330086718213'
    '7196897524293100294385477509911251666985176430415411153583804934148112'
    '2270719203394689775275781619712787479926285627950841056894489914560578'
    '6644777704963171436690681451747767610668623662035091547675844577581284'
    '1107116099737332586447792783379920367661156585471296521174976519909711'
    '4053655493786697005150045341870428321756137613385997090886777268555313'
    '7414611143572205433662323266534295986300670493366452353956774419991946'
    '7120778376342973332729789484834427321305641994642429484887054720652378'
    '7143281611104732150605474884416750181204426751173773061831004280249984'
    '0515160495726996646570665581919782210861089443979066756563614980581896'
    '3647477490973785554423411033175221560647410381701525997354437960124876'
    '6355850848264286976617275698214554930850304944031744000262468873161694'
    '1403032728660983155586725969741246309018148831176048722092207759408047'
    '8277337764758577216471860266408165536226629039774758856734871478477888'
    '0460652370770255115242696211550472734853492720444777033094043832156353'
    '9899474371867589569522488773142013721743597372132076054869435258047774'
    '9466039212874034254763903083243504140048745275480322645573043647036118'
    '6034739679137202157599997031290815163983987')


def secure_string_comparison(lstring, rstring):
    if len(lstring) != len(rstring):
        return False
    else:
        for lchar, rchar in zip(lstring, rstring):
            if lchar != rchar:
                return False
        else:
            return True


class KeyHandler(object):

    def __init__(self):
        object.__init__(self)

        self.__private_key = random.randint(1, _DEF_P - 1)
        self.__public_key = pow(2, self.__private_key, _DEF_P)

        self.__counter_key = None
        self.__counter_cipher = None

    @property
    def key(self) -> int:
        return self.__public_key

    @property
    def counter_key(self) -> int:
        return self.__counter_key

    @counter_key.setter
    def counter_key(self, key : int):
        if self.__counter_key is None:
            self.__counter_key = int(key)
        else:
            raise AttributeError('counter_key can only be set once')

    @property
    def cipher(self):
        if self.__counter_key:
            hash_ = self.generate_SHA256(long_to_bytes(pow(
                self.__counter_key,
                self.__private_key,
                _DEF_P)))
            return self.generate_AES256(hash_[0:32], hash_[16:32])
        else:
            return None

    @property
    def counter_cipher(self):
        if self.__counter_cipher:
            hash_ = self.generate_SHA256(self.__counter_cipher)
            return self.generate_AES256(hash_[0:32], hash_[16:32])
        else:
            return None

    @counter_cipher.setter
    def counter_cipher(self, bytes_ : bytes):
        if self.__counter_cipher is None:
            self.__counter_cipher = bytes_
        else:
            raise AttributeError('counter_cipher can only be set once')

    def generate_AES256(self, key, iv):
        return AES.new(key, AES.MODE_CBC, iv)

    def generate_SHA256(self, bytes_ : bytes):
        return SHA256.new(bytes_).digest()

    def generate_HMAC(self, message, key = None):
        if key is None:
            key = self.__aes_key

        return hmac.new(
            key,
            msg = str(message).encode(),
            digestmod = hashlib.sha512).digest()

    def verify_HMAC(self, hmac, data, key = None):
        if key is None:
            gen_hmac = self.generate_HMAC(data)
        else:
            gen_hmac = self.generate_HMAC(data, key)

        return secure_string_comparison(gen_hmac, base64.b85decode(hmac))

    def encrypt(self, data: str) -> bytes:
        if self.cipher:
            # Encode the data
            data = base64.b85encode(str(data).encode())
            # Pad the data
            size = AES.block_size - len(data) % AES.block_size
            data += bytes([size]) * size
            # Encrypt the data
            data = self.cipher.encrypt(data)
            # Encrypt with alternate cipher
            if self.counter_cipher:
                self.counter_cipher.encrypt(data)
            return data
        else:
            return data.encode()

    def decrypt(self, data: bytes) -> str:
        if self.cipher:
            # Decrypt with alternate cipher
            if self.counter_cipher:
                self.counter_cipher.decrypt(data)
            # Decrypt the data
            data = self.cipher.decrypt(data)
            # Unpad the data
            data = data[:-data[-1]]
            # Decode the data
            data = base64.b85decode(data).decode()
            # Make a Datagram
            return core.Datagram.from_string(data)
        else:
            return data.decode()


__all__ = [
    secure_string_comparison,
    KeyHandler,
]
