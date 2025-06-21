

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

    def msg(
        self,
        msg_send: str = "Hello World!",
        time_delay: float = 0.0
    ) -> None:
        """
        在输入框中输入指定内容并发送消息。

        参数:
            msg_send (str): 要发送的消息内容。
            time_delay (float): 发送消息后等待的时间（秒）。

        返回:
            None

        示例:
            >>> tiktok_instance.msg(msg_send="Hello, world!", time_delay=1.0)
        """
        msg_actions = ActionChains(self.driver)
        msg_actions.send_keys(msg_send).perform()
        sleep(time_delay)
        msg_actions.send_keys(Keys.RETURN).perform()

    def qrcode(
        self,
        qr_image_base64: str
    ) -> str:
        """
        从 Base64 编码的图像数据中提取并解码二维码。

        参数:
            qr_image_base64 (str): Base64 编码的图像数据。

        返回:
            str: 解码后的二维码内容。

        示例:
            >>> qr_image_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA..."
            >>> result = tiktok_instance.qrcode(qr_image_base64)
            >>> print(result)
            "https://example.com/login/callback"

        注意:
            该方法依赖于二维码解析库，如果解析失败，可能是由于图像数据不完整或二维码损坏。
        """
        with Image.open(
            BytesIO(
                b64decode(
                    qr_image_base64.replace(
                        "data:image/png;base64,",
                        str()
                    )
                )
            )
        ) as qr_image:
            qr_image_with_border = Image.new(
                'RGB',
                (
                    qr_image.size[0] + 20,
                    qr_image.size[1] + 20
                ),
                'white'
            )
            qr_image_with_border.paste(
                qr_image,
                (10, 10)
            )
            qr_code_result = QRCodeDetector().detectAndDecode(
                cvtColor(
                    array(qr_image_with_border),
                    COLOR_RGB2GRAY
                )
            )
        return qr_code_result[0]

    def login(
        self
    ) -> str:
        """
        使用二维码完成登录过程。

        返回:
            str: 解码后的二维码内容。

        示例:
            >>> tiktok_instance.get("https://www.tiktok.com/login/qrcode", time_delay=5.0)
            >>> login_result = tiktok_instance.login()
            >>> print(login_result)
            "https://example.com/login/callback"

        注意:
            登录过程需要用户手动扫描二维码。如果二维码加载失败，可能是由于网络问题或页面未正确加载。
        """
        return self.qrcode(
            self.driver.execute_script(
                "return arguments[0].toDataURL('image/png');",
                self.driver.find_element(By.CSS_SELECTOR, "canvas")
            )
        )

    def comment(
        self,
        comments_count: Dict[str, Optional[str]] = dict(),
        css_count: int = 0x400,
        time_delay: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        根据指定的评论内容选择并回复评论。

        参数:
            comments_count (dict): 包含评论内容和回复内容的字典。
            css_count (int): 最大尝试加载的评论数量。
            time_delay (float): 每次操作之间的等待时间。

        返回:
            list: 包含处理后的评论信息。

        示例:
            >>> comments_count = {"😭😭😭": None, "😭😭": "Unc clip farming ❤️‍🩹"}
            >>> result = tiktok_instance.comment(comments_count=comments_count, css_count=10, time_delay=1.0)
            >>> print(result)
            [
                {"comment_text": "😭😭", "comment_reply": "Unc clip farming ❤️‍🩹"},
                {"comment_text": "😭😭😭", "comment_reply": None}
            ]

        注意:
            如果评论加载失败，可能是由于网络问题或页面未正确加载。请确保网络连接正常，并检查页面是否加载完成。
        """
        comments_data = [
            {
                "browser_link": self.driver.current_url,
                "comment_img": comment.find_element(By.CSS_SELECTOR, "img.css-1zpj2q-ImgAvatar").get_attribute("src"),
                "comment_user": comment.find_element(By.CSS_SELECTOR, "div.css-2hpyn8-DivTriggerWrapper>a.link-a11y-focus").get_attribute("href"),
                "comment_name": comment.find_element(By.CSS_SELECTOR, "a.link-a11y-focus > p.TUXText").text,
                "comment_text": comment.find_element(By.CSS_SELECTOR, "div.css-1k8xzzl-DivCommentContentWrapper > span > p").text,
                "comment_time": comment.find_element(By.CSS_SELECTOR, "div.css-1ivw6bb-DivCommentSubContentSplitWrapper > div > span").text,
                "comment_reply": comment.find_element(By.CSS_SELECTOR, "span.TUXText--weight-medium")
            }
            for comment in self._object(
                css_parent=".css-x4xlc7-DivCommentContainer",
                css_child=".css-13wx63w-DivCommentObjectWrapper",
                css_max=css_count,
                time_delay=time_delay
            )
        ]
        if (comments_count):
            comments_data = {f2["comment_text"]: f2 for f2 in comments_data}
            comments_count = {
                key: comments_data.get(value) if value is not None else None
                for key, value in comments_count.items()
            }
            comments_data = list()
            for f1k, f1v in comments_count.items():
                if (f1v is None):
                    f1v = {
                        "avatar_url": self.driver.current_url,
                        "username": self.driver.find_element(
                            By.CSS_SELECTOR,
                            "a[data-e2e='nav-profile']"
                        ).get_attribute("href").split("@")[1],
                        "comment_text": f1v,
                        "comment_reply": self.driver.find_element(
                            By.CSS_SELECTOR,
                            ".notranslate.public-DraftEditor-content"
                        )
                    }
                self.driver.execute_script(
                    "arguments[0].scrollIntoView();",
                    f1v["comment_reply"]
                )
                f1v["comment_reply"].click()
                self.msg(msg_send=f1k, time_delay=0.0)
                f1v["comment_reply"] = f1k
                comments_data.append(f1v)
                sleep(time_delay)
        else:
            comments_data = [
                {**comment, "comment_reply": None}
                for comment in comments_data
            ]
        self.driver.execute_script("window.scrollTo(0, 0);")
        return comments_data

    def user_get(
        self
    ) -> Dict[str, Any]:
        """
        获取当前页面用户的详细信息。

        返回:
            dict: 包含用户信息的字典，包含以下键：
                - user_id (str): 用户 ID
                - user_name (str): 用户名
                - user_signature (str): 用户签名
                - user_avatar (str): 用户头像链接
                - user_page (str): 用户主页链接
                - user_list (list): 用户列表（目前为空）
                - info_follow (list): 关注信息，包含关注数和关注文本
                - info_fans (list): 粉丝信息，包含粉丝数和粉丝文本
                - info_likes (list): 点赞信息，包含点赞数和点赞文本
                - button_follow (bool): 是否需要关注该用户
                - button_message (str): 消息按钮的链接

        示例:
            >>> tiktok_instance.get("https://www.tiktok.com/@exampleuser", time_delay=5.0)
            >>> user_info = tiktok_instance.user_get()
            >>> print(user_info)
            {
                "user_id": "123456789",
                "user_name": "example_user",
                "user_signature": "这是一个签名",
                "user_avatar": "https://example.com/avatar.jpg",
                "user_page": "https://www.tiktok.com/@exampleuser",
                "user_list": [],
                "info_follow": ["100", "关注"],
                "info_fans": ["200", "粉丝"],
                "info_likes": ["300", "点赞"],
                "button_follow": True,
                "button_message": "https://www.tiktok.com/inbox"
            }

        注意:
            如果用户信息加载失败，可能是由于网络问题或页面未正确加载。请确保网络连接正常，并检查页面是否加载完成。
        """
        user_info = {
            "user_id": self.driver.find_element(By.CSS_SELECTOR, "h1[data-e2e='user-title']").text,
            "user_name": self.driver.find_element(By.CSS_SELECTOR, "h2[data-e2e='user-subtitle']").text,
            "user_signature": self.driver.find_element(By.CSS_SELECTOR, "h2[data-e2e='user-bio']").text,
            "user_avatar": self.driver.find_element(By.CSS_SELECTOR, "img.css-1zpj2q-ImgAvatar.e1e9er4e1").get_attribute("src"),
            "user_page": self.driver.current_url,
            "user_list": [],
            **{
                key: [
                    self.driver.find_element(By.CSS_SELECTOR, selector).text
                    for selector in selectors
                ]
                for key, selectors in {
                    "info_follow": ["strong[data-e2e='following-count']", "span[data-e2e='following']"],
                    "info_fans": ["strong[data-e2e='followers-count']", "span[data-e2e='followers']"],
                    "info_likes": ["strong[data-e2e='likes-count']", "span[data-e2e='likes']"]
                }.items()
            },
            "button_follow": self.driver.find_element(By.CSS_SELECTOR, "button[data-e2e='follow-button']"),
            "button_message": self.driver.find_elements(By.CSS_SELECTOR, "a.link-a11y-focus")[-1].get_attribute("href")
        }

        if user_info["button_follow"].text == "关注":
            user_info["button_follow"].click()
            user_info["button_follow"] = True
        else:
            user_info["button_follow"] = False
        return user_info

    def user_list(
        self,
        css_parent=".css-wq5jjc-DivUserListContainer",
        css_child=".css-14xr620-DivUserContainer",
        css_count: int = 0xEB,
        time_delay: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        获取当前页面用户的关注列表或粉丝列表。

        参数:
            css_count (int): 最大尝试加载的用户数量。
            time_delay (float): 每次滚动页面后等待的时间。

        返回:
            list: 包含用户信息的字典列表。

        示例:
            >>> tiktok_instance.get("https://www.tiktok.com/@exampleuser/following", time_delay=5.0)
            >>> user_list = tiktok_instance.user_list(css_count=10, time_delay=1.0)
            >>> print(user_list)
            [
                {"user_link": "https://www.tiktok.com/@user1", "followers_img": "https://example.com/user1.jpg",
                    "followers_name": "user1", "followers_status": True},
                {"user_link": "https://www.tiktok.com/@user2", "followers_img": "https://example.com/user2.jpg",
                    "followers_name": "user2", "followers_status": False}
            ]

        注意:
            如果用户列表加载失败，可能是由于网络问题或页面未正确加载。请确保网络连接正常，并检查页面是否加载完成。
        """
        return [
            {
                "user_link": self.driver.current_url,
                "followers_img": user.find_element(By.XPATH, "//*[@id='tux-portal-container']/div/div[2]/div/div/div[2]/div/div/section/div/div[3]/li[1]/div/div/a/span/img").get_attribute("src"),
                "followers_user": user.find_element(By.CSS_SELECTOR, "p.css-swczgi-PUniqueId").text,
                "followers_name": user.find_element(By.CSS_SELECTOR, "div.css-1d8n6nn-DivNicknameContainer > span").text,
                # "followers_status": user.find_element(By.CSS_SELECTOR, "button.e1bph0nm2.css-82eomn-Button-StyledFollowButtonV2.ehk74z00").text.strip() != "关注"
            }
            for user in self._object(
                css_parent=css_parent,
                css_child=css_child,
                css_max=css_count,
                time_delay=time_delay
            )
        ]

    def search_user(
        self,
        css_parent=".css-f2h6fp-DivSearchContainer",
        css_child="[data-e2e='search-user-container']",
        css_count: int = 0x20,
        time_delay: float = 0.2
    ) -> List[Dict[str, Any]]:
        """
        搜索 TikTok 用户并返回用户信息列表。

        参数:
            css_count (int): 最大返回的用户数量。
            time_delay (float): 每次操作之间的等待时间。

        返回:
            list: 包含用户信息的字典列表。

        示例:
            >>> tiktok_instance.get("https://www.tiktok.com/search/user?q=example", time_delay=5.0)
            >>> search_result = tiktok_instance.search_user(css_count=10, time_delay=1.0)
            >>> print(search_result)
            [
                {"user_link": "https://www.tiktok.com/@user1", "user_img": "https://example.com/user1.jpg",
                    "user_id": "user1", "user_name": "User One"},
                {"user_link": "https://www.tiktok.com/@user2",
                    "user_img": "https://example.com/user2.jpg", "user_id": "user2", "user_name": "User Two"}
            ]

        注意:
            如果搜索结果加载失败，可能是由于网络问题或页面未正确加载。请确保网络连接正常，并检查页面是否加载完成。
        """
        return [
            {
                "user_link": element.find_element(By.CSS_SELECTOR, "a.css-7ogsq9-StyledAvatarUserLink").get_attribute("href"),
                "user_img": element.find_element(By.CSS_SELECTOR, "img.css-1zpj2q-ImgAvatar").get_attribute("src"),
                "user_id": element.find_element(By.XPATH, "//*[@id='search_user-item-user-link-1']/div/div/a[2]/div/p").text,
                "user_name": element.find_element(By.CSS_SELECTOR, "p.css-1ns35wh-PTitle").text,
                # "user_followers": element.find_element(By.CSS_SELECTOR, "div.css-ss1kov-DivLink > div > div > a > div > span").text,
                # "user_description": element.find_element(By.XPATH, "//*[@id='search_user-item-user-link-0']/div/div/a[2]/p[2]").text
            }
            for element in self._object(
                css_parent=css_parent,
                css_child=css_child,
                css_max=css_count,
                time_delay=time_delay
            )[:css_count]
        ]

    def search_video(
        self,
        css_parent=".css-4dxm8q-DivVideoFeed.eegew6e0",
        css_child=".css-1soki6-DivItemContainerForSearch",
        css_count: int = 0x100,
        time_delay: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        搜索 TikTok 视频并返回视频信息列表。

        参数:
            css_count (int): 最大返回的视频数量。
            time_delay (float): 每次操作之间的等待时间。

        返回:
            list: 包含视频信息的字典列表。

        示例:
            >>> tiktok_instance.get("https://www.tiktok.com/search/video?q=example", time_delay=5.0)
            >>> search_result = tiktok_instance.search_video(css_count=10, time_delay=1.0)
            >>> print(search_result)
            [
                {"video_link": "https://www.tiktok.com/@user1/video/123456", "video_avatar": "https://example.com/user1.jpg", "video_description": "Example Video",
                    "video_tags": ["#example"], "video_username": "user1", "video_view_count": "100", "video_like_count": "50"},
                {"video_link": "https://www.tiktok.com/@user2/video/789012", "video_avatar": "https://example.com/user2.jpg", "video_description":
                    "Another Example", "video_tags": ["#example"], "video_username": "user2", "video_view_count": "200", "video_like_count": "100"}
            ]

        注意:
            如果搜索结果加载失败，可能是由于网络问题或页面未正确加载。请确保网络连接正常，并检查页面是否加载完成。
        """
        return [
            {
                "video_link": element.find_element(By.CSS_SELECTOR, "a.css-1mdo0pl-AVideoContainer").get_attribute("href"),
                "video_avatar": element.find_element(By.CSS_SELECTOR, "img").get_attribute("src"),
                "video_description": element.find_element(By.CSS_SELECTOR, "img").get_attribute("alt"),
                "video_tags": [tag.strip() for tag in element.find_element(By.CSS_SELECTOR, "img").get_attribute("alt").split() if tag.startswith('#')],
                "video_username": element.find_element(By.CSS_SELECTOR, "a.css-1mdo0pl-AVideoContainer").get_attribute("href").split('/')[-3],
                "video_view_count": element.find_element(By.CSS_SELECTOR, "strong.video-count.css-dirst9-StrongVideoCount.e148ts222").text,
                "video_like_count": element.find_element(By.CSS_SELECTOR, "div.css-11u47i-DivCardFooter svg.like-icon + strong").text if element.find_elements(By.CSS_SELECTOR, "div.css-11u47i-DivCardFooter svg.like-icon + strong") else "0"
            }
            for element in self._object(
                css_parent=css_parent,
                css_child=css_child,
                css_max=css_count,
                time_delay=time_delay
            )[:css_count]
        ]

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


def user_get(
    data_config: Dict[str, Any] = {
        "browser_path": "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "debug_port": None,
        "username": "mxlbbi",
        "proxy": None,
        "headless": False
    },
    data_params: Dict = {
        "launch": None,
        "connect": None,
        "get": {"browser_link": "https://www.tiktok.com/search/video?q=nmap", "time_delay": 5.0},
        "search_video": {
            "css_parent": ".css-4dxm8q-DivVideoFeed.eegew6e0",
            "css_child": ".css-1soki6-DivItemContainerForSearch",
            # "css_count": 1000,
            "time_delay": 3
        },
        # "quit": None
    },
    data_time=3,
    data_debug: bool = True
) -> Dict[str, Any]:
    """
    主函数，用于演示 TikTok 自动化操作类的功能。

    该函数通过 `tiktok` 类的实例化和调用，依次执行以下操作：
    1. 启动浏览器并连接到调试端口。
    2. 导航到指定的 TikTok 页面。
    3. 搜索用户并返回用户信息列表。
    4. 搜索视频并返回视频信息列表。
    5. 发送消息到当前页面的输入框。
    6. 获取当前页面的评论列表。
    7. 根据指定的评论内容选择并回复评论。
    8. 获取当前页面用户的详细信息。
    9. 获取当前页面用户的关注列表或粉丝列表。
    10. 关闭浏览器并终止浏览器进程。

    示例:
        >>> result = test()
        >>> print(result)
        执行上述操作并返回结果。

    注意:
        - 由于网络原因或链接问题，某些操作可能失败。如果遇到问题，请检查网页链接的合法性，并适当重试。
        - 如果不需要解析特定链接的内容，可以跳过相关步骤。
        - 请确保网络连接正常，并检查 TikTok 页面是否加载完成。

    返回:
        Dict[str, Any]: 包含每个操作的执行结果，具体格式如下：
            {
                "operation_name": {
                    "utc": "调用时间戳",
                    "args": "方法参数",
                    "status": "执行状态（True/False/None）",
                    "return": "方法返回值或错误信息"
                }
            }
    """

    from pymongo import MongoClient
    mongo = MongoClient("mongodb://localhost:27017/")
    timtok_search = data_params["get"]["browser_link"].split("=")[1]
    tiktok_task = mongo["tiktok_user"][F"userinfo_task_{timtok_search}"]
    tiktok_list = mongo["tiktok_user"][F"userinfo_list_{timtok_search}"]
    tiktok_data = mongo["tiktok_user"][F"userinfo_data_{timtok_search}"]
    # 执行 TikTok 自动化操作
    if data_debug:
        data = tiktok(**data_config).call(data_params)
        data = data["search_video"]["return"]
        for f1 in data:
            f1.update(
                {"video_link": "/".join(f1["video_link"].split("/")[:-2])}
            )
            tiktok_task.update_one(
                {"video_link": f1["video_link"]},
                {"$set": f1},
                upsert=True
            )
        # data_debug = tiktok_task.insert_many(data).inserted_ids
        print(F"导入了 {len(data)} 条初始数据。")
    print(F"sleep({data_time})")
    sleep(data_time)
    print(F"sleep({data_time})")
    for f1 in tiktok_task.find(dict(), {"_id": 0}):
        f1 = {
            # "launch": None,
            "connect": None,
            "get": {"browser_link": f1["video_link"], "time_delay": 2.0},
            "user_get": None,
            "click": {"css_selector": "span.css-1ubs7lq-SpanUnit", "time_delay": 1.0},
            "user_list": {
                "css_parent": ".css-wq5jjc-DivUserListContainer",
                "css_child": "[class^=\"es616eb\"]",
                # "css_count": 10**5 // 2,
                "time_delay": 3
            },
            # "quit": None
        }
        try:
            data = tiktok(**data_config).call(f1)
            tiktok_data.update_one(
                {"user_id": data["user_get"]["return"]["user_id"]},
                {"$set": data["user_get"]["return"]},
                upsert=True
            )
            for f2 in data["user_list"]["return"]:
                tiktok_list.update_one(
                    {"followers_user": f2["followers_user"]},
                    {"$set": f2},
                    upsert=True
                )
        except Exception as e:
            print(e)
            print(data["user_get"]["return"])
        sleep(data_time)
    print("进入tiktok_list")
    for f1 in tiktok_list.find(dict(), {"_id": 0}):
        f1 = {
            # "launch": None,
            "connect": None,
            "get": {"browser_link": F'https://www.tiktok.com/@{f1["followers_user"]}', "time_delay": 2.0},
            "user_get": None,
            "click": {"css_selector": "span.css-1ubs7lq-SpanUnit", "time_delay": 1.0},
            "user_list": {
                "css_parent": ".css-wq5jjc-DivUserListContainer",
                "css_child": ".css-7fu252-StyledUserInfoLink",
                # "css_count": 10**5 // 2,
                "time_delay": 3
            },
            # "quit": None
        }
        try:
            data = tiktok(**data_config).call(f1)
            tiktok_data.update_one(
                {"user_id": data["user_get"]["return"]["user_id"]},
                {"$set": data["user_get"]["return"]},
                upsert=True
            )
            for f2 in data["user_list"]["return"]:
                tiktok_list.update_one(
                    {"followers_user": f2["followers_user"]},
                    {"$set": f2},
                    upsert=True
                )
        except Exception as e:
            print(e)
            print(data["user_get"]["return"])
        sleep(data_time)
        # print(f1)

    tiktok(**data_config).call({"connect": None, "quit": None})
    return data


if __name__ == "__main__":
    user_get()
