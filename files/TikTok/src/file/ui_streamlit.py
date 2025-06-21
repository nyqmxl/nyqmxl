'''
pip install pymongo streamlit websockets pyotp numpy opencv-python selenium pillow pyautogui psutil urllib3 numpy

'''
# from os import popen
# _return_ = popen("dir").read()
# print(_return_)

from time import sleep
from json import loads, dumps
from datetime import datetime as dt
from uuid import uuid1
from pymongo import MongoClient
from streamlit import *


mongo = MongoClient("mongodb://localhost:27017/")
mac = str(uuid1())[-12:]
mongo_read = mongo["app_cache"][f"tiktok_read_{mac}"]
mongo_write = mongo["app_cache"][f"tiktok_write_{mac}"]
tiktok_raw = mongo["tiktok"][f"raw_{mac}"]


set_page_config(
    page_title="TikTok任务页",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="auto"
)

title("欢迎使用：TikTok任务页！")
markdown(F"【**{str(dt.now())[:-7]}**】 正在使用 {mac} 设备：使用前请确保组件服务已启动，否则无法继续响应任务！")

tab = list(tabs(["状态", "数据", "AutoXJS", "管理", "执行"]))

mongo_write.insert_one({"$query": {}})
sleep(2)
device = mongo_read.find_one_and_delete(
    {
        "query.parameters.type": {
            "$regex": "TikTok", "$options": "i"
        }
    }.copy(), {"_id": 0}
)

if (device):
    device = [
        {
            "device": f1["parameters"]["device"],
            "type": f1["parameters"]["type"],
            "send": f1["send"],
            "receive": f1["receive"]
        }
        for f1 in device["query"]
    ]
sleep(2)
with tab[0]:
    import psutil

    title("系统资源监控")

    # 创建刷新按钮
    refreshing = False  # 初始状态为不刷新

    # 创建三列布局用于显示指标
    col1, col2, col3 = columns(3)

    if col1.button("刷新"):
        rerun()
    if col2.button("开始"):
        refreshing = True
    if refreshing:
        if col3.button("停止"):
            refreshing = False
    # 初始化数据
    cpu_data = []
    memory_data = []
    disk_data = []

    # 初始化图表
    resource_chart = line_chart({})

    # 初始化指标占位符
    cpu_metric = col1.empty()
    memory_metric = col2.empty()
    disk_metric = col3.empty()

    while refreshing:
        # 获取系统资源使用情况
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # 更新数据
        cpu_data.append(cpu_usage)
        memory_data.append(memory.percent)
        disk_data.append(disk.percent)

        # 更新指标
        cpu_metric.metric(label="CPU 使用率", value=f"{cpu_usage}%")
        memory_metric.metric(label="内存使用率", value=f"{memory.percent}%")
        disk_metric.metric(label="磁盘使用率", value=f"{disk.percent}%")

        # 更新图表
        resource_chart.line_chart({
            "CPU": cpu_data,
            "内存": memory_data,
            "磁盘": disk_data
        })

        # 限制数据点数量
        if len(cpu_data) > 60:  # 保留最近60个数据点
            cpu_data.pop(0)
            memory_data.pop(0)
            disk_data.pop(0)

        sleep(2)

with tab[1]:
    mongodb = text_area(
        label="请提交MongoDB语法",
        value=dict(),
        # height=400,
        key="text_area_1"
    )
    if (mongodb):
        try:
            mongodb = loads(mongodb)
            json_swap = list()
            for f1 in tiktok_raw.find(mongodb, {"_id": 0}):
                json_swap.append(f1)
            mongodb = 5
            column = list(columns(mongodb))
            for f1 in range(len(json_swap)):
                with column[f1 % mongodb]:
                    with popover(F'{json_swap[f1]["device"]}|{json_swap[f1]["type"]}'):
                        f1 = F"```json\n{dumps(json_swap[f1]["return"]["return"], indent=4, ensure_ascii=False)}\n```"
                        markdown(F"**查询结果：{str(dt.now())}**\n{f1}")
            # write(json_swap)
        except Exception as e:
            error(e)

