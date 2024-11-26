import requests
import re
import json
import logging
from typing import Optional, Dict, Union, Tuple
from urllib.parse import parse_qs, urlparse

class BilibiliCIDFetcher:
    def __init__(self):
        """初始化CID获取器"""
        # API接口
        self.api_url = "https://api.bilibili.com/x/web-interface/view"
        self.page_url = "https://www.bilibili.com/video/{}"
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com',
            'Accept': 'application/json, text/plain, */*',
        }

    def extract_bvid(self, url: str) -> Optional[str]:
        """从URL中提取BV号"""
        # 处理完整URL
        if 'bilibili.com' in url:
            # 提取路径部分
            path = urlparse(url).path
            match = re.search(r'/(BV[a-zA-Z0-9]+)', path)
            if match:
                return match.group(1)
        # 处理纯BV号
        elif url.startswith('BV'):
            return url
        return None

    def get_cid_from_api(self, bvid: str) -> Optional[Dict]:
        """通过API获取CID"""
        try:
            params = {'bvid': bvid}
            response = requests.get(
                self.api_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 0 and 'data' in data:
                    video_data = data['data']
                    # 获取所有分P的信息
                    pages = video_data['pages']
                    result = {
                        'title': video_data['title'],
                        'pages': [{
                            'cid': page['cid'],
                            'page': page['page'],
                            'part': page['part']
                        } for page in pages]
                    }
                    return result
            
            self.logger.error(f"API请求失败: {response.status_code}")
            return None
            
        except Exception as e:
            self.logger.error(f"获取CID时发生错误: {str(e)}")
            return None

    def get_cid_from_html(self, bvid: str) -> Optional[Dict]:
        """通过网页源码获取CID"""
        try:
            url = self.page_url.format(bvid)
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # 查找页面中的视频信息
                pattern = r'<script>window\.__INITIAL_STATE__=(.*?);</script>'
                match = re.search(pattern, response.text)
                
                if match:
                    data = json.loads(match.group(1))
                    if 'videoData' in data:
                        video_data = data['videoData']
                        result = {
                            'title': video_data['title'],
                            'pages': [{
                                'cid': page['cid'],
                                'page': page['page'],
                                'part': page['part']
                            } for page in video_data['pages']]
                        }
                        return result
            
            self.logger.error("无法从HTML中提取CID")
            return None
            
        except Exception as e:
            self.logger.error(f"解析HTML时发生错误: {str(e)}")
            return None

    def get_cid(self, video_url: str, method: str = 'api') -> Optional[Dict]:
        """获取视频CID，支持API和HTML两种方式"""
        bvid = self.extract_bvid(video_url)
        if not bvid:
            self.logger.error(f"无效的视频URL或BV号: {video_url}")
            return None
            
        if method == 'api':
            return self.get_cid_from_api(bvid)
        elif method == 'html':
            return self.get_cid_from_html(bvid)
        else:
            self.logger.error(f"不支持的获取方法: {method}")
            return None

def main():
    # 使用示例
    fetcher = BilibiliCIDFetcher()
    
    # 测试视频URL（替换为实际的视频URL）
    video_url = "https://www.bilibili.com/video/BV1JfDPY2EJ3"
    
    # 使用API方法获取CID
    print("\n使用API方法获取CID:")
    result = fetcher.get_cid(video_url, method='api')
    if result:
        print(f"视频标题: {result['title']}")
        for page in result['pages']:
            print(f"P{page['page']} - {page['part']}: CID = {page['cid']}")
    
    # 使用HTML方法获取CID
    print("\n使用HTML方法获取CID:")
    result = fetcher.get_cid(video_url, method='html')
    if result:
        print(f"视频标题: {result['title']}")
        for page in result['pages']:
            print(f"P{page['page']} - {page['part']}: CID = {page['cid']}")

if __name__ == "__main__":
    main()