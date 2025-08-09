import requests
from bs4 import BeautifulSoup
import re
import os
import schedule
import time
from datetime import datetime
import ipaddress  # 新增，用于验证IP

# 目标URL列表
urls = [
    'https://ip.164746.xyz', 
    'https://cf.090227.xyz', 
    'https://stock.hostmonit.com/CloudFlareYes',
    'https://www.wetest.vip/page/cloudflare/address_v4.html',
    'https://addressesapi.090227.xyz/ct',
    'https://addressesapi.090227.xyz/cmcc',
    'https://addressesapi.090227.xyz/cmcc-ipv6',  # 注意：此为IPv6，当前忽略
    'https://addressesapi.090227.xyz/CloudFlareYes',
    'https://addressesapi.090227.xyz/ip.164746.xyz',
    'https://ipdb.api.030101.xyz/?type=bestproxy&country=true',
    'https://ipdb.api.030101.xyz/?type=bestcf&country=true'
]

# 正则表达式用于匹配IPv4地址
ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

# headers以避免被挡
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'}

# 检查ip.txt文件是否存在,如果存在则备份
if os.path.exists('ip.txt'):
    os.rename('ip.txt', 'ip_backup.txt')

def scrape_ips():
    unique_ips = set()
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' in content_type:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text()
                    ip_matches = re.findall(ip_pattern, text)
                else:
                    ip_matches = re.findall(ip_pattern, response.text)
                
                # 验证并添加有效IP
                for ip in ip_matches:
                    try:
                        ip_obj = ipaddress.ip_address(ip)
                        if not ip_obj.is_private:  # 可选：排除私有IP
                            unique_ips.add(ip)
                    except ValueError:
                        pass
        except requests.exceptions.RequestException as e:
            print(f'[{datetime.now()}] 请求 {url} 失败: {e}')
            continue
    
    if unique_ips:
        sorted_ips = sorted(unique_ips, key=lambda ip: [int(part) for part in ip.split('.')])
        with open('ip.txt', 'w') as file:
            for ip in sorted_ips:
                file.write(ip + '\n')
        print(f'[{datetime.now()}] 已保存 {len(sorted_ips)} 个唯一IP地址到ip.txt文件。')
    else:
        print(f'[{datetime.now()}] 未找到有效的IP地址。')

def main():
    scrape_ips()
    schedule.every(1).hours.do(scrape_ips)
    print(f'[{datetime.now()}] 定时任务已启动，每小时抓取一次IP地址...')
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
