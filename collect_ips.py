import requests
from bs4 import BeautifulSoup
import re
import os
import schedule
import time
from datetime import datetime

# 目标URL列表
urls = [
    'https://ip.164746.xyz', 
    'https://cf.090227.xyz', 
    'https://stock.hostmonit.com/CloudFlareYes',
    'https://www.wetest.vip/page/cloudflare/address_v4.html',
    'https://addressesapi.090227.xyz/ct',
    'https://addressesapi.090227.xyz/cmcc',
    'https://addressesapi.090227.xyz/cmcc-ipv6',
    'https://addressesapi.090227.xyz/CloudFlareYes',
    'https://addressesapi.090227.xyz/ip.164746.xyz',
    'https://ipdb.api.030101.xyz/?type=bestproxy&country=true',
    'https://ipdb.api.030101.xyz/?type=bestcf&country=true'
]

# 正则表达式用于匹配IP地址
ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

# 检查ip.txt文件是否存在,如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

def scrape_ips():
    # 使用集合存储IP地址实现自动去重
    unique_ips = set()
    
    for url in urls:
        try:
            # 发送HTTP请求获取网页内容
            response = requests.get(url, timeout=5)
            
            # 确保请求成功
            if response.status_code == 200:
                # 获取网页的文本内容
                html_content = response.text
                
                # 使用正则表达式查找IP地址
                ip_matches = re.findall(ip_pattern, html_content, re.IGNORECASE)
                
                # 将找到的IP添加到集合中（自动去重）
                unique_ips.update(ip_matches)
        except requests.exceptions.RequestException as e:
            print(f'[{datetime.now()}] 请求 {url} 失败: {e}')
            continue
    
    # 将去重后的IP地址按数字顺序排序后写入文件
    if unique_ips:
        # 按IP地址的数字顺序排序（非字符串顺序）
        sorted_ips = sorted(unique_ips, key=lambda ip: [int(part) for part in ip.split('.')])
        
        # 检查ip.txt文件是否存在,如果存在则删除它
        if os.path.exists('ip.txt'):
            os.remove('ip.txt')
        
        with open('ip.txt', 'w') as file:
            for ip in sorted_ips:
                file.write(ip + '\n')
        print(f'[{datetime.now()}] 已保存 {len(sorted_ips)} 个唯一IP地址到ip.txt文件。')
    else:
        print(f'[{datetime.now()}] 未找到有效的IP地址。')

def main():
    # 立即运行一次
    scrape_ips()
    
    # 设置定时任务，每小时运行一次（可根据需要调整时间间隔）
    schedule.every(1).hours.do(scrape_ips)
    
    print(f'[{datetime.now()}] 定时任务已启动，每小时抓取一次IP地址...')
    
    # 保持程序运行，检查并执行定时任务
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次任务

if __name__ == "__main__":
    main()
