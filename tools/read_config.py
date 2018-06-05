import configparser
import os
from pathlib import Path
from tools.decrypt import AESCipher


class SysConfig(object):
    def __init__(self):
        self.config_path = Path(os.path.abspath(__file__)).parent.parent/'chatbot.conf'
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)
        self.AESProcess = AESCipher(self.config.get("crypto", "keymaterial"), self.config.get("crypto", "key"))

    def getValue(self, node_name, config_key):
        return self.config.get(node_name, config_key)

    def getPsw(self, node_name, config_key):
        return self.AESProcess.decryptkey(self.config.get(node_name, config_key))

    def getInt(self, node_name, config_key):
        return int(self.config.get(node_name, config_key))

    def getStr(self, node_name, config_key):
        return str(self.config.get(node_name, config_key))

