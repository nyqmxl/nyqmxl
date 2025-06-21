#!/usr/bin/env python
"""
WebSocket服务端配置

此模块实现了与TikTok服务端的WebSocket通信功能，能够发送认证信息并接收消息。
通过命令行参数自定义服务器地址、端口、密钥、认证码、设备标识和类型，灵活地与不同的TikTok服务端进行通信。

模块功能：
- 发送认证信息，包括密钥、认证码、设备标识和类型。
- 通过消息循环接收服务器消息并进行处理。
- 支持自定义服务器地址和端口。
- 支持自定义密钥、认证码、设备标识和类型。

示例用法（使用默认参数值）：
python_client network.py --host 206.119.166.200 --port 8500 --secret "从data_config获取" --code "从data_config获取" --device "从data_config获取" --type "TikTok.Server"

设计架构图：
┌──────────┐
│ External │
│  Clients │
└───┬──────┘
    │DB
    ▼
┌─────────┐       ┌─────────┐       ┌─────────┐
│  Server │       │  Admin  │       │  Client │
└───┬─────┘       └────┬────┘       └───┬─────┘
    │Call              │Call            │Call
    ▼                  ▼                ▼
┌───────────────────────────────────────────────┐
│              Message Queue (MQ)               │
└───────────────────────────────────────────────┘

注意：
- 本模块依赖于websockets库进行WebSocket通信。
- 需要安装相关依赖库才能正常运行。
- 如果解析TikTok链接失败，可能是由于网络原因或链接本身的问题，请检查网络连接和链接合法性。

测试数据：
接入验证：
{
    "secret": "secret_key",
    "code": "158524",
    "device": "secret_key",
    "type": "TikTok.Server"
}
调用Call函数：{"$query": {}}
"""

from time import time
from uuid import uuid1
from json import dumps, loads
from call_mfa import totp
from pymongo import MongoClient
from argparse import ArgumentParser
from websockets.sync.client import connect
from websockets import State

data_config = [
    "ws://206.119.166.200:8500",
    {
        "secret": str(uuid1())[-12:],
        "code": totp(str(uuid1())[-12:])["code"],
        "device": str(uuid1())[-12:],
        "type": "TikTok.Server"
    }
]

mongo = MongoClient("mongodb://localhost:27017/")
mongo_read = mongo["app_cache"][F"tiktok_read_{str(uuid1())[-12:]}"]
mongo_write = mongo["app_cache"][F"tiktok_write_{str(uuid1())[-12:]}"]


def ws_cmd():
    """
    解析命令行参数并更新全局配置。

    此函数使用 `argparse` 模块解析命令行参数，根据用户输入更新 `data_config` 中的服务器地址、端口、密钥、认证码、设备标识和类型。
    如果命令行参数未提供某些值，则保留 `data_config` 中的默认值。

    支持的参数包括：
    - `--host`：服务器主机地址（默认：`206.119.166.200`）
    - `--port`：服务器端口号（默认：`8500`）
    - `--secret`：自定义密钥
    - `--code`：自定义认证码
    - `--device`：自定义设备标识
    - `--type`：自定义类型（默认：`TikTok.Server`）

    Returns:
        dict: 包含命令行参数值的字典，键包括 `host`、`port`、`secret`、`code`、`device`、`type`。

    示例：
        >>> ws_cmd()
        {
            "host": "206.119.166.200",
            "port": 8500,
            "secret": "secret_key",
            "code": "158524",
            "device": "device_id",
            "type": "TikTok.Server"
        }
    """
    parser = ArgumentParser(description="WebSocket控制服务端配置")
    parser.add_argument("--host", default="206.119.166.200", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8500, help="服务器端口号")
    parser.add_argument("--secret", help="自定义密钥")
    parser.add_argument("--code", help="自定义认证码")
    parser.add_argument("--device", help="自定义设备标识")
    parser.add_argument("--type", default="TikTok.Server", help="自定义类型")
    args = parser.parse_args()

    data_config[0] = f"ws://{args.host}:{args.port}"
    data_config[1].update({
        "secret": args.secret or data_config[1]["secret"],
        "code": args.code or data_config[1]["code"],
        "device": args.device or data_config[1]["device"],
        "type": args.type
    })
    return vars(args)


