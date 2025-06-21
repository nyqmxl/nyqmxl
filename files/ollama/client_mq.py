from datetime import datetime
import asyncio
from uuid import uuid1
from pyotp import TOTP
from base64 import b32encode
from json import loads, dumps
from websockets.client import State
from websockets.asyncio.client import connect
from pymongo import MongoClient

database = MongoClient("mongodb://localhost:27017/")
db_write = database["MQ_deepseek"]["write"]
db_read = database["MQ_deepseek"]["read"]


async def ws():
    print(end="正在连接云端消息队列服务器... ")
    async with connect("ws://206.119.166.200:8500") as websocket:
        message = str(uuid1())[-12:]
        message = {
            "secret": message,
            "code": TOTP(b32encode(message.encode("UTF-8")).decode("UTF-8")).now(),
            "device": message,
            "type": "ai.deepseek.server"
        }
        await websocket.send(dumps(message, ensure_ascii=False))
        message = loads(await websocket.recv())
        print("成功！" if (message["verified"]) else "失败！")
        print(F"服务器返回信息：{message}")
        while websocket.state == State.OPEN:
            try:
                data_recv = loads(await asyncio.wait_for(websocket.recv(), timeout=0.5))
                data_swap = {
                    "时间": str(datetime.now()),
                    "消息": data_recv
                }
                print("收到消息 -> ", dumps(data_swap, ensure_ascii=False))
                db_read.insert_one(data_recv)
            except Exception as e:
                await asyncio.sleep(0.1)
            data_send = db_write.find_one_and_delete({}, {"_id": 0})
            if data_send:
                data_send["time"] = str(datetime.now())
                await websocket.send(dumps(data_send, indent=4, ensure_ascii=False))
                data_swap = {
                    "时间": str(datetime.now()),
                    "状态": loads(await websocket.recv()),
                    "消息": data_send
                }
                print("发送消息 -> ", dumps(data_swap, ensure_ascii=False))


if __name__ == "__main__":
    from datetime import datetime as d
    from time import sleep
    while True:
        try:
            asyncio.run(ws())
        except Exception as e:
            print(F"[{d.now()}]error:{e}")
            sleep(1)
