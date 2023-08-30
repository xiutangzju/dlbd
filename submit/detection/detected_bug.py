from submit import models
import random
class DetectedBug:
    def __init__(self, user_id, bug_id, operator ,original_query, \
                 original_execution_plan,original_ground_truth,original_query_result,\
                 sqlfile,table_scan): 
        self.user_id = user_id
        self.bug_id = bug_id
        self.times = 0
        self.is_exit = False
        self.severity = random.randint(1,3)
        self.category = "Optimizer"
        self.operator = operator
        self.database = "MySQL8.0.28"
        self.original_query = original_query
        self.minimal_query = "" 
        self.original_execution_plan = original_execution_plan
        self.original_ground_truth = original_ground_truth
        self.original_query_result = original_query_result
        self.sqlfile = sqlfile
        self.table_scan = table_scan
    def save(self): 
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


