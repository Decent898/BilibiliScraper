import requests
import json
from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup


class BilibiliScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            "authority": "www.bilibili.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "dnt": "1",
            "pragma": "no-cache",
            "sec-ch-ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        }
        
        # 设置cookies
        # self.cookies = {
        #     "i-wanna-go-back": "-1",
        #     "DedeUserID": "364311362",
        #     "DedeUserID__ckMd5": "176f931271c106ea",
        #     "SESSDATA": "9e152dd0%2C1747375191%2C57a23%2Ab2CjBgE1MIwvuBpb4T4f7nO7S3JjhmJZyrniak5t677iThZyfGR7LbyBIakEsiib7um7ISVkVvSVNYSDh1N3d1d3ducXMyV1QzN1MwSUtJeEtabnJrX1hNdXFVUm1XRVY5TzRqZ2xKSnJCdEZ0YXJSbVFESFExeEFlb3VzSWJVR3FuLVBpOFcxbzFBIIEC",
        #     "bili_jct": "6cefe2346da7b9ca6d3928c78d5ccd5f",
        #     "buvid3": "5496E07F-7123-00EB-A9B8-28037097DFA572651infoc",
        #     "buvid4": "67976837-3742-AC70-F0B0-9FA4717EF65957671-023061610-KW7HkkBuEznCq1Vq030bPQ==",
        #     "fingerprint": "6590b8cbe9b42efcf5d03f0a9e8920c6",
        #     "buvid_fp": "6590b8cbe9b42efcf5d03f0a9e8920c6"
        # }
        
        # for cookie_name, cookie_value in self.cookies.items():
        #     self.session.cookies.set(cookie_name, cookie_value, domain='.bilibili.com')

    def get_video_info(self, url):
        """获取视频页面信息"""
        try:
            response = self.session.get(url)
            response.raise_for_status()  # 检查请求是否成功
            
            # 设置正确的编码
            response.encoding = 'utf-8'
            
            # 提取视频信息
            # 使用正则表达式提取初始状态数据
            initial_state = re.search(r'window\.__INITIAL_STATE__=({.*?});', response.text)
            if initial_state:
                video_data = json.loads(initial_state.group(1))
                return {
                    'status': 'success',
                    'html': response.text,
                    'video_data': video_data
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to extract video information'
                }
            
        except requests.RequestException as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def extract_video_details(self, video_data):
        """从视频数据中提取详细信息"""
        try:
            if 'videoData' in video_data:
                video_info = video_data['videoData']
                return {
                    'title': video_info.get('title', ''),
                    'description': video_info.get('desc', ''),
                    'owner': video_info.get('owner', {}).get('name', ''),
                    'view_count': video_info.get('stat', {}).get('view', 0),
                    'like_count': video_info.get('stat', {}).get('like', 0),
                    'coin_count': video_info.get('stat', {}).get('coin', 0),
                    'favorite_count': video_info.get('stat', {}).get('favorite', 0)
                }
        except Exception as e:
            return {
                'error': f'Failed to extract video details: {str(e)}'
            }

def main():
    # 创建爬虫实例
    scraper = BilibiliScraper()
    
    # 目标视频URL
    video_url = "https://www.bilibili.com/video/BV1hryGYzEC1/?vd_source=48ef35e035476d811e9bed74ea785de1"
    
    # 获取视频信息
    result = scraper.get_video_info(video_url)
    
    if result['status'] == 'success':
        # 提取视频详细信息
        if 'video_data' in result:
            details = scraper.extract_video_details(result['video_data'])
            print("\n视频详细信息:")
            for key, value in details.items():
                print(f"{key}: {value}")
                
        # 每条评论是有规律的：/html/body/div[2]/div[2]/div[1]/div[8]/bili-comments//div[2]/div[2]/bili-comment-thread-renderer[x]//bili-comment-renderer//div/div/div[2]/bili-rich-text//p/span，x从1-100
        # 获取评论/html/body/div[2]/div[2]/div[1]/
        
        # xml = etree.HTML(result['html'])
        # comments = xml.xpath('//div[@class="comment-item"]')
        
            
        # 保存视频信息到文件
            
        # 保存原始HTML到文件
        with open('bilibili_video.html', 'w', encoding='utf-8') as f:
            f.write(result['html'])
        print("\n原始HTML已保存到 bilibili_video.html")
    else:
        print(f"获取视频信息失败: {result['message']}")

if __name__ == "__main__":
    main()