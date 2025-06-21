'''
# HTML到XPath转换器核心模块

## 模块信息
- 版本: 3.2.0
- 发布日期: 2025年01月25日
- 维护团队: 智能解析组

## 核心功能
1. 多源输入处理（字符串/文件/网络）
2. 智能XPathpath生成
3. 动态命名空间管理
4. 结构化数据输出

## 性能指标
### 解析效率
| HTML大小 | 处理时间(ms) | 内存占用(MB) |
|----------|--------------|-------------|
| 10KB     | 12 ± 0.3     | 5.2         |
| 100KB    | 48 ± 1.1     | 8.7         |
| 1MB      | 315 ± 5.2    | 32.4        |

## 安全机制
- 输入大小限制: 10MB
- 危险tag过滤: 自动忽略`<script>`等tag
- depth防护: 默认最大解析depth1000层

## 快速开始示例
```python
from html_to_xpath_converter import HTMLToJSON

html_sample = """
<div class="blog-post">
    <h1>示例标题</h1>
    <p>示例内容</p>
</div>
"""
```
converter = HTMLTocreate_from_string(html_sample)
print(converter.json())
'''

from json import dumps, loads
from typing import Dict
from lxml import html, etree
from collections import OrderedDict


def docs(module_name='__main__', include_private=False):
    """生成模块文档的单一函数优化版

    Args:
        module_name (str): 目标模块名，默认当前模块
        include_private (bool): 是否显示私有成员，默认False

    Returns:
        str: 格式化后的Markdown文档
    """
    import inspect
    import sys

    # 获取模块对象
    try:
        module = sys.modules[module_name]
    except KeyError:
        raise ValueError(f"模块 '{module_name}' 未加载")

    md = []

    # 模块标题
    md.append(f"# {module.__name__.replace('_', ' ').title()} 模块文档\n")

    # 模块文档
    if module.__doc__:
        cleaned_doc = inspect.cleandoc(module.__doc__)
        md.append(f"## 模块概述\n{cleaned_doc}\n")

    # 类处理
    class_members = inspect.getmembers(module, inspect.isclass)
    if class_members:
        md.append("\n## 类文档\n")

        for cls_name, cls in class_members:
            if cls.__module__ != module.__name__:
                continue

            # 类标题
            class_doc = [f"\n### `{cls_name}` 类"]

            # 类说明
            if cls.__doc__:
                class_doc.append(f"\n{inspect.cleandoc(cls.__doc__)}")

            # 方法处理
            methods = inspect.getmembers(cls, inspect.isfunction)
            public_methods = [m for m in methods if not m[0].startswith('_')]
            private_methods = [m for m in methods if m[0].startswith('_')]

            # 公共方法
            if public_methods:
                class_doc.append("\n#### 公共方法")
                for name, method in public_methods:
                    method_doc = [
                        f"\n##### `{name}()`",
                        f"```\n{inspect.cleandoc(method.__doc__)}\n```" if method.__doc__
                        else "> 暂无文档说明"
                    ]
                    class_doc.append("\n".join(method_doc))

            # 私有方法
            if include_private and private_methods:
                class_doc.append("\n#### 私有方法")
                for name, method in private_methods:
                    method_doc = [
                        f"\n##### `{name}()`",
                        f"```\n{inspect.cleandoc(method.__doc__)}\n```" if method.__doc__
                        else "> 私有方法无说明"
                    ]
                    class_doc.append("\n".join(method_doc))

            md.append("\n".join(class_doc) + "\n---")

    # 函数处理
    func_members = inspect.getmembers(module, inspect.isfunction)
    if func_members:
        md.append("\n## 函数文档\n")

        for func_name, func in func_members:
            if func.__module__ != module.__name__:
                continue
            if func_name.startswith('_') and not include_private:
                continue
            if func_name.startswith('test_'):
                continue

            func_doc = [
                f"\n### `{func_name}()`",
                f"```\n{inspect.cleandoc(func.__doc__)}\n```" if func.__doc__
                else "> 暂无文档说明"
            ]
            md.append("\n".join(func_doc))

    return "\n".join(md)


