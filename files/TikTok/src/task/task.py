

"""
TikTok Automation Module

This module provides a comprehensive automation framework for interacting with TikTok using Selenium and other libraries.
It allows users to perform various operations such as launching a browser, navigating to TikTok pages, searching for users and videos,
extracting user and video information, sending messages, and interacting with comments.

The module is designed to be flexible and extensible, allowing users to customize their automation tasks through a variety of methods and parameters.

特点：
    - 浏览器管理：启动并连接到 Chrome 浏览器实例。
    - 页面导航：使用 URL 导航到特定的 TikTok 页面。
    - 用户和视频搜索：在 TikTok 上搜索用户和视频并提取相关信息。
    - 评论交互：提取评论、回复评论并与评论区互动。
    - 发送消息：向当前页面的输入框发送消息。
    - 用户信息提取：从 TikTok 个人资料页面提取详细用户信息。
    - 用户列表提取：提取关注者或关注用户的列表。
    - 动态方法调用：通过基于字典的接口动态调用方法。

Features:
    - Browser management: Launch and connect to a Chrome browser instance.
    - Navigation: Navigate to specific TikTok pages using URLs.
    - User and video search: Search for users and videos on TikTok and extract relevant information.
    - Comment interaction: Extract comments, reply to comments, and interact with comment sections.
    - Message sending: Send messages to the current page"s input box.
    - User information extraction: Extract detailed user information from a TikTok profile page.
    - User list extraction: Extract lists of followers or following users.
    - Dynamic method invocation: Dynamically call methods using a dictionary-based interface.

Python 环境要求：
    - Python 3.8 或更高版本（由于使用了类型提示和其他现代 Python 特性）。
    - 已安装并正确配置 Selenium WebDriver。
    - 系统上已安装 Chrome 浏览器。
    - 可选：代理服务器配置用于网络请求。

Python Environment Requirements:
    - Python 3.8 or higher (due to the use of type hints and other modern Python features).
    - Selenium WebDriver installed and configured correctly.
    - Chrome browser installed on the system.
    - Optional: Proxy server configuration for network requests.

安装命令：
    由于此模块尚未在 PyPI 上发布，因此需要从源代码安装。以下是安装步骤：
    1. 克隆或下载代码仓库。
    2. 进入项目目录。
    3. 使用以下命令安装：
       ```
       python3 -m pip install selenium pillow numpy opencv-python pyautogui
       ```
       或
       ```
       python -m pip install selenium pillow numpy opencv-python pyautogui
       ```

Installation Command:
    Since this module is not available on PyPI, it needs to be installed from the source code. Follow these steps:
    1. Clone or download the code repository.
    2. Navigate to the project directory.
    3. Install using the following command:
       ```
       python3 -m pip install selenium pillow numpy opencv-python pyautogui
       ```
       or
       ```
       python -m pip install selenium pillow numpy opencv-python pyautogui
       ```

使用示例：
    >>> from tiktok import tiktok
    >>> data = {
    ...     "browser_path": "C:/Program Files/Google/Chrome/Application/chrome.exe",
    ...     "debug_port": None,
    ...     "username": None,
    ...     "proxy": None,
    ...     "headless": False
    ... }
    >>> tiktok_instance = tiktok(**data)
    >>> tiktok_instance.launch()
    >>> tiktok_instance.connect()
    >>> tiktok_instance.get("https://www.tiktok.com/login/qrcode")

Example:
    >>> from tiktok import tiktok
    >>> data = {
    ...     "browser_path": "C:/Program Files/Google/Chrome/Application/chrome.exe",
    ...     "debug_port": None,
    ...     "username": None,
    ...     "proxy": None,
    ...     "headless": False
    ... }
    >>> tiktok_instance = tiktok(**data)
    >>> tiktok_instance.launch()
    >>> tiktok_instance.connect()
    >>> tiktok_instance.get("https://www.tiktok.com/login/qrcode")

注意事项：
    - 确保已安装 Chrome 浏览器并正确配置了 Selenium WebDriver。
    - 网络问题可能导致某些操作失败。请检查网络连接并确保提供的 URL 是有效的。
    - 对于高级用法，请参阅各个方法的文档字符串，了解有关参数和返回值的详细信息。

Note:
    - Ensure that the Chrome browser is installed and the Selenium WebDriver is configured correctly.
    - Network issues may cause certain operations to fail. Please check your network connection and ensure that the provided URLs are valid.
    - For advanced usage, refer to the individual method docstrings for detailed information on parameters and return values.

参见：
    selenium.webdriver：用于浏览器自动化的 Selenium WebDriver 库。
    PIL.Image：用于图像处理的 Python Imaging Library。
    cv2.QRCodeDetector：用于二维码检测的 OpenCV 库。

See Also:
    selenium.webdriver: The Selenium WebDriver library used for browser automation.
    PIL.Image: The Python Imaging Library used for image processing.
    cv2.QRCodeDetector: The OpenCV library used for QR code detection.
"""


