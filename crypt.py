import configparser
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
    def decrypt_key(self, keymaterial, rootkey, passwd):
        key = self.makekey(keymaterial)
        strongkey = self.strongpass(rootkey, key)
        password = self.decryptbasic(passwd, strongkey)
        return password

    def encrypt(self, raw, key):
        raw = pad(raw)
        intera = 10000
        salt = os.urandom(BS)
        iv = os.urandom(BS)
        cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
        return base64.b64encode(self.intToBytes(intera) + salt + iv + cipher.encrypt(raw.encode()))

    def encryptbasic(self, raw, key):
        raw = pad(raw)
        iv = os.urandom(BS)
        cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decryptbasic(self, enc, key):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:]))

    def creatematerial(self, material):
        intera = 10000
        salt = os.urandom(BS)
        material = base64.b64decode(material)
        return base64.b64encode(self.intToBytes(intera) + salt + material)

    def makekey(self, material):
        material = base64.b64decode(material)
        intera = material[:4]
        intera = self.bytesToint(bytearray(intera))
        saltvalue = material[4:20]
        materials = material[20:]
        # materials = [chr(a ^ b) for (a, b) in zip(materials, keymaterials)]
        passwd = material

        key = pbkdf2_sha256.encrypt(passwd, salt=saltvalue, rounds=intera)
        key = key[:16]
        return key

    def strongpass(self, enc, key):
        print(type(enc))
        bitsindex = 8
        enc = base64.b64decode(enc)
        print(enc)
        intera = enc[:4]
        intera = self.bytesToint(bytearray(intera))
        saltvalue = enc[4:20]
        iv = enc[20:36]
        cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
        passwd = unpad(cipher.decrypt(enc[36:]))

        dk = pbkdf2_sha256.encrypt(passwd, salt=saltvalue, rounds=intera)
        dk = dk[:16]
        return dk

    def intToBytes(self, src):
        bytesindex = 4
        bitsindex = 8
        mask = 0xff
        arraybyte = bytearray(bytesindex)
        i = 0
        while i < len(arraybyte):
            arraybyte[i] = ((src >> (bitsindex * i)) & mask)
            i = i + 1

        return arraybyte

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


if __name__ == "__main__":
    readfile = "crypt.conf"
    writefile = "chatbot.conf"
    #
    readconfig = configparser.RawConfigParser()
    readconfig.read(readfile)
    writeconfig = configparser.RawConfigParser()
    writeconfig.read(writefile)
    #
    AESProcess = AESCipher()
    #
    keyMaterial = readconfig.get("crypto", "keymaterial")
    materialkey = AESProcess.creatematerial(keyMaterial)
    writeconfig.set("crypto", "keymaterial", materialkey.decode())
    #
    secondkey = readconfig.get("crypto", "key")
    key = AESProcess.makekey(materialkey)

    cipertext = AESProcess.encrypt(secondkey, key)
    writeconfig.set("crypto", "key", cipertext.decode())

    strongkey = AESProcess.strongpass(cipertext, key)  # strong key

    postgreDB_db = readconfig.get("db", "database")
    cipertext = AESProcess.encryptbasic(postgreDB_db, strongkey)
    writeconfig.set("db", "database", cipertext.decode())

    postgreDB_passwd = readconfig.get("db", "password")
    cipertext = AESProcess.encryptbasic(postgreDB_passwd, strongkey)
    writeconfig.set("db", "password", cipertext.decode())

    redis_passwd = readconfig.get("redis", "password")
    cipertext = AESProcess.encryptbasic(redis_passwd, strongkey)
    writeconfig.set("redis", "password", cipertext.decode())

    redis_passwd = readconfig.get("mail", "email_host_password")
    cipertext = AESProcess.encryptbasic(redis_passwd, strongkey)
    writeconfig.set("mail", "email_host_password", cipertext.decode())
    STR = AESProcess.decryptbasic(cipertext, strongkey)
    print(STR)

    with open(writefile, 'w') as configfile:
        writeconfig.write(configfile)

    print('crypt successful!')
