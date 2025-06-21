

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
    - Message sending: Send messages to the current page's input box.
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


# 标准库
from time import sleep, time
from os import makedirs
from os.path import dirname, join

# 第三方库
from io import BytesIO
from PIL import Image
from numpy import array
from base64 import b64decode
from cv2 import COLOR_RGB2GRAY, QRCodeDetector, cvtColor

# Selenium 相关库
from typing import List, Dict, Any, Optional
from pyautogui import press
from subprocess import Popen
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains


from PIL import Image, ImageDraw, ImageFont
import os


def images(name, size=200, bg_color=(165, 136, 114), text_color=(255, 255, 255), font_size=80):
    # 创建一个空白图像
    image = Image.new('RGB', (size, size), bg_color)
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
            print("无法加载中文字体，请确保系统中存在微软雅黑或其他中文字体。")

    # 获取名字的首字母（支持中文）
    initials = name[0] if name else '?'

    # 计算文本的宽度和高度
    text_width = font.getlength(initials)
    text_height = font_size  # 这里假设文本高度为字体大小

    # 计算文本位置，使其居中
    x = (size - text_width) // 2
    y = (size - text_height) // 2

    # 在图像上绘制文本
    draw.text((x, y), initials, fill=text_color, font=font)

    # 生成文件名
    avatar_filename = f"{name}_avatar.png"

    # 保存图像
    image.save(avatar_filename)

    return avatar_filename


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

    def _rec_trav_debug_(
        self,
        html_element: WebElement
    ) -> List[WebElement]:
        """
        递归遍历给定元素的所有子元素，并返回扁平化的 WebElement 对象列表。

        参数:
            html_element (WebElement): 当前要遍历的 WebElement 对象。

        返回:
            List[WebElement]: 扁平化的 WebElement 对象列表。

        注意:
            该方法主要用于内部调试，不建议直接调用。
        """
        html_elements = [html_element]
        html_children = html_element.find_elements(By.XPATH, "./*")
        for html_child in html_children:
            html_elements.extend(self._rec_trav_debug_(html_child))
        return html_elements

    def debug(
        self,
        css_selector: str
    ) -> List[Dict[str, Any]]:
        """
        通过给定的 CSS 选择器获取页面上的所有标签结构。

        参数:
            css_selector (str): 目标容器的 CSS 选择器。

        返回:
            List[Dict[str, Any]]: 标签结构列表，每个标签包含其名称、属性、文本内容和 CSS 类名。

        示例:
            >>> tiktok_instance.get("https://www.tiktok.com/@exampleuser")
            >>> result = tiktok_instance.debug("div.some-class")
            >>> print(result)
            [
                {"html_tag_name": "div", "html_class": "some-class", "html_text": "Example Text",
                    "html_attributes": "<div class='some-class'>Example Text</div>"}
            ]
        """
        obj_data = []
        for obj_element in self._rec_trav_debug_(
            self.driver.find_element(
                By.CSS_SELECTOR,
                css_selector
            )
        ):
            obj_data.append(
                {
                    "html_tag_name": obj_element.tag_name,
                    "html_class": obj_element.get_attribute("class"),
                    "html_text": obj_element.text,
                    "html_attributes": obj_element.get_attribute("outerHTML"),
                }
            )
        return obj_data

    def _object(
        self,
        css_parent: str = ".css-7whb78-DivCommentListContainer",
        css_child: str = ".css-13wx63w-DivCommentObjectWrapper",
        css_max: float = float('inf'),
        time_delay: float = 1.0
    ) -> List[WebElement]:
        """
        获取页面上的列表。

        参数:
            css_parent (str): 父容器的 CSS 选择器。
            css_child (str): 子元素的 CSS 选择器。
            css_max (float): 最大获取的数量。
            time_delay (float): 每次滚动后的延迟时间。

        返回:
            list: 包含子元素的 WebElement 列表。

        示例:
            >>> result = tiktok_instance._object(css_parent=".parent-class", css_child=".child-class", css_max=10, time_delay=1.0)
            >>> print(result)
            [<WebElement (session="abc123", element="def456")>, ...]
        """
        obj_comments = [
            self.driver.find_element(
                By.CSS_SELECTOR,
                css_parent
            )
        ]
        self.driver.execute_script(
            "arguments[0].scrollIntoView();",
            obj_comments[0]
        )
        obj_prev_comments = None
        while len(obj_comments) < css_max and obj_comments != obj_prev_comments:
            if (int(time()) % time_delay < 2):
                obj_prev_comments = obj_comments
            for _ in range(int(time_delay)):
                sleep(time_delay / 10)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);",
                    obj_comments[-1]
                )
                sleep(time_delay / 10)
                obj_comments = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    css_child
                )
                time_delay += (time_delay / 100)
        self.driver.execute_script("window.scrollTo(0, 0);")
        return obj_comments[:int(css_max)]

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
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-extensions",
                "--disable-default-apps",
                "--disable-popup-blocking",
                "--disable-translate",
                "--disable-infobars",
                "--disable-notifications",
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
        press("esc")
        sleep(time_delay)

    def click(
        self,
        css_selector: str = "div.css-1ldzp5s-DivNumber",
        time_delay: float = 1.0
    ) -> bool:
        """
        点击页面上的指定元素。

        参数:
            css_selector (str): 要点击的元素的 CSS 选择器。
            time_delay (float): 点击前的延迟时间。

        返回:
            bool: 如果点击成功，返回 True；否则返回 False。

        示例:
            >>> tiktok_instance.click(css_selector="button.some-class", time_delay=1.0)
            True
        """
        try:
            self.driver.find_elements(
                By.CSS_SELECTOR,
                css_selector
            )[1].click()
        except:
            return False
        sleep(time_delay)
        return True

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
            if callable(getattr(self, name)) and not name.startswith("__") and name != 'call'
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

    def images(name, size=200, bg_color=(165, 136, 114), text_color=(255, 255, 255), font_size=80):
        # 创建一个空白图像
        image = Image.new('RGB', (size, size), bg_color)
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
                print("无法加载中文字体，请确保系统中存在微软雅黑或其他中文字体。")

        # 获取名字的首字母（支持中文）
        initials = name[0] if name else '?'

        # 计算文本的宽度和高度
        text_width = font.getlength(initials)
        text_height = font_size  # 这里假设文本高度为字体大小

        # 计算文本位置，使其居中
        x = (size - text_width) // 2
        y = (size - text_height) // 2

        # 在图像上绘制文本
        draw.text((x, y), initials, fill=text_color, font=font)

        # 生成文件名
        avatar_filename = f"{name}_avatar.png"

        # 保存图像
        image.save(avatar_filename)

        return avatar_filename

    def user_info(self) -> bool:

        try:
            # 点击主页按钮
            self.driver.find_element(
                By.XPATH, '//button[@aria-label="主页"]'
            ).click()
            images_data = self.driver.current_url
            self.driver.get(images_data)
            sleep(2)  # 等待页面加载

            images_data = images_data.split("/")[-1][1:]
            images_data = images(images_data)
            # 点击编辑主页按钮
            self.driver.find_element(
                By.XPATH, '//button[@data-e2e="edit-profile-entrance"]'
            ).click()
            print("002")
            sleep(2)
            avatar_input = self.driver.find_element(
                By.XPATH, '//input[@type="file"]'
            )
            avatar_input.send_keys(images_data)  # 替换为你的头像图片路径
            sleep(2)  # 等待头像上传完成
            print("003")

            print(images_data)
            os.remove(images_data)

            data_info = {
                '//div[@data-e2e="edit-profile-username-input"]/input': "jinyu_tiktok_001",
                '//div[@data-e2e="edit-profile-name-input"]/input': "jinyu_tiktok_001",
                '//textarea[@data-e2e="edit-profile-bio-input"]': "jinyu_tiktok_001"
            }

            # 遍历字典，找到每个输入框元素并输入新值
            for xpath, new_value in data_info.items():
                # 使用固定时间等待元素加载
                try:
                    sleep(1)
                    element = self.driver.find_element(By.XPATH, xpath)

                    # 使用 ActionChains 全选并删除内容
                    element.send_keys(Keys.CONTROL + "a")
                    element.send_keys(Keys.DELETE)

                    # 输入新内容
                    element.send_keys(new_value)
                except:
                    print("无法修改")

            # 等待一段时间然后点击保存按钮
            sleep(2)
            self.driver.find_element(
                By.XPATH, '//button[@data-e2e="edit-profile-save"]').click()

            # 等待二次确认弹窗加载，然后点击确认按钮
            sleep(2)
            self.driver.find_element(
                By.XPATH, '//button[@data-e2e="set-username-popup-confirm"]').click()

            sleep(60)
            print("信息修改成功")
            return True

        except Exception as e:
            print(f"修改信息时出错: {str(e)}")
            return False


def user_get(
    data_config: Dict[str, Any] = {
        "browser_path": "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "debug_port": None,
        "username": "user_info",
        "proxy": None,
        "headless": False
    },
    data_params: Dict = {
        "launch": None,
        "connect": None,
        "get": {"browser_link": "https://www.tiktok.com/", "time_delay": 5.0},
        "user_info": None,
        "quit": None
    },
    data_time=3,
    data_debug: bool = True
) -> Dict[str, Any]:
    data = tiktok(**data_config).call(data_params)
    return data


if __name__ == "__main__":
    user_get()
