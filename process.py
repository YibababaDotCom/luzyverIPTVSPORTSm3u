import requests
import re
from concurrent.futures import ThreadPoolExecutor

# 配置信息
SOURCE_URL = "https://raw.githubusercontent.com/luzyver/IPTV/refs/heads/main/SPORTS.m3u"
OUTPUT_FILE = "iptv_links.txt"
PLAYER_PREFIX = "https://yibababa.com/player/tcplayer/?url="

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Referer': 'https://cdnlivetv.tv/'
}

def is_live_event(name):
    # 过滤包含日期时间的频道
    date_pattern = r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)|\d{1,2}:\d{2}\s?(AM|PM)'
    return bool(re.search(date_pattern, name, re.IGNORECASE))

def validate_and_format(item):
    name, link = item
    if is_live_event(name.strip()):
        return None
    
    try:
        # 使用 HEAD 请求快速验证，设置超时
        response = requests.head(link.strip(), timeout=5, allow_redirects=True, headers=HEADERS)
        if response.status_code == 200:
            return f"{name.strip()},{PLAYER_PREFIX}{link.strip()}"
    except Exception:
        pass
    return None

def main():
    try:
        response = requests.get(SOURCE_URL, timeout=15)
        content = response.text
        
        # 匹配频道名称和链接
        pattern = r'#EXTINF:-1.*?,(.*?)\n(?:#.*?\n)*(https?://\S+)'
        items = re.findall(pattern, content)
        
        print(f"检测到 {len(items)} 个候选频道，开始并发验证...")
        
        # 使用线程池并发检测，显著提高速度
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(validate_and_format, items))
            
        # 过滤 None 值并保存
        valid_links = [r for r in results if r]
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(valid_links) + "\n")
            
        print(f"处理完成，共保存 {len(valid_links)} 个有效频道")
        
    except Exception as e:
        print(f"运行发生错误: {e}")
        exit(1)

if __name__ == "__main__":
    main()