def ws_connect(uri, auth_message):
    """
    装饰器工厂，用于创建 WebSocket 连接并发送认证信息。

    此装饰器工厂返回一个装饰器，用于包装处理 WebSocket 通信的函数。
    被装饰的函数将接收一个 WebSocket 连接对象和更新后的认证消息。

    Args:
        uri (str): WebSocket 服务器的 URI（格式：`ws://host:port`）。
        auth_message (dict): 认证消息，包含以下键：
            - `secret` (str): 密钥
            - `code` (str): 认证码
            - `device` (str): 设备标识
            - `type` (str): 类型（如 `TikTok.Server`）

    Returns:
        decorator: 一个装饰器函数，用于包装处理 WebSocket 通信的函数。

    示例:
        >>> @ws_connect("ws://example.com:8500", {"secret": "key", "code": "123456", "device": "device_id", "type": "TikTok.Admin"})
        >>> def example_function(websocket, updated_auth_message):
        >>>     # 处理 WebSocket 通信
        >>>     print(updated_auth_message["send"])
    """
    def decorator(func):
        def wrapper():
            with connect(uri) as websocket:
                websocket.send(dumps(auth_message, ensure_ascii=False))
                auth_response = loads(websocket.recv())
                updated_auth_message = {
                    "send": auth_response["send"],
                    "receive": auth_response["receive"],
                    "device": auth_message["device"]
                }
                func(websocket, updated_auth_message)
        return wrapper
    return decorator


@ws_connect(data_config[0], data_config[1])
def ws_function(websocket, auth_message):
    """
    处理 WebSocket 消息循环和业务逻辑。

    此函数通过循环接收服务器消息，并与 MongoDB 进行交互：
    1. 从 MongoDB 的 `tiktok_write` 集合读取消息并发送到服务器。
    2. 接收服务器消息并存储到 MongoDB 的 `tiktok_read` 集合。
    3. 处理不同类型的消息（列表、字典、整数）并进行相应的存储操作。

    Args:
        websocket: WebSocket 连接对象。
        auth_message (dict): 更新后的认证消息，包含以下键：
            - `send` (list): 发送地址 `[host, port]`
            - `receive` (list): 接收地址 `[host, port]`
            - `device` (str): 设备标识

    Returns:
        None

    示例:
        >>> ws_function()
        # 消息循环处理
    """
    auth_message.update(
        {
            "send": auth_message["receive"],
            "receive": auth_message["send"]
        }
    )
    while websocket.state == State.OPEN:
        try:
            data_write = mongo_write.find_one_and_delete(dict(), {"_id": 0})
            if data_write:
                data_write = dumps(data_write, ensure_ascii=False)
                websocket.send(data_write)
            data_read = websocket.recv(timeout=1.0)
            data_read = loads(data_read)
            match data_read:
                case list():
                    mongo_read.insert_many(data_read)
                case dict():
                    mongo_read.insert_one(data_read)
                case int():
                    data_read = [
                        loads(websocket.recv(timeout=3.0)) for _ in range(data_read)
                    ]
                    for f1 in data_read:
                        f1["send"] = auth_message["send"]
                    data_read = {"query": data_read}
                    mongo_read.insert_one(data_read)
        except Exception as e:
            # print(F"发生错误：{e}")
            pass


if __name__ == "__main__":
    """
    模块入口，解析命令行参数并启动 WebSocket 连接。

    此函数执行以下步骤：
    1. 打印初始配置。
    2. 解析命令行参数并更新配置。
    3. 启动 WebSocket 通信。
    4. 捕获键盘中断信号，优雅地关闭资源。

    示例:
        >>> python network_client.py --host 206.119.166.200 --port 8500 --secret "secret_key" --code "158524" --device "device_id" --type "TikTok.Server"
    """
    print(data_config)
    print(F"数据库：tiktok_read_{str(uuid1())[-12:]}")
    print(F"数据库：tiktok_write_{str(uuid1())[-12:]}")
    ws_cmd()
    print(F"[{time()}]:开始通信...")
    while True:
        ws_function()
    print(F"[{time()}]:结束通信...")
    mongo.close()
