#!/usr/bin/env python
"""
WebSocket客户端端配置

此模块实现了与TikTok服务端的WebSocket通信功能，能够发送认证信息并接收消息。
通过命令行参数自定义服务器地址、端口、密钥、认证码、设备标识和类型，灵活地与不同的TikTok服务端进行通信。

模块功能：
- 发送认证信息，包括密钥、认证码、设备标识和类型。
- 通过消息循环接收服务器消息并进行处理。
- 支持自定义服务器地址和端口。
- 支持自定义密钥、认证码、设备标识和类型。

示例用法（使用默认参数值）：
python network_client.py --host 206.119.166.200 --port 8500 --secret "从data_config获取" --code "从data_config获取" --device "从data_config获取" --type "TikTok.Server"

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
调用Call函数：
{
    "send": [
        "111.55.204.60",
        44523
    ],
    "receive": [
        "111.55.204.60",
        54224
    ],
    "device": "b8d4bc91c784",
    "config": {
        "browser_path": "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "debug_port": null,
        "username": "mxlbbi",
        "proxy": null,
        "headless": false
    },
    "params": {
        "launch": null,
        "connect": null,
        "get": {
            "browser_link": "https://www.baidu.com/",
            "time_delay": 5.0
        }
    }
}
"""

import asyncio
from os.path import basename
from time import time
from uuid import uuid1
from json import dumps, loads
from argparse import ArgumentParser
from call_mfa import totp
from call_browser import main
from websockets.client import State
from websockets.asyncio.client import connect

# 定义全局列表变量data_config，存储WebSocket配置参数
data_config = [
    "ws://206.119.166.200:8500",  # WebSocket URI
    {  # 初始认证消息
        "secret": str(uuid1())[-12:],
        "code": totp(str(uuid1())[-12:])["code"],
        "device": str(uuid1())[-12:],
        "type": "TikTok.Client"
    }
]


def ws_cmd():
    """
    接收命令行参数并更新data_config。

    此函数使用argparse模块解析命令行参数，更新全局变量data_config中的服务器地址、端口、密钥、认证码、设备标识和类型。
    支持的参数包括：
    -h, --help     显示帮助信息并退出
    --host         服务器主机地址
    --port         服务器端口号
    --secret       自定义密钥
    --code         自定义认证码
    --device       自定义设备标识
    --type         自定义类型

    返回值：
        dict: 包含命令行参数值的字典。
    """
    parser = ArgumentParser(description="WebSocket控制服务端配置", add_help=False)
    parser.prog = basename(__file__)  # 设置prog为当前文件名
    parser.add_argument(
        "-h", "--help", action="help",
        default=None, help="显示帮助信息并退出"
    )
    parser.add_argument("--host", metavar="     HOST", help="服务器主机地址")
    parser.add_argument("--port", type=int, metavar="     PORT", help="服务器端口号")
    parser.add_argument("--secret", metavar="   SECRET", help="自定义密钥")
    parser.add_argument("--code", metavar="     CODE", help="自定义认证码")
    parser.add_argument("--device", metavar="   DEVICE", help="自定义设备标识")
    parser.add_argument("--type", metavar="     TYPE", help="自定义类型")
    args = parser.parse_args()
    args.host and args.port and data_config.__setitem__(
        0, f"ws://{args.host}:{args.port}")
    args.secret and data_config[1].__setitem__("secret", args.secret)
    args.code and data_config[1].__setitem__("code", args.code)
    args.device and data_config[1].__setitem__("device", args.device)
    args.type and data_config[1].__setitem__("type", args.type)
    return {
        "host": args.host,
        "port": args.port,
        "secret": args.secret,
        "code": args.code,
        "device": args.device,
        "type": args.type
    }


def ws_connect(uri, auth_message):
    """
    装饰器工厂，用于创建WebSocket连接并发送认证信息。

    Args:
        uri (str): WebSocket服务器的URI。
        auth_message (dict): 认证消息，包含secret、code、device和type。

    Returns:
        decorator: 一个装饰器函数，用于包装处理WebSocket通信的函数。
    """
    def decorator(func):
        async def wrapper():
            async with connect(uri) as websocket:
                await websocket.send(dumps(auth_message, ensure_ascii=False))
                auth_response = loads(await websocket.recv())
                updated_auth_message = {
                    "send": auth_response["send"],
                    "receive": auth_response["receive"],
                    "device": auth_message["device"]
                }
                if websocket.state == State.OPEN:
                    return await func(websocket, updated_auth_message)
        return wrapper
    return decorator


@ws_connect(data_config[0], data_config[1])
async def ws_function(websocket, auth_message):
    """
    处理WebSocket消息循环和业务逻辑。

    此函数通过消息循环接收服务器消息，调用call_browser.main函数处理消息，并将结果发送回服务器。

    Args:
        websocket: WebSocket连接对象。
        auth_message: 更新后的认证消息。
    """
    async def ws_loop():
        while websocket.state == State.OPEN:
            data_main = await websocket.recv()
            print(data_main)
            try:
                data_main = loads(data_main)
                data_main.update(
                    {"return": main(data_main["config"], data_main["params"])})
            except Exception as e:
                data_main = {
                    "utc": time(),
                    "status": True,
                    "code": data_main,
                    "exec": str(e)
                }
            await websocket.send(dumps(data_main, ensure_ascii=False))
            await websocket.recv()
    try:
        print(F"[{time()}]:开始通信...")
        await ws_loop()
        print(F"[{time()}]:结束通信...")
    except Exception as e:
        print(F"[{time()}]:结束通信...，错误原因：{e}")


if __name__ == "__main__":
    print(data_config)
    ws_cmd()
    asyncio.run(ws_function())
