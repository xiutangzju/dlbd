from submit import models
import random
class DetectedBug:
    def __init__(self, user_id, bug_id, operator ,original_query, \
                 original_execution_plan,original_ground_truth,original_query_result,\
                 sqlfile,table_scan): #这里是将后端的信息提取存入对象
        self.user_id = user_id
        self.bug_id = bug_id
        self.times = 0
        self.is_exit = False
        self.severity = random.randint(1,3)#随机选择严重程度
        self.category = "Optimizer" #写死
        self.operator = operator
        self.database = "MySQL8.0.28"#写死
        self.original_query = original_query
        self.minimal_query = "" #不要了
        self.original_execution_plan = original_execution_plan
        self.minimal_execution_plan = ""          #不要了
        self.minimal_ground_truth = "t1.c0"       #不要了
        self.minimal_query_result = "t1.c0/1/2/3" #不要了
        self.original_ground_truth = original_ground_truth
        self.original_query_result = original_query_result
        self.sqlfile = sqlfile
        self.table_scan = table_scan
    def save(self): #这里将上面存入对象的信息存入数据库中
        models.LogicalBug.objects.create(
            user_id=self.user_id,
            bug_id=self.bug_id,
            severity=self.severity,
            database=self.database,
            category=self.category,
            operator=self.operator,
            original_query=self.original_query,
            original_execution_plan=self.original_execution_plan,
            original_ground_truth=self.original_ground_truth,
            original_query_result=self.original_query_result,
            minimal_ground_truth=self.minimal_ground_truth,
            minimal_query_result=self.minimal_query_result,
            minimal_execution_plan=self.minimal_execution_plan,
            minimal_query=self.minimal_query,
            sqlfile=self.sqlfile,
            table_scan = self.table_scan
        )


