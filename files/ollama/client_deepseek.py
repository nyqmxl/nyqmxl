
import asyncio
from uuid import uuid1
from pyotp import TOTP
from ollama import Client
from base64 import b32encode
from json import loads, dumps
from datetime import datetime
from websockets.client import State
from websockets.asyncio.client import connect
from pymongo import MongoClient

database = MongoClient("mongodb://localhost:27017/")
db_write = database["MQ_deepseek"]["write"]
db_read = database["MQ_deepseek"]["read"]


def to_json(obj):
    """
    递归将对象转换为字典，只处理 dict 和 list 类型的值，其他类型直接保留
    """
    try:
        match obj:
            case dict():
                obj = {key: to_json(value) for key, value in obj.items()}
            case list():
                obj = [to_json(item) for item in obj]
            case _:
                obj = to_json(dict(obj))
    finally:
        return obj


def deepseek(messages=list()):
    return to_json(
        Client(host="http://localhost:11434").chat(
            model="deepseek-coder-v2:16b",
            messages=messages,
            stream=False  # 非流式响应
        )
    )


async def main():
    print("Deepseek-Coder-v2:16b消息队列服务器已启动... ")
    while True:
        messages = db_read.find_one_and_delete({}, {"_id": 0})
        if messages:
            print(
                F'收到 {messages["receive"][0]}:{messages["receive"][1]} 的消息：{dumps(messages["data"], ensure_ascii=False)}'
            )
            messages["data"] = deepseek(messages["data"])
            print(
                F'发送 {messages["receive"][0]}:{messages["receive"][1]} 的消息：{dumps(messages["data"]["message"], ensure_ascii=False)}'
            )
            db_write.insert_one(messages)


if __name__ == "__main__":
    asyncio.run(main())
