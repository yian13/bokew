import re
import requests
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# 配置
INPUT_FILE = 'bookmarks.html'
OUTPUT_FILE = 'data.json'
# 容易被墙的关键词，手动标记 VPN
VPN_KEYWORDS = ['google', 'youtube', 'facebook', 'twitter', 'github', 'telegram', 'wikipedia', 'instagram']

def parse_via_bookmarks(html_content):
    """解析 Via 导出的标准书签格式"""
    pattern = re.compile(r'<A HREF="(.*?)".*?>(.*?)</A>')
    return pattern.findall(html_content)

def check_url(url_info):
    url, title = url_info
    is_vpn_suggest = any(k in url.lower() for k in VPN_KEYWORDS)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        # GitHub Action 在国外，timeout 设长一点
        response = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
        status = "online" if response.status_code < 400 else "error"
        code = response.status_code
    except:
        status = "offline"
        code = 0
    
    return {
        "title": title,
        "url": url,
        "status": status,
        "code": code,
        "is_vpn": is_vpn_suggest,
        "check_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

def main():
    # 解决编码问题的关键逻辑
    content = None
    for enc in ['utf-8', 'gbk', 'utf-8-sig', 'latin-1']:
        try:
            with open(INPUT_FILE, 'r', encoding=enc) as f:
                content = f.read()
                print(f"成功使用 {enc} 编码读取文件")
                break
        except Exception:
            continue

    if not content:
        print("无法读取书签文件，请确认 bookmarks.html 存在。")
        return

    bookmarks = parse_via_bookmarks(content)
    print(f"开始检测 {len(bookmarks)} 个链接...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_url, bookmarks))

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print("同步成功！")

if __name__ == "__main__":
    main()
