from os import makedirs, getpid
from json import loads
from uuid import uuid4
from psutil import cpu_count, Process
from requests import Session
from datetime import datetime
from multiprocessing import Manager, Process as MPProcess, freeze_support
from concurrent.futures import ThreadPoolExecutor
from time import sleep

def proc_download_core(download_task):
    try:
        target_url = download_task
        file_name = f"{uuid4()}.{target_url.split('/')[-1]}.ts"
        with Session() as session:
            response = session.get(target_url, stream=True)
            if response.status_code != 200:
                time_str = str(datetime.now())
                print(f"{time_str} - 哎呀，文件搬不动呢。状态码：{response.status_code}")
                return False
            file_path = f"Download/{file_name}"
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=2**24):
                    file.write(chunk)
            time_str = str(datetime.now())
            # print(f"{time_str} - 嘿咻嘿咻，{file_name} 搬运成功咯！")
            return True
    except Exception as error:
        time_str = str(datetime.now())
        print(f"{time_str} - 呜呜，被给赶出来了。{error}")
        return False

def proc_execute_and_bind(core_id, shared_task_list, list_lock):
    Process().cpu_affinity([core_id])
    process_id = getpid()
    print(f"小奶萌 {process_id:<6}（工位：{core_id:<3}）报到，干活咯！")
    while True:
        current_tasks = list()
        while len(shared_task_list):
            with list_lock:
                try:
                    current_tasks.append(shared_task_list.pop(0))
                    sleep(0.01)
                except:
                    pass
        if current_tasks:
            print(f"小奶萌 {process_id:<6}（工位：{core_id:<3}）。这次需要干 {len(current_tasks)} 个活，冲冲冲！")
            with ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(proc_download_core, current_tasks)
        
        sleep(0.1)

def handle_task_config(config_core_id, shared_task_list, list_lock):
    Process().cpu_affinity([config_core_id])
    process_id = getpid()
    print(f"小管家 {process_id:<6}（工位：{config_core_id:<3}）到岗，分配任务咯！")
    while True:
        try:
            with list_lock:
                with open('code_tasks.json', 'r+') as config_file:
                    config_content = config_file.read()
                    if config_content:
                        makedirs("Download", exist_ok=True)
                        new_tasks = loads(config_content)
                        shared_task_list.extend(new_tasks)
                        time_str = str(datetime.now())
                        print(f"{time_str} - 小管家 {process_id:<6}（工位：{config_core_id:<3}）：新的任务清单来咯，本次追加了 {len(new_tasks)} 个任务！")
                        config_file.truncate(0)
        except Exception as error:
            print(f"读取任务单出错咯：{error}")
            sleep(5)
        sleep(0.1)

def main():
    makedirs("Download", exist_ok=True)
    freeze_support()
    with Manager() as manager:
        shared_task_list = manager.list()
        list_lock = manager.Lock()
        cpu_cores = cpu_count()
        print(f"哇哦！发现 {cpu_cores:3d} 个小奶萌。全员开工，效率起飞！")
        config_process = MPProcess(target=handle_task_config, args=(0, shared_task_list, list_lock))
        config_process.start()
        worker_processes = [MPProcess(target=proc_execute_and_bind, args=(core_id, shared_task_list, list_lock)) for core_id in range(1, cpu_cores)]
        for worker in worker_processes:
            worker.start()
        config_process.join()
        for worker in worker_processes:
            worker.join()

if __name__ == "__main__":
    main()