from django.db import models
import random
# Create your models here.
class User(models.Model):
    username = models.CharField(verbose_name='username:', max_length=64)
    password = models.CharField(verbose_name='password:', max_length=64)
    step = models.IntegerField(default=0)

class Connection(models.Model):
    # 外键
    user_id = models.ForeignKey(to='User', related_name='user_data_source', on_delete=models.CASCADE)
    host = models.CharField(verbose_name='Host:', max_length=64, null=True)
    port = models.IntegerField(verbose_name='Port:', null=True)
    username = models.CharField(verbose_name='User:', max_length=128, null=True)
    password = models.CharField(verbose_name='Password:', max_length=128, null=True)
    database = models.CharField(verbose_name='Databases:', max_length=128, null=True)

class TestFile(models.Model):
    user_id = models.ForeignKey(to='User', on_delete=models.CASCADE)
    file = models.FileField(upload_to='./test_files', null=True)

class LogicalBug(models.Model):
    user_id = models.ForeignKey(to='User', on_delete=models.CASCADE)
    bug_id = models.IntegerField()
    severity = models.IntegerField()
    database = models.CharField(max_length=63)
    category = models.CharField(max_length=63)
    operator = models.CharField(max_length=2048)
    status = models.BooleanField(default=False)
    original_query = models.CharField(max_length=1023)
    minimal_query = models.CharField(max_length=511)
    # execution_plan = models.CharField(max_length=1023)
    original_execution_plan = models.CharField(max_length=2048, default="")
    minimal_execution_plan = models.CharField(max_length=2048, default="")
    original_ground_truth = models.CharField(max_length=1023)
    original_query_result = models.CharField(max_length=1023)
    minimal_ground_truth = models.CharField(max_length=1023)
    minimal_query_result = models.CharField(max_length=1023)
    is_display = models.BooleanField(default=False)
    sqlfile = models.TextField(default=True)#存储sql文件的信息
    table_scan = models.CharField(max_length=1024, default="")#存储table信息的执行计划


class Statistics(models.Model):
    user_id = models.ForeignKey(to='User', on_delete=models.CASCADE)
    query_num = models.IntegerField(default=0)
    query_type_num = models.IntegerField(default=0)
    # 断点，当用户暂停后保存断点位置，便于之后继续检测
    break_point = models.CharField(max_length=32, default="0/0")
    # 当前检测状态
    status = models.CharField(max_length=32, default="none")
