import re
import requests
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# 配置
INPUT_FILE = 'bookmarks.html'
OUTPUT_FILE = 'data.json'
# 这里的关键词可以根据你的需要增加，用来标记可能需要代理的网站
VPN_KEYWORDS = ['google', 'youtube', 'facebook', 'twitter', 'github', 'telegram', 'wikipedia', 'medium']

def parse_via_bookmarks(html_content):
    pattern = re.compile(r'<A HREF="(.*?)".*?>(.*?)</A>')
    return pattern.findall(html_content)

def check_url(url_info):
    url, title = url_info
    is_vpn_suggest = any(k in url.lower() for k in VPN_KEYWORDS)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        # 注意：GitHub Actions 环境在国外，访问 Google 也会返回 200
        response = requests.get(url, timeout=8, headers=headers)
        status = "online" if response.status_code == 200 else "error"
    except:
        status = "offline"
    
    return {
        "title": title,
        "url": url,
        "status": status,
        "is_vpn": is_vpn_suggest,
        "check_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

def main():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Waiting for bookmarks.html upload...")
        return

    bookmarks = parse_via_bookmarks(content)
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(check_url, bookmarks))

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()