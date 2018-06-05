# Author: YuYuE (1019303381@qq.com) 2018.03.
import configparser
import os
from chatbot.settings import BASE_DIR
from tools.decrypt import AESCipher


config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'chatbot.conf'))
keyMaterial = config.get("crypto", "keymaterial")
secondkey = config.get("crypto", "key")
AESProcess = AESCipher(keyMaterial, secondkey)
redis_host = config.get("redis", "host")
redis_port = config.get("redis", "port")
redis_db = config.get("redis", "db")
redis_password_ = config.get("redis", "password")
redis_password = AESProcess.decryptkey(redis_password_).decode()