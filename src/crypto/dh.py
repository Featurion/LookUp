from Crypto.Random.random import randint
from Crypto.Util.number import bytes_to_long, long_to_bytes

def_g = 2
def_p = 0x00a53d56c30fe79d43e3c9a0b678e87c0fcd2e78b15c676838d2a2bd6c299b1e7fdb286d991f62e8f366b0067ae71d3d91dac4738fd744ee180b16c97a54215236d4d393a4c85d8b390783566c1b0d55421a89fca20b85e0faecded7983d038821778b6504105f455d8655953d0b62841e9cc1248fa21834bc9f3e3cc1c080cfcb0b230fd9a2059f5f637395dfa701981fad0dbeb545e2e29cd20f7b6baee9314039e16ef19f604746fe596d50bb3967da51b948184d8d4511f2c0b8e4b4e3abc44144ce1f5968aadd053600a40430ba97ad9e0ad26fe4c444be3f48434a68aa132b1677d8442454fe4c6ae9d3b7164e6603f1c8a8f5b5235ba0b9f5b5f86278e4f69eb4d5388838ef15678535589516a1d85d127da8f46f150613c8a49258be2ed53c3e161d0049cabb40d15f9042a00c494746753b9794a9f66a93b67498c7c59b8253a910457c10353fa8e2edcafdf6c9354a3dc58b5a825c353302d686596c11e4855e86f3c6810f9a4abf917f69a6083330492aedb5621ebc3fd59778a40e0a7fa8450c8b2c6fe3923775419b2ea35cd19abe62c50020df991d9fc772d16dd5208468dc7a9b51c6723495fe0e72e818ee2b2a8581fab2caf6bd914e4876573b023862286ec88a698be2dd34c03925ab5ca0f50f0b2a246ab852e3779f0cf9d3e36f9ab9a50602d5e9216c3a29994e81e151accd88ea346d1be6588068e873

class DHError(Exception):
    pass

class DiffieHellman(object):

    def __init__(self, p=None, g=None, priv_key=None):
        if (p is not None) and (g is not None):
            self.p = p
            self.g = g
        else:
            self.p = def_p
            self.g = def_g
        self.priv_key = priv_key

    def generateKeys(self):
        if len(str(def_p)) < 1028: # Important sanity check
            raise DHError('Contact a developer immediately, your LookUp has been tampered with')
        if not self.priv_key:
            self.priv_key = randint(1, self.p - 1)
        priv_key = self.priv_key
        if isinstance(priv_key, bytes):
            priv_key = bytes_to_long(self.priv_key)
        self.pub_key = pow(self.g, self.priv_key, self.p)
        return long_to_bytes(self.pub_key)

    def computeKey(self, rpub_key):
        if not self.priv_key:
            raise DHError('Private key not generated')
        if isinstance(rpub_key, bytes):
            rpub_key = bytes_to_long(rpub_key)
        return long_to_bytes(pow(rpub_key, self.priv_key, self.p))