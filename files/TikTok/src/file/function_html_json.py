from os.path import isfile
from requests import get
from lxml import html
from json import dumps
from typing import Union, Dict, Any


class convert:
    def __init__(self, data: Union[str, Dict[str, Any]]):
        self.data = data

    def html_to_json(self, html_element) -> Dict[str, Any]:
        """
        将HTML元素转换为JSON格式。

        Args:
            html_element: 当前处理的HTML元素。

        Returns:
            Dict[str, Any]: 当前节点的JSON表示。
        """
        json_node = {
            "tag": html_element.tag,
            "attributes": {key: value for key, value in html_element.attrib.items()},
            "text": html_element.text.strip() if html_element.text and html_element.text.strip() else "",
            "children": []
        }
        for child in html_element:
            child_json = self.html_to_json(child)
            if isinstance(child_json, dict):  # 确保子节点是可序列化的字典
                json_node["children"].append(child_json)
        return json_node

    def json_to_html(self, json_node: Dict[str, Any]) -> str:
        """
        将JSON数据还原为HTML字符串，仅对特定的自闭合标签进行特殊处理。

        Args:
            json_node (Dict[str, Any]): JSON数据，表示HTML的树形结构。

        Returns:
            str: 还原后的HTML字符串。
        """
        attributes = " ".join(
            [f'{key}="{value}"' for key, value in json_node.get("attributes", {}).items()])
        if attributes:
            attributes = " " + attributes

        # 特殊处理的自闭合标签
        special_tags = {"br", "img", "hr", "input"}

        if json_node["tag"] in special_tags:
            # 自闭合标签
            return f"<{json_node['tag']}{attributes}/>"
        elif not json_node["children"]:
            # 有文本内容但没有子节点
            return f"<{json_node['tag']}{attributes}>{json_node['text']}</{json_node['tag']}>"
        else:
            # 有子节点
            html_string = f"<{json_node['tag']}{attributes}>"
            for child in json_node["children"]:
                html_string += self.json_to_html(child)
            html_string += f"</{json_node['tag']}>"
            return html_string

    def auto(self) -> Union[Dict[str, Any], str, None]:
        """
        自动判断输入是HTML内容还是JSON字典，并进行相应的转换。

        Returns:
            Union[Dict[str, Any], str, None]: 如果输入是HTML内容，返回JSON字典；如果输入是JSON字典，返回HTML内容；如果无法识别，返回None。
        """
        if isinstance(self.data, str):
            # 如果输入是HTML内容，转换为JSON
            html_tree = html.fromstring(self.data)
            return self.html_to_json(html_tree)
        elif isinstance(self.data, dict):
            # 如果输入是JSON字典，转换为HTML
            return self.json_to_html(self.data)
        else:
            # 如果无法识别，返回None
            return None


def file(file_path: str, content: str = None) -> Union[str, bool]:
    """
    根据参数数量执行文件读取或写入操作。
    - 如果有两个参数（文件路径和内容），则写入文件。
    - 如果只有一个参数（文件路径），则检查文件是否存在，如果存在则读取文件内容。

    Args:
        file_path (str): 文件路径。
        content (str, optional): 要写入的内容，默认为None。

    Returns:
        Union[str, bool]: 
        - 如果是写入文件，返回写入是否成功的布尔值。
        - 如果是读取文件，返回文件内容。
        - 如果路径无效或文件不存在，返回False。
    """
    if content:
        # 写入操作
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    else:
        # 读取操作
        if isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return False  # 如果文件不存在，返回 False


def fetch_html_content(url: str) -> str:
    """
    获取指定网址的HTML内容。

    Args:
        url (str): 目标网址。

    Returns:
        str: 网页的HTML内容，如果请求失败则返回None。
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = get(url, headers=headers)
        if response.status_code == 200:
            response.encoding = response.apparent_encoding
            return response.text
        print(f"请求失败，状态码：{response.status_code}")
    except Exception as e:
        print(f"请求出错：{e}")
    return None


def main():
    url = "https://www.baidu.com"  # 目标网址
    output_html_file = "output.html"  # 输出HTML文件名
    original_html_file = "original.html"  # 原始HTML文件名
    output_json_file = "output.json"  # 输出JSON文件名

    # 获取HTML内容
    original_html_content = fetch_html_content(url)
    if not original_html_content:
        print("未能获取HTML内容，请检查网络连接或网址是否正确。")
        return

    # 保存原始HTML内容
    if not file(original_html_file, original_html_content):  # 使用 file 函数保存文件
        print(f"保存原始HTML文件失败：{original_html_file}")
        return
    print(f"原始HTML内容已保存到文件：{original_html_file}")

    # 初始化转换器并处理HTML到JSON
    converter = convert(original_html_content)
    json_data = converter.auto()

    if json_data is None:
        print("无法识别输入类型。")
        return

    # 检查json_data是否是可序列化的字典
    if not isinstance(json_data, dict):
        print("生成的JSON数据不是字典类型，无法保存到文件。")
        return

    # 将JSON数据保存到文件
    try:
        json_content = dumps(
            json_data, ensure_ascii=False, indent=4)  # 将字典转换为JSON字符串
        if not file(output_json_file, json_content):  # 使用 file 函数保存JSON文件
            print(f"保存JSON文件失败：{output_json_file}")
            return
        print(f"JSON数据已保存到文件：{output_json_file}")
    except Exception as e:
        print(f"处理JSON数据时出错：{e}")
        return

    # 初始化转换器并处理JSON到HTML
    converter = convert(json_data)
    generated_html_content = converter.auto()

    if generated_html_content is None:
        print("无法识别输入类型。")
        return

    # 将还原后的HTML保存到文件
    if not file(output_html_file, generated_html_content):  # 使用 file 函数保存HTML文件
        print(f"保存生成的HTML文件失败：{output_html_file}")
        return
    print(f"生成的HTML内容已保存到文件：{output_html_file}")


if __name__ == "__main__":
    # main()
    with open("page_content.html", "r", encoding="UTF-8") as pf1:
        with open("page_content.json", "w", encoding="UTF-8") as pf2:
            pf2.write(
                dumps(
                    convert(pf1.read()).auto(),
                    indent=4, ensure_ascii=False
                )
            )
