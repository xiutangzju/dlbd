import json
import os
import asyncio
import random

import websockets
import threading
import re
import multiprocessing
from threading import Thread
from asgiref.sync import sync_to_async

from django.shortcuts import render, HttpResponse
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from submit.detection.detected_bug import DetectedBug
from submit.utils.form import BootstrapForm, BootstrapModalForm
from submit.utils.data_source import data_source
from submit.utils.my_encoder import MyEncoder
from submit.utils.connection import Connection
from submit import models
from submit.generate_3NF.treatment import Treatment
from submit.utils.generate_table_schema import GenerateTableSchema
from submit.detection.create_records import CreateRecords


# Create your views here.
# auth_choices = [
#     ('auth', 'User & Password'),
#     ('no auth', 'No auth')
# ]


class ConnectingInfo(BootstrapModalForm):
    class Meta:
        model = models.Connection
        fields = ['host', 'port', 'username', 'password', 'database']


class LoginInfo(BootstrapModalForm):
    class Meta:
        model = models.User
        fields = ['username', 'password']
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "username"}),
            "password": forms.PasswordInput(attrs={"placeholder": "password"}),
        }


class RegisterInfo(BootstrapModalForm):
    confirm_password = forms.CharField(
        label="confirm_password:",
        widget=forms.PasswordInput(attrs={"placeholder": "confirm your password"}),
    )

    class Meta:
        model = models.User
        fields = ['username', 'password', 'confirm_password']
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "username"}),
            "password": forms.PasswordInput(attrs={"placeholder": "password"}),
        }


connection_list = dict() #存放用户连接数据库的对象
# create_records_list = dict()

tem_operator = ""
bug_type = 0
async def websocket_listener():
    async with websockets.connect("ws://localhost:8885") as websocket:
        while True:
            message = await websocket.recv() #就是Java端的json_String
            print(f"{message}")
            try:
                entry = json.loads(message) #转化为字典
                print(entry)
                tem_operator = entry["operator"] #获取operator 载入临时变量
                update_bug_type(tem_operator)#对这个临时operator进行处理来修改bug类型数量
                user_object = await sync_to_async(models.User.objects.get)(id=1)#从python本地数据库拉出来。
                #entry["original_execution_plan"]就是我要的参数，另一个参数是operator
                #这两个参数进入扫描函数，得到的结果就是table_scan
                #再将得到的table_scan传入数据库完成存储
                table_scan_result = table_scan(entry["operator"],entry["original_execution_plan"])
                detectedBug = DetectedBug(user_object,bug_id=entry["bug_id"],original_query=entry["original_query"],\
                                          original_execution_plan=entry["original_execution_plan"],\
                                          original_ground_truth=entry["original_ground_truth"],\
                                          original_query_result=entry["original_ground_result"],\
                                          operator=entry["operator"],sqlfile=entry["sqlfile"],\
                                          table_scan=table_scan_result) #这里是传来的数据
                await sync_to_async(detectedBug.save)()
                print("############## detect bug saved ##############")
            except json.JSONDecodeError as e:
                print("JSON parsing error:", e)

def remove_cost_info(input_string): # 使用正则表达式匹配 (cost 以及后面的内容
    pattern = re.compile(r'\(cost[^)]*\)')#匹配以(cost开头的字符串
    result = re.sub(pattern, '', input_string)#取缔(cost开头的字符串
    return result

def get_subString(str1,str2):#这个函数获取两个字符串的最大子串的长度
    m = len(str1)
    n = len(str2)
    # 创建一个二维数组来保存最长公共子串的长度
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_length = 0  # 最大子串长度
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                max_length = max(max_length, dp[i][j])
    return max_length
def table_scan(operator,original_execution_plan):#获取包含最大子串的执行计划
    resultPlan = ""
    max_length = 0
    exePlan = original_execution_plan.split("->")
    for subPlan in exePlan:
        i = get_subString(operator,subPlan)
        if i>max_length:
            max_length = i
            resultPlan = subPlan
    return remove_cost_info(resultPlan)#取缔cost部分字符串

received_strings = {}  # 用于跟踪已经接收过的字符串
def update_bug_type(input_string):
    global bug_type
    if input_string in received_strings:
        pass
    else:
        bug_type += 1
        received_strings[input_string] = True
#-----------------------分割线--------------------------
def start_websocket_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(websocket_listener())

def home(request):
    """ 起始页 """
    websocket_thread = threading.Thread(target=start_websocket_thread)
    websocket_thread.start()
    return render(request, 'home.html')

