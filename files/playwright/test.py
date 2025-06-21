import asyncio
from playwright.async_api import Browser, BrowserContext, Page, Locator, Response
from browserforge.fingerprints import Screen
from camoufox.async_api import AsyncCamoufox as Camoufox


async def __browser__(**kwargs):
    if not kwargs:
        kwargs = {
            "user": "default",
            "no_viewport": False
        }
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


async def demo():
    # from pprint import pprint as print
    from json import dumps
    launcher = await __browser__()
    launcher = await launcher.start()
    # launcher = launcher.page[0]

    await launcher.goto(**{"url": "https://www.baidu.com"})
    await asyncio.sleep(**{"delay": 2})
    await launcher.close()
    input("Press Enter to close the device...")  # 等待用户输入


if __name__ == '__main__':
    asyncio.run(demo())
