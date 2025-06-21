#!/usr/bin/env python
"""
WebSocket管理端配置

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
└─────────┘       └─────────┘       └─────────┘
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
    "type": "TikTok.Admin"
}
调用Call函数：
{
    "send": [
        "223.104.84.77",
        34080
    ],
    "receive": [
        "223.104.84.77",
        34079
    ],
    "device": "secret_key",
    "data": {
        "code": "print('1566')\nTrue"
    }
}
"""

from uuid import uuid1
from json import dumps, loads
from call_mfa import totp
from time import time, sleep
from websockets.sync.client import connect  # 使用同步的connect
from argparse import ArgumentParser
from os.path import basename

_return_ = None
data_config = [
    "ws://206.119.166.200:8500",
    {
        "secret": str(uuid1())[-12:],
        "code": totp(str(uuid1())[-12:])["code"],
        "device": str(uuid1())[-12:],
        "type": "TikTok.Admin"
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
    parser = ArgumentParser(description="WebSocket控制服务端配置", add_help=False)
    parser.prog = basename(__file__)  # 设置prog为当前文件名
    parser.add_argument("-h", "--help", action="help",
                        default=None, help="显示帮助信息并退出")
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

    示例:
        >>> @ws_connect("ws://example.com:8500", {"secret": "key", "code": "123456", "device": "device_id", "type": "TikTok.Admin"})
        >>> def example_function(websocket, auth_response):
        >>>     # 处理WebSocket通信
    """
    def decorator(func):
        def wrapper():
            with connect(uri) as websocket:  # 使用同步的with连接
                websocket.send(dumps(auth_message, ensure_ascii=False))  # 同步发送
                auth_response = loads(websocket.recv())  # 同步接收
                # print(auth_response)
                updated_auth_message = {
                    "send": auth_response["send"],
                    "receive": auth_response["receive"],
                    "device": auth_message["device"]
                }
                return func(websocket, updated_auth_message)
        return wrapper
    return decorator

@ws_connect(data_config[0], data_config[1])
def ws_function(websocket, auth_message):
    """
    处理WebSocket消息循环和业务逻辑。

    此函数通过消息循环接收服务器消息，调用call_browser.main函数处理消息，并将结果发送回服务器。

    Args:
        websocket: WebSocket连接对象。
        auth_message: 更新后的认证消息。

    示例:
        >>> ws_function()
    """
    def ws_loop():
        while True:  # 同步循环
            try:
                data_json = websocket.recv()  # 同步接收
                data_json = loads(data_json)
                if "data" in data_json and "code" in data_json["data"]:
                    data_json["data"] = {
                        "utc": time(),
                        "status": True,
                        "code": data_json["data"]["code"] or None,
                        "exec": None
                    }
                    try:
                        data_json["data"]["exec"] = str(
                            data_json["data"]["code"])
                        exec(data_json["data"]["exec"], globals())
                        data_json["data"]["exec"] = _return_
                    except Exception as e:
                        data_json["data"]["status"] = False
                        data_json["data"]["exec"] = str(e)
            except Exception as e:
                data_json = {
                    "utc": time(),
                    "status": False,
                    "code": data_json,
                    "exec": str(e)
                }
            websocket.send(dumps(data_json, ensure_ascii=False))  # 同步发送
    try:
        print(F"[{time()}]:开始通信...")
        ws_loop()
        print(F"[{time()}]:结束通信...")
    except Exception as e:
        print(F"[{time()}]:结束通信...，错误原因：{e}")

if __name__ == "__main__":
    """
    模块入口，解析命令行参数并启动WebSocket连接。

    示例:
        >>> python network_client.py --host 206.119.166.200 --port 8500 --secret "secret_key" --code "158524" --device "device_id" --type "TikTok.Server"
    """
    print(data_config)
    ws_cmd()
    ws_function()  # 直接调用同步函数