def user_img(request):
    user_info = request.session.get("user_info")
    if user_info:
        name_header = user_info.get("username")[0].upper()
        return HttpResponse("user-" + name_header)
    else:
        return HttpResponse("user")

def login(request):
    if request.method == 'GET':
        login_form = LoginInfo()
        return render(request, 'modal_alert/login_alert.html', {'login_form': login_form})

    login_form = LoginInfo(data=request.POST)
    if login_form.is_valid():
        user_object = models.User.objects.filter(**login_form.cleaned_data).first()
        if not user_object:
            login_form.add_error("password", "Incorrect username or password")
        else:
            # 登录成功
            request.session["user_info"] = {"id": user_object.id, "username": user_object.username}
            # 更新当前状态
            cur_step = models.User.objects.filter(username=user_object.username).values('step').first().get("step")
            if cur_step == 0:
                request.session["step"] = 1
                models.User.objects.filter(username=user_object.username).update(step=1)
            else:
                request.session["step"] = cur_step
                if cur_step >= 2:
                    # 自动连接数据库
                    cur_connection = models.Connection.objects.filter(user_id=user_object.id).first()
                    cur_database = cur_connection.database
                    c = None
                    if cur_connection.host is None:
                        # 连接服务端的数据库
                        c = Connection(cur_database)
                    else:
                        c = Connection(**cur_connection)
                    c.connect_database()
                    connection_list[cur_database] = c

            return JsonResponse({'status': 'success'})

    errors = []
    for item in login_form:
        errors.append(item.errors)

    res = {
        'status': 'failed',
        'errors': errors
    }
    return JsonResponse(res)

def register(request):
    if request.method == "GET":
        register_form = RegisterInfo()
        return render(request, 'modal_alert/register_alert.html', {"register_form": register_form})

    register_form = RegisterInfo(data=request.POST)
    if register_form.is_valid():
        # 判断输入是否符合规范
        register_info = register_form.cleaned_data
        username_first_char = register_info.get("username")[0].upper()
        # 两次输入的密码不相同
        if register_info.get("password") != register_info.get("confirm_password"):
            # 添加错误
            register_form.add_error("confirm_password", "The passwords entered twice are different")
        # 存在重复的用户名
        elif models.User.objects.filter(username=register_info.get("username")).first():
            register_form.add_error("username", "The username has been used")
        # 用户名首字符不是字母和数字
        elif (ord(username_first_char) not in range(ord('A'), ord('Z'))) and \
                (ord(username_first_char) not in range(ord('0'), ord('9'))):
            register_form.add_error("username", "Please enter the first character as a letter or number")
        else:
            register_form.save()
            # 创建一个DataSource数据行
            models.Connection.objects.create(
                user_id=models.User.objects.filter(username=register_info.get("username")).first(),
            )
            # 创建一个TestFile数据行
            models.TestFile.objects.create(
                user_id=models.User.objects.filter(username=register_info.get("username")).first(),
            )
            # # 创建一个Statistics数据行
            models.Statistics.objects.create(
                user_id=models.User.objects.filter(username=register_info.get("username")).first(),
            )
            return JsonResponse({"status": "success"})

    errors = []
    for item in register_form:
        errors.append(item.errors)

    res = {
        'status': 'failed',
        'errors': errors
    }
    return JsonResponse(res)

def logout(request):
    # 删除连接
    database_name = models.Connection.objects.filter(user_id=request.session["user_info"].get("id")).first().database
    if database_name in connection_list:
        connection_list[database_name].close()
        del connection_list[database_name]

    request.session.clear()

    return JsonResponse({"status": "success"})


def change_step(request, cur_step):
    request.session["step"] = cur_step
    models.User.objects.filter(id=request.session["user_info"].get("id")).update(step=cur_step)


def get_connecting_alert(request):
    """ 连接数据库页 """

    data_source_form = ConnectingInfo()
    return render(request, 'modal_alert/connecting_alert.html',
                  {'data_source': data_source,
                   'data_source_form': data_source_form,
                   })

def connect_public_database(request):
    """ 连接用户公开的数据库 """

    data_source_form = ConnectingInfo(data=request.POST)
    if data_source_form.is_valid():
        # 将表单数据转换为对象形式，原来是HTML文本形式
        database_info = data_source_form.cleaned_data

        # 连接数据库
        c = Connection(
            database_info.get("database"),
            host=database_info.get("host"),
            port=database_info.get("port"),
            user=database_info.get("username"),
            password=database_info.get("password")
        )
        if c.connect_database():
            change_step(request, 2)
            models.Connection.objects.filter(user_id=request.session["user_info"].get("id")).update(**database_info)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({"status": "connecting error"})

    errors = []
    for item in data_source_form:
        errors.append(item.errors)

    res = {
        'status': 'input error',
        'errors': errors
    }
    return JsonResponse(res)

