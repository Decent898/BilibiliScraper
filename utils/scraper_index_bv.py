import requests
import re
import time
import random

class BilibiliCrawler:
    def __init__(self, proxy=None):
        """
        初始化爬虫，增加反反爬策略
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': 'buvid3=123456; _uuid=randomstring'  # 添加模拟Cookie
        }
        self.proxy = proxy
    
    def crawl_homepage_bvs(self, count=50, max_retries=3):
        """
        多策略爬取B站主页视频BV号
        
        Args:
            count (int): 需要获取的BV号数量
            max_retries (int): 最大重试次数
        
        Returns:
            list: BV号列表
        """
        bvs = []
        urls_to_try = [
            'https://www.bilibili.com',
            'https://www.bilibili.com/index/',
            'https://www.bilibili.com/v/popular/'
        ]
        
        for attempt in range(max_retries):
            try:
                for url in urls_to_try:
                    # 随机延迟
                    # time.sleep(random.uniform(1, 3))
                    
                    # 发送请求获取内容
                    response = requests.get(
                        url, 
                        headers=self.headers,
                        proxies=self.proxy,
                        timeout=15,
                        allow_redirects=True
                    )
                    # time.sleep(random.uniform(3, 5))
                    # 尝试多种正则匹配模式
                    patterns = [
                        r'href="//www\.bilibili\.com/video/(BV[a-zA-Z0-9]{10})/"',
                        r'/video/(BV[a-zA-Z0-9]{10})/',
                        r'BV[a-zA-Z0-9]{10}'
                    ]
                    
                    for pattern in patterns:
                        found_bvs = re.findall(pattern, response.text)
                        bvs.extend(found_bvs)
                    
                    # 去重
                    bvs = list(set(bvs))
                    
                    # 如果找到足够数量的BV号，直接返回
                    if len(bvs) >= count:
                        return bvs[:count]
                
            except Exception as e:
                print(f"第 {attempt+1} 次尝试失败: {e}")
        
        return bvs[:count]

# 使用示例
if __name__ == '__main__':
    crawler = BilibiliCrawler()
    
    # 爬取BV号
    bv_list = crawler.crawl_homepage_bvs(count=100)
    
    print(f"爬取的 {len(bv_list)} 个BV号:")
    for bv in bv_list:
        print(bv)