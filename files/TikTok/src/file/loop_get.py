from camoufox.sync_api import Camoufox
from browserforge.fingerprints import Screen
from playwright.sync_api import Browser, BrowserContext, Page, Locator, Response
import time

def create_context(user_data='default', proxy=None):
    # 初始化 Camoufox
    camoufox = Camoufox(
        os='windows',
        screen=Screen(max_width=1280, max_height=1200),  # 设置屏幕分辨率
        persistent_context=True,
        user_data_dir=f'user_data/{user_data}',
        config={
            'webrtc:ipv4': '',  # 防止 WebRTC 泄露真实IP
            'webrtc:ipv6': 'fe80::1',  # 防止 WebRTC 泄露真实IP
            'timezone': 'America/Los_Angeles'  # 设置时区
        },
        proxy={
            'server': proxy,  # 代理服务器
            # 'username': None,
            # 'password': None,
        } if proxy else None,
        i_know_what_im_doing=False,
        no_viewport=False,  # 不隐藏视口
        locale='zh-CN'  # 设置语言为中文
    )
    # 启动浏览器上下文
    context: BrowserContext = camoufox.start()
    return context

def main():
    # 创建浏览器上下文
    context = create_context()

    # 打开一个新的页面
    page: Page = context.new_page()

    # 使用 goto 方法打开网页
    page.goto("https://www.tiktok.com/login", timeout=30000)  # 超时30秒

    # 确保页面已加载并处理后才进行后续操作
    page.wait_for_load_state("networkidle")
    print("网页已打开")

    # 进行其他操作，例如截屏、查找元素等
    # ...

    # 保持浏览器打开一段时间（例如30秒）
    time.sleep(30)

    # 关闭页面和上下文
    page.close()
    context.close()

if __name__ == "__main__":
    main()