def connect_server_database(request):
    """ 连接服务端提供的数据库 """

    user_id = request.session.get("user_info").get("id")
    database_name = "database_" + str(user_id) + "_" + request.POST.get("database_name")
    c = Connection(database_name)
    print(c)
    status = "success"
    if c.connect_MySQL():
        # 判断该用户是否已经创建过该数据库
        is_exist = c.database_is_exist()
        if is_exist == -1:
            status = "server error"
        elif is_exist == 1:
            if not (c.close() and c.connect_database()):
                status = "server error"
        elif not (c.create_database() and c.close() and c.connect_database()):
            status = "create error"
    else:
        status = "server error"

    if status == "success":
        change_step(request, 2)
        connection_list[database_name] = c
        models.Connection.objects.filter(user_id=request.session["user_info"].get("id")).update(
            database=database_name,
            host=None,
            port=None,
            username=None,
            password=None,
        )
        print(connection_list)

    return JsonResponse({"status": status})

def get_step(request):
    cur_step = request.session["step"]
    res = {
        "status": "success",
        "cur_step": cur_step
    }
    return JsonResponse(res)

@csrf_exempt
def upload(request):
    user_id = request.session["user_info"].get("id")
    file_object = request.FILES.get("file")
    file_object.name = str(user_id) + "_" + file_object.name

    # 删除原有的同名本地文件
    if os.path.exists('media/test_files/' + file_object.name):
        os.remove('media/test_files/' + file_object.name)

    # 这里更新文件必须这样，直接update无法在本地创建文件
    cur_file = models.TestFile.objects.get(user_id=user_id)
    cur_file.file = file_object
    cur_file.save()

    change_step(request, 3)
    return JsonResponse({"status": "success"})


def generate(request):
    # 生成数据
    c = connection_list.get(
        models.Connection.objects.filter(user_id=request.session["user_info"].get("id")).first().database
    )
    print(c)
    print(type(c))
    treatment = Treatment(
        models.TestFile.objects.filter(user_id=request.session["user_info"].get("id")).first().file.name
        , c)
    treatment.main()

    # 查询表结构
    table_schema = c.get_table_schema()
    g = GenerateTableSchema(table_schema)
    g.generate_all()
    res = {
        "status": "success",
        "tables": g.tables,
        "intra_links": g.intra_links,
        "external_links": g.external_links
    }

    if models.User.objects.filter(id=request.session["user_info"].get("id")).values("step").first().get("step") < 4:
        change_step(request, 4)
    return JsonResponse(res, encoder=MyEncoder)


def start(request):
    cur_user_id = request.session["user_info"].get("id")
    # 删除该用户原有的bug记录和检测记录
    models.LogicalBug.objects.filter(user_id=cur_user_id).delete()
    models.Statistics.objects.filter(user_id=cur_user_id).update(
        query_num=0, query_type_num=0, status="start"
    )
    # create_records = CreateRecords(models.User.objects.get(id=request.session["user_info"].get("id")))
    # cur_process = Thread(target=create_records.generateBug)
    # cur_process.start()
    # create_records_list[cur_user_id] = create_records
    global bug_type
    bug_type = 0
    change_step(request, 5)
    return JsonResponse({"status": "success"})

def area1(request):
    c = connection_list.get(
        models.Connection.objects.filter(user_id=request.session["user_info"].get("id")).first().database
    )
    table_schema = c.get_table_schema()
    g = GenerateTableSchema(table_schema)
    g.generate_table()
    return render(request, 'components/area1.html', {"tables": g.tables})

def area2(request):
    c = connection_list.get(
        models.Connection.objects.filter(user_id=request.session["user_info"].get("id")).first().database
    )
    table_names = c.get_table_name()
    return render(request, 'components/area2.html', {"table_names": table_names})

def area3(request):
    return render(request, 'components/area3.html')

def area4(request):
    return render(request, 'components/area4.html')

