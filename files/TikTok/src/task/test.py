from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 启动 Chrome 浏览器，启用远程调试端口
# chrome.exe --remote-debugging-port=9222 --headless=new --window-size=1920,1080

# 创建一个 Chrome 选项对象
chrome_options = Options()

# 添加调试地址
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# 连接到已经启动的 Chrome 实例
driver = webdriver.Chrome(options=chrome_options)

try:
    # 打开网页
    # driver.get("https://www.baidu.com")

    # 进行截图并保存
    driver.save_screenshot("screenshot.png")
    print("截图保存成功！")

finally:
    # 关闭浏览器
    driver.quit()