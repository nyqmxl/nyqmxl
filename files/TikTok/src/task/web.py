'''
pip install pymongo streamlit websockets pyotp numpy opencv-python selenium pillow pyautogui psutil urllib3 openpyxl pandas

'''
from subprocess import Popen
from datetime import datetime as dt
from json import loads, dumps
from streamlit import *
from uuid import uuid1
from time import sleep
from task import *
from os import makedirs, walk, system, chdir, getcwd, remove
from os.path import exists, dirname, abspath, isfile
from pandas import read_excel

current_script_dir = dirname(abspath(__file__))
chdir(current_script_dir)


def web():
    set_page_config(
        page_title="TikTok任务页",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="auto"
    )

    title("欢迎使用：TikTok可视化任务管理！")
    markdown(
        F"【**{str(dt.now())[:-7]}**】 设备 “{str(uuid1())[-12:]}” 在 “{getcwd()}” 下工作！")

    tab = list(tabs(["说明", "状态", "添加", "管理", "文件"]))

    with tab[0]:
        if isfile("说明.md"):
            with open("说明.md", "r", encoding="UTF-8") as pf:
                markdown(pf.read())

    with tab[1]:
        import psutil
        markdown("## 监控运行")
        refreshing = False  # 初始状态为不刷新

        col1, col2, col3 = columns(3)
        if col1.button("刷新"):
            rerun()
        if col2.button("开始"):
            refreshing = True
        if refreshing:
            if col3.button("停止"):
                refreshing = False

        cpu_data = []
        memory_data = []
        disk_data = []

        # 创建可折叠区域
        with expander("监控数据", expanded=True):
            # 在可折叠区域内创建指标和图表的占位符
            col_metric1, col_metric2, col_metric3 = columns(3)
            cpu_metric = col_metric1.empty()
            memory_metric = col_metric2.empty()
            disk_metric = col_metric3.empty()
            resource_chart = empty()

        with expander("运行状态", expanded=False):
            column_path = columns(2)
            image1 = column_path[0].empty()
            image2 = column_path[1].empty()

        while refreshing:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

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

            if len(cpu_data) > 60:  # 保留最近60个数据点
                cpu_data.pop(0)
                memory_data.pop(0)
                disk_data.pop(0)

            # 更新图片
            if isfile("images.png"):
                image1.image("images.png", caption=F"{str(dt.now())[:-7]} 运行正常...")
            if isfile("error.png"):
                image2.image("error.png", caption=F"{str(dt.now())[:-7]} 运行错误...")

            sleep(1)

    with tab[2]:
        tab_config = {
            "browser_path": ["浏览器路径", "C:/Program Files/Google/Chrome/Application/chrome.exe"],
            "debug_port": ["浏览器端口", 9222],
            "username": ["数据用户名", "test"],
            "proxy": ["代理地址", None],
            "headless": ["无头请求", False]
        }
        tab_data = {
            "launch": ["启动浏览器", None],
            "connect": ["连接浏览器", None],
            "get": ["打开标签页", None],
            "reg": ["注册用户", None],
            "login": ["登入用户", None],
            "info": ["用户信息", None],
            "post_video": ["上传视频", None],
            "get_list": ["获取信息", None],
            "search_videos": ["添加评论", None],
            "post_comment": ["发送评论", None],
            "quit": ["关闭浏览器", None],
        }
        markdown("## 配置参数")
        with expander("点击打开:配置参数", expanded=False):
            for f1 in tab_config.copy():
                column = list(columns([2, 8]))
                f1v_bool = column[0].checkbox(tab_config[f1][0], value=True)
                match f1:
                    case "headless":
                        tab_config[f1] = column[1].selectbox(
                            label=tab_config[f1][0],
                            options=[False, True],
                            key=f1,
                            label_visibility="collapsed"
                        )
                    case "debug_port":
                        tab_config[f1] = column[1].text_input(
                            tab_config[f1][0], tab_config[f1][1], key=f1,
                            label_visibility="collapsed"
                        )
                        tab_config[f1] = int(tab_config[f1])
                    case _:
                        tab_config[f1] = column[1].text_input(
                            tab_config[f1][0], tab_config[f1][1], key=f1,
                            label_visibility="collapsed"
                        )
                if (not f1v_bool):
                    del tab_config[f1]
        markdown("---")
        markdown("## 配置参数")
        with expander("点击打开:配置参数"):
            for f1 in tab_data.copy():
                markdown("---")
                column = list(columns(5))
                f1v_bool = column[0].checkbox(tab_data[f1][0], value=False)
                if (f1v_bool):
                    match f1:
                        case "launch":
                            tab_data["launch"] = None
                        case "connect":
                            tab_data["connect"] = None
                        case "get":
                            tab_data["get"] = {
                                "browser_link": column[1].text_input(
                                    label="打开连接",
                                    key="browser_link"
                                ),
                                "time_delay": float(
                                    column[2].text_input(
                                        label="等待时间",
                                        value=3.0,
                                        key="browser_time_delay"
                                    )
                                ),
                            }
                        case "reg":
                            tab_data["reg"] = {
                                "user": column[1].text_input(label="用户名", key="reg_user"),
                                "passwd": column[2].text_input(label="密码", key="reg_passwd")
                            }
                        case "login":
                            tab_data["login"] = {
                                "user": column[1].text_input(label="用户名", key="login_user"),
                                "passwd": column[2].text_input(label="密码", key="login_passwd")
                            }
                        case "info":
                            post_paths = "files"
                            if not exists(post_paths):
                                makedirs(post_paths)
                            post_paths = [
                                f"./{root}/{file}" for root, dirs,
                                files in walk(post_paths) for file in files
                            ]
                            tab_data["info"] = {
                                "path": column[1].selectbox(label="头像", options=post_paths, key="info_path"),
                                "user": column[2].text_input(label="用户名", key="info_user"),
                                "name": column[3].text_input(label="姓名", key="info_name"),
                                "bio": column[4].text_input(label="个人简介", key="info_bio")
                            }
                        case "post_video":
                            post_paths = "files"
                            if not exists(post_paths):
                                makedirs(post_paths)
                            post_paths = [
                                f"./{root}/{file}" for root, dirs,
                                files in walk(post_paths) for file in files
                            ]
                            tab_data["post_video"] = {
                                "file_path": column[1].selectbox(label="视频路径", options=post_paths, key="video_path"),
                                "video_description": column[2].text_input(label="视频描述", key="video_description"),
                                "source_comment": column[3].text_input(label="视频评论", key="video_comment")
                            }
                        case "get_list":
                            tab_data["get_list"] = {
                                "parent": column[1].text_input(
                                    label="父容器",
                                    value="/html/body",
                                    key="xpath_parent"
                                ),
                                "child": column[2].text_input(
                                    label="子容器",
                                    value="//div[@data-e2e='search_video-item']",
                                    key="xpath_child"
                                )
                            }
                        case "search_videos":
                            tab_data["search_videos"] = {
                                "source_comment": column[1].text_input(
                                    label="添加评论",
                                    value="jinyu_tiktok_001",
                                    key="search_videos"
                                )
                            }
                        case "post_comment":
                            tab_data["post_comment"] = {
                                "source_comment": column[1].text_input(
                                    label="发表评论",
                                    value="jinyu_tiktok_001",
                                    key="post_comment"
                                )
                            }
                        case "quit":
                            tab_data["quit"] = None
                        case _:
                            pass
                else:
                    del tab_data[f1]
            markdown("---")
        markdown("---")
        markdown("## 保存文件")
        with expander("点击打开:保存文件"):
            st_paths = "config"
            if not exists(st_paths):
                makedirs(st_paths)
            markdown("### 配置参数")
            json(tab_config)
            column = list(columns([4, 1]))
            st_paths = column[0].text_input(
                label="请输入文件名",
                value=str(),
                label_visibility="collapsed",
                key="tab_config"
            )
            if (column[1].button("保存参数") and st_paths):
                with open(F"./config/[config]{st_paths}.json", "w", encoding="UTF-8") as pf:
                    pf.write(dumps(tab_config, indent=4, ensure_ascii=False))
                balloons()
            markdown("### 配置任务")
            json(tab_data)
            column = list(columns([4, 1]))
            st_paths = column[0].text_input(
                label="请输入文件名",
                value=str(),
                label_visibility="collapsed",
                key="tab_data"
            )
            if (column[1].button("保存任务") and st_paths):
                with open(F"./config/[params]{st_paths}.json", "w", encoding="UTF-8") as pf:
                    pf.write(dumps(tab_data, indent=4, ensure_ascii=False))
                balloons()

    with tab[3]:
        config_paths = "config"
        config_swap = dict()
        if not exists(config_paths):
            makedirs(config_paths)
        markdown("## 管理配置文件")
        with expander("配置文件", expanded=False):
            config_swap = [
                f"./{root}/{file}" for root, dirs,
                files in walk(config_paths) for file in files
            ]
            column_path = columns(3)
            config_swap = {
                f12: column_path[f11 % len(column_path)].checkbox(f12)
                for f11, f12 in enumerate(config_swap)
            }
        for f1 in config_swap.copy():
            if (not config_swap[f1]):
                del config_swap[f1]
        task_data = {"config": dict(), "params": list()}
        config_swap = list(config_swap)
        for f1 in list(config_swap):
            if ("[config]" in f1):
                try:
                    with open(f1, "r", encoding="UTF-8") as pf:
                        f1 = pf.read()
                    f1 = loads(f1)
                except Exception as e:
                    warning(F"本次添加跳过，请检查配置文件格式。{f1}")
                    continue
                task_data["config"] = f1
            if ("[params]" in f1):
                try:
                    with open(f1, "r", encoding="UTF-8") as pf:
                        f1 = pf.read()
                    f1 = loads(f1)
                except Exception as e:
                    warning(F"本次添加跳过，请检查配置文件格式。{f1}")
                    continue
                task_data["params"].append(f1)
            if ("[task]" in f1 or "[done]" in f1):
                try:
                    with open(f1, "r", encoding="UTF-8") as pf:
                        f1 = pf.read()
                    f1 = loads(f1)
                except Exception as e:
                    warning(F"本次添加跳过，请检查配置文件格式。{f1}")
                    continue
                task_data = f1
        with expander("编辑参数", expanded=False):
            task_data = dumps(task_data, indent=4, ensure_ascii=False)
            task_data = loads(
                text_area(
                    label="编辑参数",
                    value=task_data,
                    height=len(task_data.split("\n")) * 22 + 0X20,
                    label_visibility="collapsed"
                )
            )
        with expander("浏览参数", expanded=True):
            task_data = dumps(task_data, indent=4, ensure_ascii=False)
            code(task_data, language="json")
        column_button = columns([3, 1, 1, 1, 1, 1])
        file_name = column_button[0].text_input(
            label="请输入文件名：",
            label_visibility="collapsed"
        )

        if (column_button[1].button("生成配置", key="tab3_config") and file_name):
            with open(F"./{config_paths}/[task]{file_name}", "w", encoding="UTF-8") as pf:
                pf.write(task_data)
        if (column_button[2].button("运行任务", key="tab3_task")):
            for f1 in config_swap:
                Popen(["python", "task.py", "--config", f1])
                toast(F"提交 {f1} 任务", icon="🎉")
        if (column_button[3].button("删除文件", key="tab3_del")):
            for f1 in config_swap:
                remove(f1)
            sleep(0.5)
            rerun()
        if (column_button[4].button("更新文件", key="tab3_update")):
            rerun()
        if (column_button[5].button("外部编辑", key="tab3_edit")):
            for f1 in config_swap:
                try:
                    Popen(["cmd", "/k", f1])
                    toast(F"文件 {f1} 已打开")
                except Exception as e:
                    warning(F"文件路径：{f1}，{e}")

    with tab[4]:
        markdown("## 文件管理")
        markdown("---")
        markdown("### 上传文件")
        uploaded_files = file_uploader(
            label="上传文件",
            accept_multiple_files=True,
            label_visibility="collapsed",
            help="支持多个文件上传，上传后文件将储存在files目录下。"
        )
        file_paths = "files"
        if not exists(file_paths):
            makedirs(file_paths)
        for uploaded_file in uploaded_files:
            with open(F"./{file_paths}/{uploaded_file.name}", "wb") as pf:
                pf.write(uploaded_file.read())
            uploaded_file.close()
        markdown("---")
        markdown("### 管理目录")
        config_swap = list()
        with expander("文件目录", expanded=False):
            column_path = columns(4)
            config_swap = [
                f"./{root}/{file}" for root, dirs,
                files in walk(file_paths) for file in files
            ]
            config_swap = {
                f12: column_path[f11 % len(column_path)].checkbox(f12)
                for f11, f12 in enumerate(config_swap)
            }
            for f1 in config_swap.copy():
                if (not config_swap[f1]):
                    del config_swap[f1]
            config_swap = list(config_swap)

        column_button = columns(8)
        if (column_button[1].button("更新文件", key="tab4_update")):
            rerun()
        if (column_button[0].button("删除文件", key="tab4_del")):
            for f1 in config_swap:
                remove(f1)
            sleep(0.5)
            rerun()
        if (config_swap):
            markdown("---")
            markdown("### 预览界面")
            column_path = columns(4)
            for f11, f12 in enumerate(config_swap):
                try:
                    try:
                        column_path[f11 % 4].dataframe(read_excel(f12))
                        continue
                    except:
                        pass
                    try:
                        column_path[f11 % 4].image(f12)
                        continue
                    except:
                        pass
                    try:
                        column_path[f11 % 4].video(f12)
                        continue
                    except:
                        pass

                except Exception as e:
                    warning(e)


if __name__ == "__main__":
    web()