def polling(request):#这里载入数据进入前端以备调用
    logical_bugs = models.LogicalBug.objects.filter(
        user_id=request.session["user_info"].get("id"),
        is_display=False).values("severity", "bug_id", "category", "operator", "status", "id").all()
    bug_list = list(logical_bugs)
    logical_bugs.update(is_display=True)
    statistics = models.Statistics.objects.filter(user_id=request.session["user_info"].get("id")).first()

    res = {
        "status": "success",
        "bug_list": bug_list,
        "statistics": statistics,
        "bug_type":bug_type
    }
    return JsonResponse(res, encoder=MyEncoder)

def bug_detail(request):#这里是bug_detail细节
    bug_id = request.GET.get("bug_id")
    bug = models.LogicalBug.objects.filter(id=bug_id).values("id", "bug_id", "severity", "database", "category",
                                                             "operator","sqlfile","table_scan").first()
    severity_match = [
        ["S1(Critical)", "#FF0000"],
        ["S2(Serious)", "#FF8C00"],
        ["S3(Non-critical)", "#FFD700"],
    ]
    severity = severity_match[bug.get("severity") - 1][0]
    severity_color = severity_match[bug.get("severity") - 1][1]

    return render(request, 'modal_alert/bug_detail_alert.html',
                  {"bug": bug, "severity": severity, "severity_color": severity_color})

def dynamic_bug_detail(request):
    bug_id = request.GET.get("bug_id")
    detail_type = request.GET.get("detail_type")
    if detail_type == "original":
        bug = models.LogicalBug.objects.filter(id=bug_id).values("original_query", "original_ground_truth",
                                                                 "original_query_result",
                                                                 "original_execution_plan").first()
    else:
        bug = models.LogicalBug.objects.filter(id=bug_id).values("minimal_query", "minimal_ground_truth",
                                                                 "minimal_query_result",
                                                                 "minimal_execution_plan").first()

    res = {
        "status": "success",
        "bug": list(bug.values())
    }
    return JsonResponse(res, encoder=MyEncoder)

def pause_detection(request):
    """ 暂停检测，保存断点 """
    cur_user_id = request.session["user_info"].get("id")
    # cur_record = create_records_list[cur_user_id]
    # del create_records_list[cur_user_id]
    # cur_record.is_exit = True
    # cur_point = str(cur_record.bug_id) + "/" + str(cur_record.times)
    # models.Statistics.objects.filter(user_id=cur_user_id).update(break_point=cur_point, status="pause")
    return JsonResponse({"status": "success"})

def continue_detection(request):
    """ 继续检测 """
    cur_user_id = request.session["user_info"].get("id")
    cur_point = models.Statistics.objects.filter(user_id=cur_user_id).values("break_point").first().get("break_point")
    cur_point = cur_point.split("/")
    cur_record = CreateRecords(models.User.objects.filter(id=cur_user_id).first(), int(cur_point[0]), int(cur_point[1]))
    cur_process = Thread(target=cur_record.generateBug)
    cur_process.start()
    # create_records_list[cur_user_id] = cur_record
    models.Statistics.objects.filter(user_id=cur_user_id).update(status="start")
    return JsonResponse({"status": "success"})

def stop_detection(request):
    """ 终止检测 """
    cur_user_id = request.session["user_info"].get("id")
    # cur_record = create_records_list[cur_user_id]
    # del create_records_list[cur_user_id]
    # cur_record.is_exit = True
    cur_point = "0/0"
    models.Statistics.objects.filter(user_id=cur_user_id).update(break_point=cur_point, status="none")
    return JsonResponse({"status": "success"})

def retest(request):
    """ 重新检测 """
    cur_bug_id = request.GET.get("bug_id")
    models.LogicalBug.objects.filter(id=cur_bug_id).update(status=True)
    return JsonResponse({"status": "success"})

def review(request):
    """ 重新查看之前的检测记录 """
    cur_user_id = request.session["user_info"].get("id")
    bugs = models.LogicalBug.objects.filter(user_id=cur_user_id).values("severity", "bug_id", "category", "operator",
                                                                        "status", "id").all()
    bugs = list(bugs)
    statistics = models.Statistics.objects.filter(user_id=cur_user_id).first()
    res = {
        "status": "success",
        "bug_list": bugs,
        "statistics": statistics,
    }
    return JsonResponse(res, encoder=MyEncoder)

def detection_status(request):
    cur_user_id = request.session["user_info"].get("id")
    cur_status = models.Statistics.objects.filter(user_id=cur_user_id).values("status").first().get("status")
    res = {
        "status": "success",
        "detection_status": cur_status
    }
    return JsonResponse(res, encoder=MyEncoder)