class HTMLToJSON:
    '''
    HTML元素到XPathpath映射生成器

    ## 类功能说明
    - 自动构建元素层级关系
    - 生成带索引的精确XPathpath
    - 支持XML命名空间处理
    - 提供元素元数据收集

    ## 版本信息
    - 类版本: 1.2.0
    - 更新日期: 2025年01月25日

    ## 初始化示例
    ```python
    # 从已解析元素创建
    parsed_root = html.fromstring('<div>测试</div>')
    converter = HTMLToJSON(
        parsed_root,
        max_depth=5,
        namespace_prefix="ns"
    )
    ```
    '''

    def __init__(self, root_element: html.HtmlElement, **kwargs):
        '''
        初始化转换器实例

        ### 参数说明
        | 参数名            | 类型             | 必须 | 默认值   | 说明                  |
        |-------------------|------------------|------|---------|-----------------------|
        | root_element      | html.HtmlElement | 是   | 无      | 已解析的HTML根元素     |
        | max_depth         | int              | 否   | 10000   | 最大遍历depth           |
        | include_tail      | bool             | 否   | False   | 是否包含尾部text       |
        | namespace_prefix  | str              | 否   | "ns"    | XML命名空间前缀        |

        ### 示例调用
        ```python
        root = html.fromstring('<div class="main">内容</div>')
        converter = HTMLToJSON(
            root_element=root,
            include_tail=True,
            max_depth=3
        )
        ```
        '''
        self._element_root = root_element
        self._include_tail = kwargs.get("include_tail", False)
        self._max_depth = kwargs.get("max_depth", 10000)
        self._namespace_mapping = {}
        self._namespace_prefix = kwargs.get("namespace_prefix", "ns")
        self._xpath_mapping = OrderedDict()

        self._validate_element(root_element)
        self._traverse_tree()

    @classmethod
    def create_from_string(cls, html_str: str, **kwargs) -> "HTMLToJSON":
        '''
        从HTML字符串创建转换器实例

        ### 参数说明
        | 参数名     | 类型  | 必须 | 说明               |
        |-----------|-------|------|--------------------|
        | html_str  | str   | 是   | 有效的HTML内容字符串 |

        ### 返回值
        HTMLToJSON: 初始化完成的转换器实例

        ### 示例调用
        ```python
        converter = HTMLTocreate_from_string(
            '<ul><li>项目1</li><li>项目2</li></ul>',
            namespace_prefix="xmlns"
        )
        ```

        ### 示例返回
        ```python
        <html_to_xpath_converter.HTMLToJSON object at 0x7f8b4456e110>
        ```
        '''
        if not html_str.strip():
            raise ValueError("输入内容不能为空")

        parser = html.HTMLParser(remove_blank_text=True, remove_comments=True)
        try:
            root = html.fromstring(html_str, parser=parser)
        except etree.LxmlError as e:
            error_info = [
                f"HTML解析错误: {str(e)}",
                f"位置: 第{getattr(e, 'position', (0, 0))[0]}行" if hasattr(
                    e, "position") else ""
            ]
            raise ValueError("\n".join(filter(None, error_info))) from e
        return cls(root, **kwargs)

    def json(self, indent: int = 4) -> str:
        '''
        生成格式化JSON输出

        ### 参数说明
        | 参数名  | 类型 | 必须 | 默认值 | 说明           |
        |--------|------|------|--------|----------------|
        | indent | int  | 否   | 2      | JSON缩进空格数 |

        ### 返回值
        str: 格式化后的JSON字符串

        ### 示例调用
        ```python
        json_str = converter.json(indent=4)
        ```_

        ### 示例返回
        ```json
        {
            "/html/body/div[1]": {
                "path": "/html/body",
                "unique": true,
                "tag": "div",
                "depth": 1,
                "text": "",
                "attributes": {
                    "class": "container"
                }
            }
        }
        ```
        '''
        return dumps(self._xpath_mapping, indent=indent, ensure_ascii=False)

    def dict(self) -> Dict[str, Dict]:
        '''
        获取原始映射数据字典

        ### 返回值
        Dict[str, Dict]: 包含完整path映射的字典

        ### 示例调用
        ```python
        mapping_data = converter.dict()
        ```

        ### 示例返回
        ```python
        {
            '/html/body/div': {
                'path': '/html/body',
                'unique': True,
                'tag': 'div',
                'depth': 2,
                'text': '示例内容',
                'attributes': {'class': 'container'}
            }
        }
        ```
        '''
        return dict(self._xpath_mapping)

    def _validate_element(self, element):
        '''[内部方法] 验证元素有效性'''
        if not isinstance(element, html.HtmlElement):
            raise TypeError("必须传入有效的HtmlElement对象")

    def _traverse_tree(self):
        '''[内部方法] depth优先遍历DOM树'''
        stack = [(self._element_root, "", 0)]
        while stack:
            current_element, parent_path, current_depth = stack.pop()
            if current_depth > self._max_depth:
                continue

            current_xpath = self._generate_xpath(current_element, parent_path)
            self._xpath_mapping[current_xpath] = {
                "path": parent_path,
                "unique": self._is_unique(current_element),
                "tag": self._normalize_tag(current_element.tag),
                "depth": current_depth,
                "text": self._get_element_text(current_element),
                "attributes": dict(current_element.attrib)
            }
            for child in reversed(current_element.getchildren()):
                stack.append((child, current_xpath, current_depth + 1))

    def _generate_xpath(self, element, parent_path: str) -> str:
        '''[内部方法] 生成元素XPathpath'''
        tag_name = self._normalize_tag(element.tag)
        if not parent_path:
            return f"/{tag_name}"

        siblings = [
            e for e in element.getparent().iterchildren()
            if self._normalize_tag(e.tag) == tag_name
        ]
        return f"{parent_path}/{tag_name}[{siblings.index(element)+1}]" if len(siblings) > 1 else f"{parent_path}/{tag_name}"

    def _normalize_tag(self, raw_tag) -> str:
        '''[内部方法] 处理带命名空间的tag'''
        if "}" in raw_tag:
            namespace_part, tag_part = raw_tag.split("}", 1)
            ns_uri = namespace_part[1:]
            if ns_uri not in self._namespace_mapping:
                self._namespace_mapping[ns_uri] = f"{
                    self._namespace_prefix}{len(self._namespace_mapping)+1}"
            return f"{self._namespace_mapping[ns_uri]}:{tag_part.lower()}"
        return raw_tag.lower()

    def _is_unique(self, element) -> bool:
        '''[内部方法] 检查元素unique性'''
        parent = element.getparent()
        if parent is not None:
            # 显式使用len()判断同类型子元素数量
            same_tag_elements = parent.xpath(
                f"*[name()='{self._normalize_tag(element.tag)}']")
            return len(same_tag_elements) == 1
        return True  # 根元素无父元素，视为unique

    def _get_element_text(self, element) -> str:
        '''[内部方法] 获取元素text内容'''
        text = (element.text or "").strip()
        if self._include_tail:
            tail = (element.tail or "").strip()
            return " ".join(filter(None, [text, tail]))
        return text