with tab[2]:
    data_tab_2 = None
    if (device):
        data_tab_2 = multiselect(
            "请选择设备",
            device,
            default=None,
            key="multiselect_2"
        )
        javascript = text_area(
            label="请粘贴运行的**javascript**代码",
            value='print("测试");\ntoast("测试");',
            key="text_area_2"
        )
        markdown(
            F"---\n等待提交的javascript代码（代码预览区）\n```javascript\n{javascript}\n```"
        )
        if (data_tab_2 and javascript):
            javascript = {"data": javascript}
            for f1 in data_tab_2:
                f1.update(javascript)
        javascript = None
        if (button("提交", key="button_2_1")):
            try:
                mongo_write.insert_many(data_tab_2.copy())
                while not javascript:
                    javascript = mongo_read.find_one_and_delete(
                        dict(), {"_id": 0})
                    sleep(0.1)
                sleep(2)
                if (javascript and ["status", "send", "receive"] == list(javascript)):
                    if (javascript["status"]):
                        success("提交成功")
                        balloons()
                    else:
                        error("提交失败")
                        snow()
            except Exception as e:
                warning(e)
        if (button("获取", key="button_2_2")):
            javascript = mongo_read.find_one_and_delete(dict(), {"_id": 0})
            if (javascript and "data" in javascript):
                # write(javascript)
                text(
                    F'运行{"成功" if javascript["data"]["status"] else "失败"}：{dt.now()}')
                markdown(F'执行代码\n```javascript\n{javascript["data"]["code"]}\n```')

with tab[3]:
    data_tab_3 = None
    if (device):
        data_tab_3 = multiselect(
            "请选择设备",
            device,
            default=None,
            key="multiselect_3"
        )
        python = text_area(
            label="请粘贴运行的**python**代码",
            value='from os import popen\n_return_ = popen("dir").read()',
            key="text_area_3"
        )
        markdown(
            F"---\n等待提交的Python代码（代码预览区）\n```python\n{python}\n```"
        )
        if (data_tab_3 and python):
            python = {"data": {"code": python}}
            for f1 in data_tab_3:
                f1.update(python)
        # write(data_tab_3)
        if (button("提交", key="button_3_1")):
            try:
                mongo_write.insert_many(data_tab_3.copy())
                while not python:
                    python = mongo_read.find_one_and_delete(dict(), {"_id": 0})
                    sleep(0.1)
                sleep(2)
                if (python and ["status", "send", "receive"] == list(python)):
                    if (python["status"]):
                        success("提交成功")
                        balloons()
                    else:
                        error("提交失败")
                        snow()
            except Exception as e:
                warning(e)
        if (button("获取", key="button_3_2")):
            python = mongo_read.find_one_and_delete(dict(), {"_id": 0})
            if (python and "data" in python):
                # write(python["data"])
                text(
                    F'运行{"成功" if python["data"]["status"] else "失败"}：{dt.fromtimestamp(python["data"]["utc"])}')
                markdown(F'执行代码\n```python\n{python["data"]["code"]}\n```')
                markdown(F'执行结果\n```python\n{python["data"]["exec"]}\n```')

with tab[4]:
    if (device):
        data_tab_4 = multiselect(
            "请选择设备",
            device,
            default=None,
            key="multiselect_4"
        )
        exec_json = dumps(
            {
                "config": {
                    "browser_path": "C:/Program Files/Google/Chrome/Application/chrome.exe",
                    "debug_port": None,
                    "username": "mxlbbi",
                    "proxy": None,
                    "headless": False
                },
                "params": {
                    "launch": None,
                    "connect": None,
                    "get": {
                        "browser_link": "https://www.baidu.com/",
                        "time_delay": 5.0
                    },
                    "quit": None
                }
            }, indent=4, ensure_ascii=False)
        exec_json = text_area(
            label="请提交执行**json**规则",
            value=exec_json,
            height=400,
            key="text_area_4"
        )
        if (data_tab_4 and exec_json):
            for f1 in data_tab_4:
                f1.update(loads(exec_json))
            markdown(
                F"---\n等待提交的JSON配置文件（代码预览区）\n```json\n{dumps(data_tab_4, indent=4, ensure_ascii=False)}\n```"
            )
        if (button("提交", key="button_4_1")):
            try:
                mongo_write.insert_many(data_tab_4.copy())
                exec_json = None
                while not (exec_json and ["status", "send", "receive"] == list(exec_json)):
                    exec_json = mongo_read.find_one_and_delete(
                        dict(), {"_id": 0})
                    sleep(0.1)
                sleep(2)
                if (exec_json and ["status", "send", "receive"] == list(exec_json)):
                    if (exec_json["status"]):
                        success("提交成功")
                        balloons()
                    else:
                        error("提交失败")
                        snow()
            except Exception as e:
                warning(e)
        if (button("获取", key="button_4_2")):
            exec_json = mongo_read.find_one_and_delete(dict(), {"_id": 0})
            if (exec_json):
                # write(exec_json)
                tiktok_raw.insert_one(exec_json)
                text(
                    F'运行{"成功" if exec_json["return"]["status"] else "失败"}：{dt.now()}'
                )
                markdown(
                    F'执行配置\n```python\n{dumps(exec_json["return"]["args"], indent=4, ensure_ascii=False)}\n```')
                markdown(
                    F'执行结果\n```json\n{dumps(exec_json["return"]["return"], indent=4, ensure_ascii=False)}\n```')
