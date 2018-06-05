import pymysql
from tools.read_config import SysConfig


class MysqlConn(object):
    def __init__(self):
        self.config = SysConfig()
        self.db = pymysql.connect(host=self.config.getValue('db', 'host'), user=self.config.getValue('db', 'user'),
                                  password=self.config.getPsw('db', 'password').decode(),
                                  db=self.config.getPsw('db', 'database').decode(),
                                  port=self.config.getInt('db', 'port'), charset='utf8')
        self.cur = self.db.cursor()

    def execute(self, exec_sql):
        self.cur.execute(exec_sql)
        return self.cur.fetchall()


if __name__ == '__main__':
    r = MysqlConn()
    sql = 'select * from data_admin_sensitive'
    result = r.execute(sql)
    print(result[0][1])
