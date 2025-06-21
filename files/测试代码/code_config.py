from urllib.parse import urljoin
import requests
import json


def fetch_content(url):
    """访问链接并返回处理好的链接列表"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        base_url = url.rsplit('/', 1)[0] + '/'
        links = []
        for line in response.text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                absolute_url = urljoin(url, line)
                links.append(absolute_url)
        return links
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return []


def extract_non_m3u8_links(url):
    """递归提取非.m3u8链接"""
    links = fetch_content(url)
    non_m3u8_links = []
    for link in links:
        if link.endswith('.m3u8'):
            non_m3u8_links.extend(extract_non_m3u8_links(link))
        else:
            non_m3u8_links.append(link)
    return non_m3u8_links


def demo_config(tasks):
    tasks = [f1 for f1 in tasks]

    # 将任务列表写入文件
    with open('code_tasks.json', 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=4)

    print(f"已生成 {len(tasks)} 个任务并写入到 tasks.json 文件")


start_url = "https://1080p.huyall.com/play/DdwQRzra/index.m3u8"
non_m3u8_links = extract_non_m3u8_links(start_url)
demo_config(non_m3u8_links)