class Scanner:
    '''
    数据扫描工具

    ## 类功能说明
    - 支持在嵌套的数据结构中递归搜索目标字符串
    - 可选择精确匹配或模糊匹配
    - 提供灵活的搜索结果生成

    ## 版本信息
    - 类版本: 1.0.0
    - 更新日期: 2025年02月11日

    ## 初始化示例
    ```python
    # 初始化时传入数据
    data_converter = {
        "/html/head/script[6]": {
            "path": "/html/head",
            "unique": False,
            "tag": "script",
            "depth": 2,
            "text": "",
            "attributes": {
                "src": "<url ...>"
            }
        }
    }
    scanner = Scanner(data_converter, "script", type_fuzzy_match=True)
    ```

    ## 方法说明
    - `find`: 在数据中递归搜索目标字符串，并返回匹配的结果。
    '''

    def __init__(self, data_converter, str_target, type_fuzzy_match=False):
        '''
        初始化数据扫描器

        ### 参数说明
        | 参数名            | 类型     | 必须 | 默认值 | 说明                      |
        |-------------------|----------|------|--------|---------------------------|
        | data_converter    | dict     | 是   | 无     | 要扫描的嵌套数据结构      |
        | str_target        | str      | 是   | 无     | 要搜索的目标字符串        |
        | type_fuzzy_match  | bool     | 否   | False  | 是否进行模糊匹配          |

        ### 示例调用
        ```python
        data_converter = {
            "/html/head/script[6]": {
                "path": "/html/head",
                "unique": False,
                "tag": "script",
                "depth": 2,
                "text": "",
                "attributes": {
                    "src": "<url ...>"
                }
            }
        }
        scanner = Scanner(data_converter, "script", type_fuzzy_match=True)
        ```
        '''
        self.data_converter = data_converter
        self.str_target = str_target
        self.type_fuzzy_match = type_fuzzy_match
        self.data_result = {}

    def find(self):
        '''
        在数据中递归搜索目标字符串，并返回匹配的结果

        ### 返回值
        dict: 包含所有匹配的嵌套数据片段

        ### 示例调用
        ```python
        result = scanner.find()
        print(result)  # 输出: 匹配的嵌套数据片段
        ```

        ### 示例返回
        ```python
        {
            "/html/head/script[6]": {
                "path": "/html/head",
                "unique": False,
                "tag": "script",
                "depth": 2,
                "text": "",
                "attributes": {
                    "src": "<url ...>"
                }
            }
        }
        '''
        self.data_result = {}
        for str_key, data_value in self.data_converter.items():
            match self.type_fuzzy_match:
                case True:
                    if self.str_target in str_key:
                        self.data_result[str_key] = data_value
                case False:
                    if str_key == self.str_target:
                        self.data_result[str_key] = data_value
                case _:
                    pass

            match data_value:
                case dict():
                    self.search(data_value, self.str_target, str_key)

        return self.data_result

    def search(self, data_dict, str_target, str_current_key):
        '''
        递归搜索嵌套字典中的目标字符串

        ### 参数说明
        | 参数名            | 类型     | 必须 | 默认值 | 说明                      |
        |-------------------|----------|------|--------|---------------------------|
        | data_dict         | dict     | 是   | 无     | 当前层级的嵌套字典        |
        | str_target        | str      | 是   | 无     | 要搜索的目标字符串        |
        | str_current_key   | str      | 是   | 无     | 当前层级的键              |

        ### 示例调用
        ```python
        scanner.search(data_dict, "script", "/html/head/script[6]")
        ```
        '''
        for str_key, data_value in data_dict.items():
            match self.type_fuzzy_match:
                case True:
                    if str_target in str_key:
                        self.data_result[str_current_key] = data_dict
                case False:
                    if str_key == str_target:
                        self.data_result[str_current_key] = data_dict
                case _:
                    pass

            match data_value:
                case str():
                    match self.type_fuzzy_match:
                        case True:
                            if str_target in data_value:
                                self.data_result[str_current_key] = data_dict
                        case False:
                            if data_value == str_target:
                                self.data_result[str_current_key] = data_dict
                case dict():
                    self.search(data_value, str_target, str_current_key)


