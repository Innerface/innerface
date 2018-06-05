# Author: YuYuE (1019303381@qq.com) 2018.04.
import redis
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


def connect(password=True):
    if password:
        conn = redis.Redis(redis_host, redis_port, redis_db, redis_password)
    else:
        conn = redis.Redis(redis_host, redis_port, redis_db, '')
    return conn


def get_redis(key, conn=None):
    if conn is None:
        conn = connect()
    return conn.get(key)


def set_redis(key, value, conn=None):
    if conn is None:
        conn = connect()
    conn.set(key, value)


if __name__ == "__main__":
    conn = connect()
    set_redis('name', 'yuyue', conn)
    print(get_redis('name1', conn))
