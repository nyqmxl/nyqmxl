

# from playwright.sync_api import Browser, BrowserContext, Page, Locator, Response
from browserforge.fingerprints import Screen
from camoufox.sync_api import Camoufox
from time import sleep


class Api:
    def __init__(self, **kwargs):
        if (not kwargs):
            kwargs = {
                "user": "default",
                # "screen": {
                #         "min_width": 1920,
                #         "max_width": 1920,
                #         "min_height": 1080,
                #         "max_height": 1080
                # },
                # "proxy": {
                #     "server": "socks5://127.0.0.1:10809",
                #     # "username": None,
                #     # "password": None,
                # },
                "no_viewport": False
            }

        self.kwargs = kwargs
        self.swap = None
        self.pointer_browser = None

    def call(Class=None, List=list()):
        from time import time
        swap_call = None
        for Dict in List:
            for f1 in Dict:
                try:
                    swap_exec = getattr(Class, f1, None)
                    if (callable(swap_exec) and "params" in Dict[f1]):
                        if (Dict[f1]["params"]):
                            swap_call = swap_exec(**Dict[f1]["params"].copy())
                        else:
                            swap_call = swap_exec()
                        swap_exec = callable(swap_exec)
                except BaseException as e:
                    # import traceback
                    # swap_call = traceback.format_exc()
                    swap_call = str(e)
                    swap_exec = False
                Dict[f1] = {
                    "utc": time(),
                    "params": Dict[f1]["params"],
                    "exec": swap_exec,
                    "res": swap_call
                }
                swap_call = None
        return {Class.__name__ if isinstance(Class, type) else Class.__class__.__name__: List}

    def delay(self, **kwargs):
        timeout = kwargs.get("timeout", 0.0)
        sleep(timeout)
        return timeout

    def demo(self, **kwargs):
        print(**kwargs)

    def __browser__(self, **kwargs):
        return Camoufox(
            os="windows",
            screen=Screen(
                **kwargs.get(
                    "screen",
                    {
                        "min_width": 1440,
                        "max_width": 1440,
                        "min_height": 900,
                        "max_height": 900
                    }
                )
            ),
            persistent_context=True,
            user_data_dir=f"data_user/{kwargs.get('user', 'default')}",
            config={
                "webrtc:ipv4": "",
                "webrtc:ipv6": "fe80::1",
                "timezone": "America/Los_Angeles"
            },
            proxy=kwargs.get("proxy", None),
            i_know_what_im_doing=False,
            no_viewport=kwargs.get("no_viewport", False),
            locale="zh-CN"
        )

    def browser(self, **kwargs):
        from time import time
        swap_exec = None
        self.pointer_browser = self.__browser__(**self.kwargs).start().pages[0]
        for f1 in kwargs.copy():
            try:
                swap_exec = getattr(self.pointer_browser, f1, None)
                if ("params" in kwargs[f1]):
                    print(kwargs[f1]["params"])
                    if (kwargs[f1]["params"]):
                        swap_call = swap_exec(**kwargs[f1]["params"])
                    else:
                        swap_call = swap_exec()
                    swap_exec = True
            except BaseException as e:
                swap_call = str(e)
                swap_exec = False
            kwargs[f1] = {
                "utc": time(),
                "params": kwargs[f1],
                "exec": swap_exec,
                "res": swap_call
            }
            swap_call = None
        return kwargs

    def launch(self):
        self.pointer_browser = self.__browser__(**self.kwargs).start().pages[0]

    def close(self):
        self.pointer_browser.close()

    def goto(self, **kwargs):
        self.pointer_browser.goto(**kwargs)
        return kwargs

    def test(self):
        self.pointer_browser
        page = self.pointer_browser.pages[0]  # 获取默认打开的唯一标签页

        data = getattr(page, "goto", None)(**{"url": "https://www.baidu.com"})
        data = getattr(page, "title", None)()


def demo():
    # from pprint import pprint as print
    from json import dumps
    launcher = Api()
    if (False):
        launcher.launch()  # 明确启动浏览器
        launcher.goto(**{"url": "https://www.devicescan.net/zh"})  # 访问页面
    else:
        if (True):
            launcher_data = launcher.call(
                [
                    {
                        "launch": {"params": None},
                        "goto": {"params": {"url": "https://www.devicescan.net/zh"}},
                        "delay": {"params": {"timeout": 2}},
                        "close": {"params": None}
                    },
                    {"delay": {"params": {"timeout": 3}}},
                    {
                        "launch": {"params": None},
                        "goto": {"params": {"url": "https://www.baidu.com"}},
                        "delay": {"params": {"timeout": 2}},
                        "close": {"params": None}
                    }
                ]
            )
        else:
            launcher_data = launcher.call(
                [
                    {
                        "browser": {
                            "params": {
                                "launch": {"params": None},
                                "goto": {"params": {"url": "https://www.baidu.com"}},
                                "close": {"params": None}
                            }
                        }
                    }
                ]
            )

        print(dumps(launcher_data, indent=4, ensure_ascii="UTF-8"))

    input("Press Enter to close the device...")  # 等待用户输入
    # launcher.close()  # 关闭浏览器


if __name__ == '__main__':
    demo()
    # try:
    #     print(weioru)
    # except:
    #     print("-" * 100)
    #     s = traceback.format_exc()
    # print(s)
