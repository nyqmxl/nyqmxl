from playwright.sync_api import sync_playwright
import time

def create_context(proxy=None):
    with sync_playwright() as p:
        # 启动 Chromium 浏览器
        browser = p.chromium.launch(headless=False)

        # 创建一个新的浏览器上下文
        context = browser.new_context(
            # 设置操作系统为 Windows 的典型 User-Agent
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            # 设置屏幕分辨率
            viewport={"width": 1280, "height": 800},
            # 设置时区
            timezone_id="America/Los_Angeles",
            # 设置语言
            locale="zh-CN",
        )

        # 如果需要使用代理
        if proxy:
            context.set_proxy(proxy)

        # 返回浏览器上下文
        return context

def main():
    # 创建浏览器上下文
    context = create_context()

    # 打开一个新的页面
    page = context.new_page()

    # 使用 goto 方法打开网页
    page.goto("https://www.tiktok.com/login", timeout=30000)  # 超时30秒

    # 确保页面已加载并处理后才进行后续操作
    page.wait_for_load_state("networkidle")
    print("网页已打开")

    # 防止 WebRTC 泄露真实 IP
    page.evaluate('''() => {
        // 禁用 WebRTC
        if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
            const origGetUserMedia = navigator.mediaDevices.getUserMedia;
            navigator.mediaDevices.getUserMedia = function(constraints) {
                return origGetUserMedia.apply(navigator.mediaDevices, [constraints]);
            };
        }
    }''')

    # 进行其他操作，例如截屏、查找元素等
    # ...

    # 保持浏览器打开一段时间（例如30秒）
    time.sleep(30)

    # 关闭页面和上下文
    page.close()
    context.close()

if __name__ == "__main__":
    main()