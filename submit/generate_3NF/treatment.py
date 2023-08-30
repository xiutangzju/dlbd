# -*- coding: UTF-8 -*-
from pandas import *
from submit.generate_3NF.tane import Tane
from submit.generate_3NF.normalization import Normalization
from submit.utils.connection import Connection


class Treatment:
    def __init__(self, file_name, c):
        file_path = 'media/' + file_name
        self.c = c
        self.dataset = read_csv(file_path)
        self.total_tuples = 0  # 总列数
        self.column_list = []  # 属性名数组
        self.columns_match_list = []
        self.final_table_schema_list = []
        self.column_max_len_list = []

    def pretreatment(self):
        # 重新设置列名
        for i, val in enumerate(self.dataset.columns.values):
            self.dataset.columns.values[i] = chr(i + ord('A'))
            self.columns_match_list.append(val)

        self.total_tuples = len(self.dataset.index)
        self.column_list = list(self.dataset.columns.values)

    def treatment(self):
        # 生成最小函数依赖集
        tane = Tane(self.dataset, self.total_tuples, self.column_list)
        tane.main()
        minimal_FD_list = tane.final_FD_list
        self.column_max_len_list = tane.column_max_len_list

        # 模式归一化，转换为3NF
        n = Normalization(self.column_list, minimal_FD_list, self.columns_match_list)
        n.normalization()
        self.final_table_schema_list = n.table_schema_list
        # print(self.final_table_schema_list)
        # for i in range(len(self.final_table_schema_list)):
        #     self.final_table_schema_list[i] = sorted(list(self.final_table_schema_list[i]))
        #     for j, element in enumerate(self.final_table_schema_list[i]):
        #         self.final_table_schema_list[i][j] = self.columns_match_list[ord(element) - ord('A')]
        # print(self.final_table_schema_list)

    # 后处理
    def post_treatment(self):
        # 将符合3NF的数据表添加到数据库中
        for i, table_schema in enumerate(self.final_table_schema_list):
            table_schema = sorted(list(table_schema))
            cur_data_list = []
            # 表名
            table_name = "t_" + str(i + 1)#这里
            self.c.delete_table(table_name)
            # 生成数据表
            sql = "create table " + table_name + " ( "
            for col in table_schema:
                col_name = self.columns_match_list[ord(col) - ord('A')]
                max_len = self.column_max_len_list[ord(col) - ord('A')]
                cur_data_list.append(self.dataset[col].tolist())
                sql += col_name + " varchar(" + str(max_len) + "), "
            sql = sql[0: -2]
            sql += ");"
            # if self.c.execute(sql) == -1:
            if self.c == None or self.c.execute(sql) == -1:
                return False

            # 插入数据
            data_size = len(cur_data_list[0])
            sql = "insert into " + table_name + " values"
            for j in range(data_size):
                sql += "("
                for k in range(len(cur_data_list)):
                    sql += "'" + str(cur_data_list[k][j]) + "', "
                sql = sql[0: -2]
                sql += "),"
            sql = sql[0: -2]
            sql += ");"
            print(sql)
            if self.c.execute(sql) == -1:
                return False

        return True

    def main(self):
        self.pretreatment()
        self.treatment()
        self.post_treatment()


if __name__ == '__main__':
    c = Connection("database_10_test")
    c.connect_database()
    t = Treatment(
        "C:/Users/Lenovo/Desktop/graduationDesign/DjangoProject/submit/upload_files/wide_table.csv",
        c)
    t.pretreatment()
    t.treatment()
    # t.post_treatment()