import base64

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import randint
from Crypto.Util.number import long_to_bytes


DEF_P = int('0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67'
            'CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF2'
            '5F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6'
            'F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007C'
            'B8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62'
            'F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32'
            '905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9'
            'DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AAAC4'
            '2DAD33170D04507A33A85521ABDF1CBA64ECFB850458DBEF0A8AEA71575D06'
            '0C7DB3970F85A6E1E4C7ABF5AE8CDB0933D71E8C94E04A25619DCEE3D2261A'
            'D2EE6BF12FFA06D98A0864D87602733EC86A64521F2B18177B200CBBE11757'
            '7A615D6C770988C0BAD946E208E24FA074E5AB3143DB5BFCE0FD108E4B82D1'
            '20A92108011A723C12A787E6D788719A10BDBA5B2699C327186AF4E23C1A94'
            '6834B6150BDA2583E9CA2AD44CE8DBBBC2DB04DE8EF92E8EFC141FBECAA628'
            '7C59474E6BC05D99B2964FA090C3A2233BA186515BE7ED1F612970CEE2D7AF'
            'B81BDD762170481CD0069127D5B05AA993B4EA988D8FDDC186FFB7DC90A6C0'
            '8F4DF435C93402849236C3FAB4D27C7026C1D4DCB2602646DEC9751E763DBA'
            '37BDF8FF9406AD9E530EE5DB382F413001AEB06A53ED9027D831179727B086'
            '5A8918DA3EDBEBCF9B14ED44CE6CBACED4BB1BDB7F1447E6CC254B33205151'
            '2BD7AF426FB8F401378CD2BF5983CA01C64B92ECF032EA15D1721D03F482D7'
            'CE6E74FEF6D55E702F46980C82B5A84031900B1C9E59E7C97FBEC7E8F323A9'
            '7A7E36CC88BE0F1D45B7FF585AC54BD407B22B4154AACC8F6D7EBF48E1D814'
            'CC5ED20F8037E0A79715EEF29BE32806A1D58BB7C5DA76F550AA3D8A1FBFF0'
            'EB19CCB1A313D55CDA56C9EC2EF29632387FE8D76E3C0468043E8F663F4860'
            'EE12BF2D5B0B7474D6E694F91E6DCC4024FFFFFFFFFFFFFFFF', 0)


class KeyHandler(object):

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
        self.aes_mode = AES.MODE_CBC
        self.aes_key = None
        self.aes_iv = None
        self.__pub_key = None
        self.__priv_key = None
        self.generateKey()

    def getKey(self):
        if self.__pub_key is None:
            self.generateKey()
        return self.__pub_key

    def generateKey(self):
        if self.__pub_key:
            # err: 'suspicious attempt to generate key'
            pass
        else:
            if not self.__priv_key:
                self.__priv_key = randint(1, DEF_P - 1)
                # log: DEBUG, 'generated private key'
            else:
                # err: 'private key exists'
                return
            self.__pub_key = pow(2, self.__priv_key, DEF_P)
            # log: DEBUG, generated public key

    def generateSecret(self, key):
        if self.__priv_key:
            # log: DEBUG, 'generating secret'
            self.dh_secret = long_to_bytes(pow(key, self.__priv_key, DEF_P))
            hash_ = self.generateHash(str(self.dh_secret).encode())
            self.aes_key = hash_[0:32]
            self.aes_iv = hash_[16:32]
        else:
            # err: 'no private key exists'
            return

    def generateCipher(self):
        return AES.new(self.aes_key, self.aes_mode, self.aes_iv)

    def generateHmac(self, data):
        return HMAC.HMAC(self.aes_key, data).digest()

    def generateHash(self, data):
        return SHA256.new(data).digest()

    def encrypt(self, data: str):
        try:
            data = base64.b85encode(data.encode())
            data = KeyHandler._pad(data, AES.block_size)
            data = self.generateCipher().encrypt(data)
            return data
        except:
            # err: 'error encrypting data'
            pass

    def decrypt(self, data: bytes):
        try:
            data = self.generateCipher().decrypt(data)
            data = KeyHandler._unpad(data)
            data = base64.b85decode(data).decode()
            return data
        except Exception as e:
            # err: 'error decrypting data'
            pass