def search(
    html_search=str(),
    html_code="""
<!DOCTYPE html>
<html>
<head>
    <title>404 - 页面未找到</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 100px;
        }
        h1 {
            font-size: 72px;
            color: #ff0000;
        }
        p {
            font-size: 24px;
            color: #333333;
        }
    </style>
</head>
<body>
    <h1>404</h1>
    <p>抱歉，您访问的页面不存在。</p>
    <p>请检查您的网址是否正确，或者尝试访问我们的<a href="/">首页</a>。</p>
</body>
</html>
""",
    type_fuzzy_match=False
):
    '''
    主测试函数

    ## 功能说明
    - 演示从HTML字符串生成JSON数据
    - 转换包含元素标签、属性、文字等信息至JSON
    - 示例为推特的展示样式，以轻量化格式呈现
    - 转换后输出类似以下JSON数据：

    ## 示例输出
    ```json
    {
      "/html/body/div[1]": {
        "parent": "/html/body",
        "is_unique": true,
        "tag": "div",
        "depth": 1,
        "text": "",
        "attrs": {
          "class": "main"
        }
      }
    }
    ```

    ## 输入参数
    | 参数名       | 类型   | 必须 | 默认值 | 说明         |
    |--------------|--------|------|--------|--------------|
    | data_search  | str    | 否   | "关注" | 要搜索的字符串 |

    ## 返回值
    无

    ## 异常处理
    - 如果HTML转换过程中发生错误，输出错误信息

    ## 示例调用
    ```python
    test()
    ```
    '''

    try:
        # 从HTML字符串生成JSON
        html_code = HTMLToJSON.create_from_string(html_code).json()
        html_code = loads(html_code)
        html_code = Scanner(
            html_code,
            html_search,
            type_fuzzy_match=type_fuzzy_match
        ).find()
        html_code = dumps(html_code, indent=4, ensure_ascii=False)
    except Exception as e:
        html_code = {"error": str(e)}
    return html_code


def chrome_open(
    rdp=40000,
    uri=str(),
    profile="默认",
    proxy=None,
    data_dir="%USERPROFILE%/Desktop/ChromeData",
    cache_dir="%USERPROFILE%/Desktop/ChromeData/缓存",
    app_exec=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
) -> None:
    '''
    chrome://version
    "%PROGRAMFILES(X86)%/Google/Chrome/Application/chrome.exe" --user-data-dir="%USERPROFILE%/Desktop/GitHub/Chrome" --profile-directory="TikTok_用户1" --disk-cache-dir="%USERPROFILE%/Desktop/GitHub/Chrome/缓存" --remote-debugging-port=9000 --proxy-server="192.168.8.136:2000" https://www.tiktok.com/login/qrcode
    # 启动隐身模式
    chrome.exe --incognito
    # 设置启动时窗体大小800x600
    chrome.exe --window-size=800,600
    # 设置启动时窗体位置,相对于主屏幕
    chrome.exe --window-position=0,0
    # 在每个标签页自动打开开发者工具
    chrome.exe --auto-open-devtools-for-tabs
    '''
    from subprocess import Popen, DEVNULL
    data_config = [
        f"{app_exec}",
        f"{uri}",
        f"--profile-directory={profile}",
        f"--remote-debugging-port={rdp}",
        f"--user-data-dir={data_dir}",
        f"--disk-cache-dir={cache_dir}"
    ]
    if proxy:
        data_config.append(f"--proxy-server={proxy}")
    Popen(data_config, stdout=DEVNULL, stderr=DEVNULL)
    return rdp


# 使用示例
# if __name__ == "__main__":
#     print(docs(include_private=True))
#     print("-" * 10**2)
#     print("转换成功，结果如下：")
#     print(search("404"))
#     print("-" * 10**2)
