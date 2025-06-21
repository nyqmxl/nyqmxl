# pip install --upgrade pip setuptools wheel pymongo streamlit psutil && streamlit run mq_web.py

import pandas as pd
from pytz import timezone
from time import sleep, time
from psutil import *
from streamlit import *
from pymongo import MongoClient
from datetime import datetime as dt
from json import dumps

dbs = 'mongodb://127.0.0.1:27017'
dbs = MongoClient(dbs)
db_mq = dbs["mq_server"]["mq_data"]
db_type = dbs["mq_server"]["device_info"]
db_log = dbs["mq_server"]["log_records"]


set_page_config(
    page_title="消息队列",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': "https://github.com/nyqmxl",
        'Report a bug': "https://github.com/nyqmxl",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)


def tab(db_data):
    data_json = list()
    data_list = db_data.find({}, {"_id": 0}).limit(100000)
    for f1 in data_list:
        f1 = {f2k: dumps(f2v, ensure_ascii=False) if type(
            f2v) != str else f2v for f2k, f2v in f1.items()}
        data_json.append(f1)
    data_list = pd.DataFrame(data_json)
    dataframe(data_list)


def msg():

    title(F"缓存服务器信息预览 {str(dt.now(timezone('Asia/Shanghai')))[:-10]}")
    col = list(columns(3))
    col[0].metric(
        label="CPU",
        value=F"{cpu_percent(interval=1)}%",
        # delta=str(dt.now())[:-7]
    )
    col[0].metric(
        label="缓存",
        value=db_mq.count_documents({}),
        # delta=str(dt.now())[:-7]
    )
    col[1].metric(
        label="RAM",
        value=F"{virtual_memory().percent}%",
        # delta=str(dt.now())[:-7]
    )
    col[1].metric(
        label="设备",
        value=db_type.count_documents({}),
        # delta=str(dt.now())[:-7]
    )
    col[2].metric(
        label="ROM",
        value=F"{disk_usage('/').percent}%",
        # delta=str(dt.now())[:-7]
    )
    col[2].metric(
        label="日志",
        value=db_log.count_documents({}),
        # delta=str(dt.now())[:-7]
    )

    with popover("设备信息", use_container_width=True):
        tab(db_type)
    with popover("日志记录", use_container_width=True):
        tab(db_log)
    with popover("缓存数据", use_container_width=True):
        tab(db_mq)

    if (checkbox("自动刷新")):
        rerun()


try:
    msg()
except Exception as e:
    error(str(e))

dbs.close()
