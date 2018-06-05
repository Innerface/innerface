import base64
import os

from Crypto.Cipher import AES
from passlib.hash import pbkdf2_sha256

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

key_list = [190, 208, 91, 152, 224, 15, 59, 93, 25, 93, 223, 250, 87, 214, 178, 169]
keymaterials = str(bytearray(key_list))


class AESCipher:
    def __init__(self, material, key):
        self.keymaterial = material
        self.secondkey = key

    def decryptkey(self, passwd):
        key = self.makekey(self.keymaterial)
        strongkey = self.strongpass(self.secondkey, key)
        password = self.decryptbasic(passwd, strongkey)
        return password

    def decryptbasic(self, enc, key):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:]))

    def makekey(self, material):
        material = base64.b64decode(material)
        intera = material[:4]
        intera = self.bytesToint(bytearray(intera))
        saltvalue = material[4:20]

        passwd = material

        key = pbkdf2_sha256.encrypt(passwd, salt=saltvalue, rounds=intera)
        key = key[:16]
        return key

    def strongpass(self, enc, key):
        bitsindex = 8
        enc = base64.b64decode(enc)
        intera = enc[:4]
        intera = self.bytesToint(bytearray(intera))
        saltvalue = enc[4:20]
        iv = enc[20:36]
        cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
        passwd = unpad(cipher.decrypt(enc[36:]))

        dk = pbkdf2_sha256.encrypt(passwd, salt=saltvalue, rounds=intera)
        dk = dk[:16]
        return dk

    def bytesToint(self, arraybyte):
        bytesindex = 4
        bitsindex = 8
        mask = 0xff
        out = 0
        i = 0
        while i < len(arraybyte):
            out += (arraybyte[i] & mask) << (bitsindex * i)
            i = i + 1
        return out
    #
    # def encrypt(self, raw, key):
    #     raw = pad(raw)
    #     intera = 10000
    #     salt = os.urandom(BS)
    #     iv = os.urandom(BS)
    #     cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
    #     return base64.b64encode(self.intToBytes(intera) + salt + iv + cipher.encrypt(raw.encode()))
    #
    # def encryptbasic(self, raw, key):
    #     raw = pad(raw)
    #     iv = os.urandom(BS)
    #     cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
    #     return base64.b64encode(iv + cipher.encrypt(raw.encode()))
    #
    # def creatematerial(self, material):
    #     intera = 10000
    #     salt = os.urandom(BS)
    #     material = base64.b64decode(material)
    #     return base64.b64encode(self.intToBytes(intera) + salt + material)
    #
    # def intToBytes(self, src):
    #     bytesindex = 4
    #     bitsindex = 8
    #     mask = 0xff
    #     arraybyte = bytearray(bytesindex)
    #     i = 0
    #     while i < len(arraybyte):
    #         arraybyte[i] = ((src >> (bitsindex * i)) & mask)
    #         i = i + 1
    #
    #     return arraybyte
    #


if __name__ == '__main__':
    keymaterial = b'ECcAAEtkYubvtUtbKR82meEEiJ6F6Z6JyFq1ui2ZqdqB6zKyR7KZq16uJqU='
    key = b'ECcAAOKb5DwtV8WD0FiY8s1TJbqOKjXlQrEur0OVTnYZS/Imq+CvJ2zhxWjYv6QsDIwW1F893r3ds7tzw5AfTvze2IE='
    A = AESCipher(keymaterial, key)