from os import makedirs
from os.path import dirname, join, abspath
from random import randint
from datetime import datetime as dt
from time import sleep, time
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any, Optional
from pyautogui import press
from subprocess import Popen
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


class tiktok:
    """
    TikTok 自动化操作类，用于通过 Selenium 和其他库实现与 TikTok 的交互。

    该类提供了以下功能：
    - 启动 Chrome 浏览器并连接到 TikTok 页面。
    - 搜索用户和视频，并提取相关信息。
    - 发送消息和评论。
    - 提取用户和视频的详细信息。
    - 自动化登录过程（通过二维码）。
    - 与评论进行交互（如回复评论）。

    属性:
        browser_path (str): 浏览器可执行文件路径。
        debug_port (int): 浏览器调试端口。
        username (str): TikTok 账号用户名。
        proxy (str): 代理服务器地址（可选）。
        headless (bool): 是否以无头模式运行浏览器。
        driver (webdriver): Selenium WebDriver 实例。
        browser_process (Popen): 浏览器进程实例。
        user_data_dir (str): 用户数据目录。
        cache_dir (str): 缓存目录。

    示例:
        >>> data = {
        ...     "browser_path": "C:/Program Files/Google/Chrome/Application/chrome.exe",
        ...     "debug_port": None,
        ...     "username": None,
        ...     "proxy": None,
        ...     "headless": False
        ... }
        >>> tiktok_instance = tiktok(**data)
        >>> tiktok_instance.launch()
        >>> tiktok_instance.connect()
        >>> tiktok_instance.get("https://www.tiktok.com/login/qrcode")

    注意:
        使用该类时需要确保 Chrome 浏览器已安装，并且 Selenium WebDriver 配置正确。
        如果使用代理或无头模式，需要确保相关配置正确。
        网络问题可能导致某些操作失败，请确保网络连接正常，并检查提供的 URL 是否合法。
    """

    def __init__(
        self,
        browser_path: Optional[str] = None,
        debug_port: Optional[int] = None,
        username: Optional[str] = None,
        proxy: Optional[str] = None,
        headless: bool = False
    ) -> None:
        """
        初始化 TikTok 自动化操作类。

        参数:
            browser_path (str, 可选): 浏览器可执行文件路径，默认为 "chrome"。
            debug_port (int, 可选): 浏览器调试端口，默认为 9222。
            username (str, 可选): TikTok 账号用户名，默认为 "default"。
            proxy (str, 可选): 代理服务器地址，默认为 None。
            headless (bool, 可选): 是否以无头模式运行浏览器，默认为 False。

        示例:
            >>> tiktok_instance = tiktok(browser_path="/path/to/chrome", debug_port=9222, username="my_username")
        """
        self.swap = None
        self.browser_path = browser_path or "chrome"
        self.debug_port = debug_port or 9222
        self.username = username or "default"
        self.proxy = proxy
        self.headless = headless
        self.driver = None
        self.browser_process = None
        self.user_data_dir = join(dirname(__file__), "profiles", self.username)
        self.cache_dir = join(dirname(__file__), "cache", self.username)
        makedirs(self.user_data_dir, exist_ok=True)
        makedirs(self.cache_dir, exist_ok=True)

    def launch(
        self
    ) -> bool:
        """
        启动浏览器，并根据指定的配置运行。

        返回:
            bool: 如果浏览器启动成功，返回 True；否则返回 False。

        示例:
            >>> tiktok_instance.launch()
            True
        """
        try:
            browser_args = [
                self.browser_path,
                f"--remote-debugging-port={self.debug_port}",
                f"--user-data-dir={self.user_data_dir}",
                f"--disk-cache-dir={self.cache_dir}",
                # "--no-sandbox",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-default-apps",
                "--disable-popup-blocking",
                "--disable-translate",
                "--disable-infobars",
                "--disable-notifications",
                "--enable-unsafe-swiftshader",
                "--window-size=1440,2560"
            ]
            self.proxy and browser_args.append(f"--proxy-server={self.proxy}")
            self.headless and browser_args.append("--headless=new")
            self.browser_process = Popen(browser_args)
            return True
        except:
            return False

    def connect(
        self
    ) -> bool:
        """
        连接到正在运行的浏览器实例。

        返回:
            bool: 如果连接成功，返回 True；否则返回 False。

        示例:
            >>> tiktok_instance.connect()
            True
        """
        try:
            browser_options = Options()
            browser_options.add_experimental_option(
                "debuggerAddress",
                f"127.0.0.1:{self.debug_port}"
            )
            self.driver = webdriver.Chrome(options=browser_options)
            return True
        except Exception as e:
            return False

    def quit(self):
        self.driver.close()
        self.driver.quit()

    def get(
        self,
        browser_link: str = "https://www.tiktok.com/login/qrcode",
        time_delay: float = 1.0
    ) -> None:
        """
        在浏览器中导航到指定的 URL。

        参数:
            browser_link (str): 要导航到的 URL。
            time_delay (float): 导航后等待的时间（秒）。

        返回:
            None

        示例:
            >>> tiktok_instance.get("https://www.tiktok.com/@exampleuser", time_delay=5.0)

        注意:
            如果导航失败，可能是由于网络问题或提供的 URL 不合法。请检查网络连接并确保 URL 正确。
        """
        self.driver.get(browser_link)
        self.driver.window_handles[0]
        press("esc")
        sleep(time_delay)
        self.driver.save_screenshot("images.png")

    def call(
        self,
        func_call: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        调用指定的功能方法，并返回执行结果。

        该方法允许通过一个字典动态调用类中的其他方法。字典的键为方法名，值为该方法的参数（如果需要）。
        如果方法调用成功，返回结果会包含执行状态和返回值；如果失败，则返回错误信息。

        参数:
            func_call (dict): 包含要调用的方法及其参数的字典。
                - 键为方法名（如 `launch`、`connect`、`get` 等）。
                - 值为该方法的参数（如果需要），可以是 `None` 或一个字典。

        返回:
            dict: 包含每个方法的执行结果，格式如下：
                {
                    "method_name": {
                        "utc": "调用时间戳",
                        "args": "方法参数",
                        "status": "执行状态（True/False/None）",
                        "return": "方法返回值或错误信息"
                    }
                }

        示例:
            >>> data = {
            ...     "launch": None,
            ...     "connect": None,
            ...     "get": {"browser_link": "https://www.tiktok.com/@exampleuser", "time_delay": 5.0},
            ...     "user_get": None,
            ...     "comment": {"comments_count": {"😭😭😭": None, "😭😭": "Unc clip farming ❤️‍🩹"}},
            ...     "get": {"browser_link": "https://www.tiktok.com/@anotheruser", "time_delay": 5.0},
            ...     "user_list": None,
            ...     "search_user": None,
            ...     "search_video": None,
            ...     "quit": None
            ... }
            >>> result = tiktok_instance.call(data)
            >>> print(result)
            {
                "launch": {"utc": 1681234567, "args": None, "status": True, "return": None},
                "connect": {"utc": 1681234568, "args": None, "status": True, "return": None},
                "get": {"utc": 1681234569, "args": {"browser_link": "https://www.tiktok.com/@exampleuser", "time_delay": 5.0}, "status": True, "return": None},
                "user_get": {"utc": 1681234570, "args": None, "status": True, "return": {"user_id": "123456789", "user_name": "example_user", ...}},
                "comment": {"utc": 1681234571, "args": {"comments_count": {"😭😭😭": None, "😭😭": "Unc clip farming ❤️‍🩹"}}, "status": True, "return": [...]},
                "get": {"utc": 1681234572, "args": {"browser_link": "https://www.tiktok.com/@anotheruser", "time_delay": 5.0}, "status": True, "return": None},
                "user_list": {"utc": 1681234573, "args": None, "status": True, "return": [...]},
                "search_user": {"utc": 1681234574, "args": None, "status": True, "return": [...]},
                "search_video": {"utc": 1681234575, "args": None, "status": True, "return": [...]},
                "quit": {"utc": 1681234576, "args": None, "status": True, "return": None}
            }

        注意:
            - 如果某个方法调用失败，`status` 会是 `False`，并且 `return` 会包含错误信息。
            - 如果某个方法名在类中不存在，`status` 会是 `None`，并且 `return` 会是 `None`。
            - 该方法会自动处理多个方法的调用顺序，但不会自动处理方法之间的依赖关系。如果某个方法依赖于之前的某个方法的结果，请确保调用顺序正确。
        """
        func_list = {
            name: getattr(self, name)
            for name in dir(self)
            if callable(getattr(self, name)) and not name.startswith("__") and name != "call"
        }
        if type(func_call) == dict:
            for func_name in list(func_call):
                if func_name in func_list:
                    try:
                        func_call[func_name] = {
                            "utc": time(),
                            "args": func_call[func_name],
                            "status": True,
                            "return": func_list[func_name](**func_call[func_name]) if type(func_call[func_name]) == dict else func_list[func_name]()
                        }
                    except Exception as func_error:
                        func_call[func_name] = {
                            "utc": time(),
                            "args": func_call[func_name],
                            "status": False,
                            "return": str(func_error)
                        }
                else:
                    func_call[func_name] = {
                        "utc": time(),
                        "args": func_call[func_name],
                        "status": None,
                        "return": None
                    }
            return func_call
        return None

    def reg(self, user, passwd):
        while (not self.driver.find_elements(By.XPATH, "//*[@id='Month-options-list-container']")):
            sleep(0.1)  # 弹出验证框
        sleep(1)
        reg_data = {
            "date": {
                "comboboxes": self.driver.find_elements(
                    By.XPATH,
                    "//*[@role='combobox']"
                ),
                # 定义年、月、日的最大选项数并生成随机选项索引
                "operations": [
                    # 月
                    f"//*[@id='Month-options-list-container']/div[{str(randint(1, 13))}]",
                    # 日
                    f"//*[@id='Day-options-list-container']/div[{str(randint(1, 31))}]",
                    # 年
                    f"//*[@id='Year-options-list-container']/div[{str(randint(19, 107))}]"
                ],
            },
            "user_info": {
                "//input[@placeholder='邮箱地址']": user,
                "//input[@placeholder='密码']": passwd
            }
        }
        for index, text in enumerate(reg_data["date"]["operations"]):
            reg_data["date"]["comboboxes"][index].click()
            self.driver.find_element(By.XPATH, text).click()

        for f1k, f1v in reg_data["user_info"].items():
            self.driver.find_element(By.XPATH, f1k).send_keys(f1v)
        send_code_button = self.driver.find_element(
            By.XPATH,
            "//button[@data-e2e='send-code-button']"
        )
        send_code_button.click()
        send_code_button.click()
        sleep(5)
        while self.driver.find_elements(By.XPATH, "//button[@id='captcha_close_button']"):
            print(F"[{str(dt.now())}] 弹出验证阻止下一步。")
            sleep(1)  # 弹出验证框
        send_code_button.click()
        sleep(1)
        reg_data = self.driver.find_elements(
            By.XPATH,
            "//span[@role='status']"
        )
        if (reg_data):
            return reg_data[0].text

        verification_code_input = self.driver.find_element(
            By.XPATH,
            "//input[@placeholder='输入 6 位验证码']"
        )

        print(F"[{str(dt.now())}] 请手动输入6位验证码...")

        while len(verification_code_input.get_attribute("value")) != 6:
            sleep(0.1)
        self.driver.find_element(
            By.XPATH,
            "//button[contains(text(), '下一步')]"
        ).click()
        sleep(1)
        reg_data = self.driver.find_elements(
            By.XPATH,
            "//div[@type='error']/span[@role='status']"
        )
        reg_data = reg_data[0].text if (reg_data) else None
        return reg_data

    def login(self, user, passwd):
        username_input = self.driver.find_element(
            By.XPATH, "(//input[contains(@placeholder,'电子邮件或用户名')])[1]")
        username_input.send_keys(user)

        # 定位密码输入框并输入密码
        password_input = self.driver.find_element(
            By.XPATH, "(//input[contains(@placeholder,'密码')])[1]")
        password_input.send_keys(passwd)

        # 定位并点击登录按钮
        login_button = self.driver.find_element(
            By.XPATH, "(//button[@data-e2e='login-button'])[1]")
        login_button.click()
        sleep(5)
        while self.driver.find_elements(By.XPATH, "//button[@id='captcha_close_button']"):
            print(F"[{str(dt.now())}] 弹出验证阻止下一步。")
            sleep(1)  # 弹出验证框
        sleep(5)
        verification_code_input = self.driver.find_elements(
            By.XPATH,
            "//input[@placeholder='输入 6 位验证码']"
        )
        if (verification_code_input):
            verification_code_input = verification_code_input[0]
            print(f"[{str(dt.now())}] 请手动输入6位验证码...")

            # 循环检测输入框的值是否为6位
            while len(verification_code_input.get_attribute("value")) != 6:
                sleep(0.1)

            # 点击“下一步”按钮
            self.driver.find_element(
                By.XPATH,
                "//button[contains(text(), '下一步')]"
            ).click()
            print(f"[{str(dt.now())}] 验证码输入完成，点击下一步按钮")
            sleep(5)
            reg_data = self.driver.find_elements(
                By.XPATH,
                "//div[@class='twv-component-error-text']"
            )
            reg_data = reg_data[0].text if (reg_data) else None
            return reg_data

    def images(self, name, size=200, bg_color=(165, 136, 114), text_color=(255, 255, 255), font_size=80):

        # 创建一个空白图像
        image = Image.new("RGB", (size, size), bg_color)
        draw = ImageDraw.Draw(image)

        # 加载中文字体（微软雅黑）
        try:
            # 尝试加载微软雅黑字体
            font_path = "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑字体路径
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            # 如果微软雅黑字体不可用，则尝试加载其他中文字体
            try:
                font_path = "/System/Library/Fonts/PingFang.ttc"  # macOS 系统字体
                font = ImageFont.truetype(font_path, font_size)
            except IOError:
                # 如果仍然无法加载中文字体，则使用默认字体
                font = ImageFont.load_default()
                print("无法加载中文字体，请确保系统中存在微软雅黑或其他中文字体")

        # 获取名字的首字母（支持中文）
        initials = name[0] if name else "?"

        # 计算文本的宽度和高度
        text_width = font.getlength(initials)
        text_height = font_size  # 这里假设文本高度为字体大小

        # 计算文本位置，使其居中
        x = (size - text_width) // 2
        y = (size - text_height) // 3.5

        # 在图像上绘制文本
        draw.text((x, y), initials, fill=text_color, font=font)

        # 生成文件名
        avatar_filename = f"{name}_avatar.png"
        # 保存图像
        image.save(avatar_filename)

        return avatar_filename

    def info(self, path=None, user=str(), name=str(), bio=str()) -> bool:
        try:
            while self.driver.find_elements(By.XPATH, "//button[@id='captcha_close_button']"):
                print(F"[{str(dt.now())}] 弹出验证阻止下一步。")
                sleep(1)  # 弹出验证框
            sleep(1)  # 弹出验证框
            self.driver.find_element(
                By.XPATH, "//button[@aria-label='主页']"
            ).click()
            images_data = self.driver.current_url
            self.driver.get(images_data)
            sleep(2)
            self.driver.find_element(
                By.XPATH, "//button[@data-e2e='edit-profile-entrance']"
            ).click()
            sleep(3)
            if (path):
                images_data = path
            else:
                images_data = images_data.split("/")[-1].split("?")[0][1:]
                images_data = str(images_data)
                images_data = self.images(images_data)
            images_data = abspath(images_data)
            self.driver.find_element(
                By.XPATH,
                "//input[@type='file' and @accept]"
            ).send_keys(images_data)
            sleep(2)
            self.driver.find_element(By.XPATH, "//button[text()='应用']").click()
            sleep(2)
            data_info = {
                "//div[@data-e2e='edit-profile-username-input']/input": user,
                "//div[@data-e2e='edit-profile-name-input']/input": name,
                "//textarea[@data-e2e='edit-profile-bio-input']": bio
            }
            for xpath, new_value in data_info.items():
                try:
                    sleep(0.1)
                    element = self.driver.find_element(By.XPATH, xpath)
                    element.send_keys(Keys.CONTROL + "a")
                    element.send_keys(Keys.DELETE)
                    element.send_keys(new_value)
                except:
                    print(F"[{str(dt.now())}] 无法修改")
            sleep(2)
            self.driver.find_element(
                By.XPATH,
                "//button[@data-e2e='edit-profile-save']"
            ).click()
            print(F"[{str(dt.now())}] 更新信息")
            sleep(5)
            return True

        except Exception as e:
            print(F"[{str(dt.now())}] 修改信息时出错: {str(e)}")
            return False

    def post_video(self, file_path, video_description, source_comment):
        try:
            file_path = abspath(file_path)
            self.driver.find_element(
                By.XPATH,
                "//input[@type='file']"
            ).send_keys(file_path)
            while (not self.driver.find_elements(By.XPATH, "//div[@class='jsx-1979214919 info-status success']")):
                sleep(0.1)
            sleep(1)
            description_editor = self.driver.find_element(
                By.XPATH,
                "//div[@class='notranslate public-DraftEditor-content']"
            )
            description_editor.click()
            description_editor.send_keys(Keys.CONTROL + "a")
            description_editor.send_keys(Keys.DELETE)
            description_editor.send_keys(video_description)
            sleep(1)
            self.driver.find_element(
                By.XPATH,
                "//button[@data-e2e='post_video_button']"
            ).click()
            sleep(5)
            self.driver.find_element(
                By.XPATH,
                "//div[@data-tt='VideoCover_index_VideoCoverContainer']"
            ).click()
            sleep(2)
            self.driver.find_element(
                By.XPATH,
                "//textarea[@placeholder='添加评论...']"
            ).send_keys(source_comment)
            self.driver.find_element(
                By.XPATH,
                "//button/span[text()='发布']"
            ).click()
            return True
        except Exception as e:
            print(e)
            return False

    def get_list(self, parent, child):
        self.swap = self.driver.find_element(By.XPATH, parent)
        parent = 2**16
        while self.driver.execute_script("return document.body.scrollHeight") != parent:
            parent = self.driver.execute_script(
                "return document.body.scrollHeight"
            )
            for _ in range(3):
                # 滚动父容器到底部
                self.swap.send_keys(Keys.END)
                self.driver.save_screenshot("images.png")
                sleep(1)
        self.swap = self.swap.find_elements(By.XPATH, child)
        return len(self.swap)

    def search_videos(self, source_comment=str()):
        for video in range(len(self.swap)):
            try:
                self.swap[video] = self.swap[video].find_element(
                    By.TAG_NAME,
                    "a"
                ).get_attribute("href")
                self.swap[video] = {
                    "user_uri": "/".join(self.swap[video].split("/")[:4]),
                    "user_video": self.swap[video],
                    "user_comment": source_comment
                }
            except Exception as e:
                print(f"Error: {e}")
        return self.swap

    def post_comment(self, source_comment=str()):
        if (self.swap and type(self.swap) == list):
            for f1 in self.swap:
                try:
                    print(
                        end=F"[{str(dt.now())}] 使用 {f1['user_comment']} 评论：{f1['user_video']}\t")
                    self.get(browser_link=f1["user_video"], time_delay=3.0)
                    self.driver.window_handles[0]
                    while (not self.driver.find_elements(
                        By.XPATH,
                        '//*[@id="main-content-video_detail"]/div/div[2]/div[1]/div[1]/div[1]/div[5]/div[2]/button[2]'
                    )):
                        sleep(0.1)
                    self.driver.find_element(
                        By.XPATH,
                        '//*[@id="main-content-video_detail"]/div/div[2]/div[1]/div[1]/div[1]/div[5]/div[2]/button[2]'
                    ).click()
                    sleep(2)
                    self.driver.find_element(
                        By.XPATH,
                        '//div[@data-e2e="comment-text"]'
                    ).click()
                    sleep(0.1)
                    actions = ActionChains(self.driver)
                    actions.send_keys(f1["user_comment"]).perform()
                    sleep(0.1)
                    actions.send_keys(Keys.ENTER).perform()
                    print("成功")
                except Exception as e:
                    self.driver.save_screenshot("error.png")
                    print(e)
            return len(self.swap)


def task(
    config: Dict[str, Any] = {
        "browser_path": "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "debug_port": None,
        "username": "test",
        "proxy": None,
        "headless": False
    },
    params: List = [
        # {
        # "launch": None,
        # "connect": None,
        # "get": {"browser_link": "https://www.tiktok.com/signup/phone-or-email/email", "time_delay": 3.0},
        # "reg": {"user": "admin@mengyunos.com", "passwd": "admin@12345"},
        # "get": {"browser_link": "https://www.tiktok.com/login/phone-or-email/email", "time_delay": 3.0},
        # "login": {"user": "jinyu_tiktok_001@outlook.com", "passwd": "jinyu_tiktok_001"},
        # "get": {"browser_link": "https://www.tiktok.com/login/phone-or-email/email", "time_delay": 3.0},
        # "info": {"user": "jinyu_tiktok_001", "name": "jinyu_tiktok_001", "bio": "jinyu_tiktok_001"},
        # "get": {"browser_link": "https://www.tiktok.com/tiktokstudio/upload?from=webapp&lang=zh-Hans", "time_delay": 3.0},
        # "post_video": {"file_path": "Download.mp4", "video_description": "jinyu_tiktok_001", "source_comment": "jinyu_tiktok_001"},
        # "get": {"browser_link": "https://www.tiktok.com/search/video?q=%E5%B0%8F%E8%90%9D%E8%8E%89", "time_delay": 3.0},
        # "get_list": {"parent": "/html/body", "child": "//div[@data-e2e='search_video-item']"},
        # "search_videos": {"source_comment": "嘿嘿。"},
        # "post_comment": {"source_comment": "嘿嘿。"},
        # "quit": None
        # }
    ],
    # data_time=3,
    # data_debug: bool = True
) -> Dict[str, Any]:
    match (params):
        case dict():
            params = tiktok(**config).call(params)
        case list():
            for f1 in params:
                f1 = tiktok(**config).call(f1)
        case _:
            print(params)
    return {"config": config, "params": params}


def main():
    parser = '''
    {
        "config": {
            "browser_path": "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "debug_port": null,
            "username": "test",
            "proxy": null,
            "headless": false
        },
        "params": [
            {
                "launch": null
            },
            {
                "connect": null,
                "get": {
                    "browser_link": "https://www.baidu.com",
                    "time_delay": 3.0
                }
            },
            {
                "connect": null,
                "get": {
                    "browser_link": "https://www.tiktok.com",
                    "time_delay": 3.0
                }
            },
            {
                "connect": null,
                "quit": null
            }
        ]
    }
    '''
    from argparse import ArgumentParser
    from json import loads, dumps
    from uuid import uuid1
    # 创建参数解析器
    try:
        parser = ArgumentParser(
            description="这是一个加载 JSON 配置文件的程序。",
            epilog="示例：python your_script.py --config params/config.json"
        )
        parser.add_argument(
            "--config",
            type=str,
            help="JSON 配置文件的路径",
            required=True
        )
        parser = parser.parse_args().config.replace("\\", "/")
        with open(parser, "r", encoding="UTF-8") as pf:
            parser_data = pf.read()
        parser_data = loads(parser_data)
        parser = "/".join(parser.split("/")[:-1])
        parser = F"{parser}/[done]{str(dt.now())[:-7]}.json".replace(":", "_")
        parser_data = task(**parser_data)
        with open(parser, "w", encoding="UTF-8") as pf:
            pf.write(dumps(parser_data, indent=4, ensure_ascii=False))

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
