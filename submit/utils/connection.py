# -*- coding: UTF-8 -*-
from multiprocessing import Process
import pymysql
from submit.utils.generate_table_schema import GenerateTableSchema


class MySQLConfig:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 3306
        self.user = 'root'
        self.password = '12344321'


class Connection:
    config = MySQLConfig()

    def __init__(self, database_name, host=config.host, port=config.port,
                 user=config.user, password=config.password):
        self.conn = None
        self.cur = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database_name = database_name

    def connect_database(self):
        try:
            self.conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.database_name
            )
            self.cur = self.conn.cursor()
            return True
        except Exception as e:
            print(e)
            return False

    # 仅连接MySQL，需要创建数据库
    def connect_MySQL(self):
        try:
            self.conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
            )
            self.cur = self.conn.cursor()
            return True
        except Exception as e:
            print(e)
            return False

    """
    判断该数据库是否已经存在
    返回值：1代表已经存在，0代表没有创建，-1代表执行语句失败
    """

    def database_is_exist(self):
        try:
            sql = "show databases like '" + self.database_name + "';"
            database = self.cur.execute(sql)
            if database > 0:
                return 1
            else:
                return 0
        except Exception as e:
            print(e)
            return -1

    def create_database(self):
        try:
            sql = "create database " + self.database_name + ";"
            self.cur.execute(sql)
            return True
        except Exception as e:
            print(e)
            return False

    def execute(self, sql):
        try:
            row_num = self.cur.execute(sql)
            self.conn.commit()
            return row_num
        except Exception as e:
            print(e)
            return -1

    def fetchAll(self):
        try:
            res = self.cur.fetchall()
            return res
        except Exception as e:
            print(e)
            return None

    def get_table_schema(self):
        """ 获取表结构 """

        table_schemas = []
        sql = "show tables;"
        table_num = self.execute(sql)
        for i in range(1, table_num + 1):
            sql = "desc t_" + str(i) + ";"
            self.execute(sql)
            cur_schema = self.fetchAll()
            table_schemas.append(cur_schema)
        return table_schemas

    def get_table_name(self):
        sql = "show tables;"
        self.execute(sql)
        table_names = self.fetchAll()
        table_names = list(table_names)
        for i in range(len(table_names)):
            table_names[i] = "".join(table_names[i])
        return table_names

    def delete_table(self, table_name):
        sql = "drop table if exists " + table_name
        self.execute(sql)

    def close(self):
        try:
            self.cur.close()
            self.conn.close()
            self.cur = None
            self.conn = None
            return True
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    c = Connection("database_10_test")
    c.connect_database()
    table_names = c.get_table_name()
    print(table_names)
