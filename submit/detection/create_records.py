# -*- coding: UTF-8 -*-
#这个函数目前没有任何作用
import time
import random
from submit import models


class CreateRecords:
    def __init__(self, user_id, bug_id=0, times=0):
        self.user_id = user_id
        self.bug_id = bug_id
        self.times = times
        self.is_exit = False
        self.severity = random.randint(1,3)
        self.category = ["Optimizer", "Optimizer", "Optimizer", "Optimizer", "Options", "Optimizer", "Storage",
                         "Optimizer"]
        self.operator = ["Table Join", "Aggregation", "Column Sort", "Table Join", "Sort_buffer_size", "Table Join",
                         "Repair Table", "Table Join"]
        self.database = "MySQL8.0.28"
        self.original_query = "\nSET optimizer_switch='semijoin=on';\n" \
                              "SELECT *\n" \
                              "FROM T4\n" \
                              "WHERE T4.goodsName IN (\n" \
                              "SELECT T3.goodsName\n" \
                              "FROM T3\n" \
                              "WHERE (T3.goodsName NOT IN (\n" \
                              "SELECT T3.goodsName\n" \
                              "FROM T3\n" \
                              "WHERE T3.goodsName)) = (T3.goodsName);"
        self.minimal_query = "\nSET optimizer_switch='semijoin=on';\n" \
                             "SELECT t1.c0\n" \
                             "FROM t1\n" \
                             "WHERE (t1.c0 NOT IN (\n" \
                             "SELECT t2.c0\n" \
                             "FROM t1 as t2\n" \
                             "WHERE t2.c0 )) = (t1.c0);\n"
        self.original_execution_plan = "| -> Inner hash join (T3.goodsName = `<subquery2>`.ref1)  (cost=8.25 rows=15)\n" \
                                       "-> Table scan on T3  (cost=3.23 rows=15)\n" \
                                       "-> Hash\n" \
                                       "-> Table scan on <subquery2>  (cost=3.25..3.58 rows=15)\n" \
                                       "-> Materialize with deduplication  (cost=1.52..2.62 rows=15)\n" \
                                       "-> Filter: (t2.c0 is not null)  (cost=2.58 rows=15)\n" \
                                       "-> Table scan on t2  (cost=2.35 rows=15)\n" \
                                       "|"
        self.minimal_execution_plan = "| -> Inner hash join (t1.c0 = `<subquery2>`.ref1)  (cost=7.38 rows=6)\n" \
                                      "-> Table scan on t1  (cost=0.35 rows=6)\n" \
                                      "-> Hash\n" \
                                      "-> Table scan on <subquery2>  (cost=0.43..2.58 rows=6)\n" \
                                      "-> Materialize with deduplication  (cost=1.38..3.53 rows=6)\n" \
                                      "-> Filter: (t2.c0 is not null)  (cost=0.35 rows=6)\n" \
                                      "-> Table scan on t2  (cost=0.35 rows=6)\n" \
                                      "|"
        self.minimal_ground_truth = "t1.c0"
        self.minimal_query_result = "t1.c0/1/2/3"
        self.original_ground_truth = "goodsName;price;orderId/computer;1400;34542/coffee;12;74535/book;29;12409/" \
                                     "game;23;74512"
        self.original_query_result = "goodsName;price;orderId/computer;1400;34542/radio;1234;09812/coffee;12;74535/" \
                                     "book;29;12409/game;23;74512/watch;2800;12490/mouse;97;09134/phone;2499;45702"

    def generateBug(self):
        cur_statistics = models.Statistics.objects.filter(user_id=self.user_id).first()
        # query_num = cur_statistics.query_num
        # query_type_num = cur_statistics.query_type_num
        while True:
            if cur_statistics.query_num >= 10000 or self.is_exit:
                break
            cur_statistics.query_num += 60
            cur_statistics.query_type_num += 1
            cur_statistics.save()
            # models.Statistics.objects.filter(user_id=self.user_id).update(query_num=query_num,
            #                                                               query_type_num=query_type_num)

            if self.times in [1, 3, 5, 7, 8, 10, 11, 13]:
                models.LogicalBug.objects.create(
                    user_id=self.user_id,
                    bug_id=self.bug_id + 1,
                    severity=self.severity[self.bug_id],
                    database=self.database,
                    category=self.category[self.bug_id],
                    operator=self.operator[self.bug_id],
                    original_query=self.original_query,
                    minimal_query=self.minimal_query,
                    original_execution_plan=self.original_execution_plan,
                    minimal_execution_plan=self.minimal_execution_plan,
                    original_ground_truth=self.original_ground_truth,
                    original_query_result=self.original_query_result,
                    minimal_ground_truth=self.minimal_ground_truth,
                    minimal_query_result=self.minimal_query_result
                )
                self.bug_id += 1

            self.times += 1
            time.sleep(1)
