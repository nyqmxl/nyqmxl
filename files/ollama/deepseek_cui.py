
import asyncio
from uuid import uuid1
from pyotp import TOTP
from base64 import b32encode
from json import loads, dumps
from websockets.sync.client import connect


def deepseek(data=list()):
    with connect("ws://206.119.166.200:8500") as websocket:
        message = str(uuid1())[-12:]
        message = {
            "secret": message,
            "code": TOTP(b32encode(message.encode("UTF-8")).decode("UTF-8")).now(),
            "device": message,
            "type": "ai.deepseek.client"
        }
        websocket.send(dumps(message, ensure_ascii=False))
        message = loads(websocket.recv())
        query = {"$query": {"parameters.type": "ai.deepseek.server"}}
        websocket.send(dumps(query, ensure_ascii=False))
        query = websocket.recv()
        if (bool(query)):
            query = loads(websocket.recv())
        message = {
            "send": message["receive"],
            "receive": query["receive"],
            "type": "ai.deepseek.client",
            "data": data
        }
        websocket.send(dumps(message, ensure_ascii=False))
        query = {
            "状态": loads(websocket.recv()),
            "消息": message
        }
        print("发送：", dumps(query, ensure_ascii=False))
        print("-" * 120)
        print("接收：", websocket.recv())


def main():
    from datetime import datetime as d
    from os import system as sys, name
    if (name == "nt"):
        sys("title DeepSeek客户端（测试版） && color F0 && mode con cols=150 lines=30")
        sys("pip install websockets pyotp")
    print("环境配置完成...")
    while True:
        print("#" * 120)
        print(F"[{str(d.now())}] 你好！有什么可以帮助您？")
        data = [
            {"role": "assistant", "content": "你好！有什么可以帮助您？"},
            {"role": "user", "content": input(
                F"[{str(d.now())}] 请键入问题并按下回车发送 -> ")}
        ]
        print("-" * 120)
        deepseek(data)


if __name__ == "__main__":
    main()
