import requests
import xml.etree.ElementTree as ET
import json
import csv
import os
import logging
from datetime import datetime
import time
import re
from typing import Dict, Optional, List, Tuple

class BilibiliUpScraper:
    def __init__(self, save_dir: str = 'bilibili_data'):
        """初始化爬虫"""
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(save_dir, 'scraper.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # API URLs
        self.up_info_url = "https://api.bilibili.com/x/space/acc/info"
        self.up_videos_url = "https://api.bilibili.com/x/space/arc/search"
        self.video_info_url = "https://api.bilibili.com/x/web-interface/view"
        self.danmaku_url = "https://comment.bilibili.com/{}.xml"
        
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com'
        }

    def get_up_info(self, mid: str) -> Optional[Dict]:
        """获取UP主信息"""
        try:
            params = {'mid': mid}
            response = requests.get(
                self.up_info_url,
                params=params,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 0:
                    return {
                        'name': data['data']['name'],
                        'mid': mid
                    }
            self.logger.error(f"获取UP主信息失败: {mid}")
            return None
            
        except Exception as e:
            self.logger.error(f"获取UP主信息异常: {mid}, 错误: {str(e)}")
            return None

    def get_up_videos(self, mid: str) -> List[Dict]:
        """获取UP主所有视频信息"""
        videos = []
        page = 1
        page_size = 50
        
        try:
            while True:
                params = {
                    'mid': mid,
                    'ps': page_size,
                    'tid': 0,
                    'pn': page,
                    'order': 'pubdate'
                }
                
                response = requests.get(
                    self.up_videos_url,
                    params=params,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['code'] == 0:
                        vlist = data['data']['list']['vlist']
                        if not vlist:  # 没有更多视频了
                            break
                            
                        for video in vlist:
                            videos.append({
                                'bvid': video['bvid'],
                                'title': video['title'],
                                'created': video['created']
                            })
                            
                        page += 1
                        time.sleep(1)  # 避免请求过快
                    else:
                        self.logger.error(f"获取视频列表失败: {mid}, 页码: {page}")
                        break
                else:
                    self.logger.error(f"获取视频列表请求失败: {mid}, 页码: {page}")
                    break
                    
        except Exception as e:
            self.logger.error(f"获取视频列表异常: {mid}, 错误: {str(e)}")
            
        return videos

    def get_video_info(self, bvid: str) -> Optional[Dict]:
        """获取视频信息，包括cid"""
        try:
            params = {'bvid': bvid}
            response = requests.get(
                self.video_info_url,
                params=params,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 0:
                    return {
                        'title': data['data']['title'],
                        'cid': data['data']['cid'],
                        'bvid': bvid
                    }
            return None
            
        except Exception as e:
            self.logger.error(f"获取视频信息异常: {bvid}, 错误: {str(e)}")
            return None

    def get_danmaku(self, cid: str) -> Optional[str]:
        """获取弹幕XML内容"""
        try:
            url = self.danmaku_url.format(cid)
            response = requests.get(url, headers=self.headers)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                return response.text
            return None
            
        except Exception as e:
            self.logger.error(f"获取弹幕异常: {cid}, 错误: {str(e)}")
            return None

    def parse_xml(self, xml_content: str) -> Optional[Dict]:
        """解析XML格式的弹幕内容"""
        try:
            root = ET.fromstring(xml_content)
            
            info = {
                'chatserver': root.find('chatserver').text if root.find('chatserver') is not None else '',
                'chatid': root.find('chatid').text if root.find('chatid') is not None else '',
                'mission': root.find('mission').text if root.find('mission') is not None else '',
                'maxlimit': root.find('maxlimit').text if root.find('maxlimit') is not None else '',
                'state': root.find('state').text if root.find('state') is not None else '',
                'real_name': root.find('real_name').text if root.find('real_name') is not None else '',
                'source': root.find('source').text if root.find('source') is not None else '',
                'comments': []
            }
            
            for d in root.findall('d'):
                p = d.get('p', '').split(',')
                if len(p) >= 8:
                    comment = {
                        'time': float(p[0]),
                        'type': int(p[1]),
                        'size': int(p[2]),
                        'color': int(p[3]),
                        'timestamp': int(p[4]),
                        'pool': int(p[5]),
                        'user_hash': p[6],
                        'dmid': p[7],
                        'content': d.text
                    }
                    info['comments'].append(comment)
            
            return info
            
        except Exception as e:
            self.logger.error(f"解析XML失败: {str(e)}")
            return None

    def sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除非法字符"""
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        if len(filename) > 200:
            filename = filename[:197] + '...'
        return filename

    def save_data(self, data: Dict, video_info: Dict, up_info: Dict, save_format: str = 'both'):
        """保存弹幕数据"""
        try:
            # 创建UP主专属文件夹
            up_dir = os.path.join(self.save_dir, self.sanitize_filename(up_info['name']))
            if not os.path.exists(up_dir):
                os.makedirs(up_dir)
            
            # 使用视频标题作为文件名
            base_filename = self.sanitize_filename(video_info['title'])
            
            if save_format in ['json', 'both']:
                json_path = os.path.join(up_dir, f'{base_filename}.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'up_info': up_info,
                        'video_info': video_info,
                        'danmaku_data': data
                    }, f, ensure_ascii=False, indent=2)
                    
            if save_format in ['csv', 'both']:
                csv_path = os.path.join(up_dir, f'{base_filename}.csv')
                with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'UP主', 'UP主ID', '视频标题', '视频BV号', 
                        '弹幕出现时间', '类型', '字体大小', '颜色', 
                        '发送时间', '弹幕池', '用户哈希', '弹幕ID', '弹幕内容'
                    ])
                    for comment in data['comments']:
                        writer.writerow([
                            up_info['name'],
                            up_info['mid'],
                            video_info['title'],
                            video_info['bvid'],
                            comment['time'],
                            comment['type'],
                            comment['size'],
                            comment['color'],
                            datetime.fromtimestamp(comment['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                            comment['pool'],
                            comment['user_hash'],
                            comment['dmid'],
                            comment['content']
                        ])
                        
        except Exception as e:
            self.logger.error(f"保存数据失败: {str(e)}")

    def process_up_videos(self, mid: str, save_format: str = 'both'):
        """处理UP主的所有视频"""
        # 获取UP主信息
        up_info = self.get_up_info(mid)
        if not up_info:
            return
            
        self.logger.info(f"开始处理UP主: {up_info['name']} (mid: {mid})")
        
        # 获取所有视频列表
        videos = self.get_up_videos(mid)
        self.logger.info(f"共获取到 {len(videos)} 个视频")
        
        # 处理每个视频
        for i, video in enumerate(videos, 1):
            self.logger.info(f"处理视频 {i}/{len(videos)}: {video['title']}")
            
            # 获取视频详细信息
            video_info = self.get_video_info(video['bvid'])
            if not video_info:
                continue
                
            # 获取弹幕
            xml_content = self.get_danmaku(str(video_info['cid']))
            if not xml_content:
                continue
                
            # 解析弹幕
            danmaku_data = self.parse_xml(xml_content)
            if not danmaku_data:
                continue
                
            # 保存数据
            self.save_data(danmaku_data, video_info, up_info, save_format)
            
            # 添加延时
            time.sleep(1)
            
        self.logger.info(f"UP主 {up_info['name']} 的视频处理完成")

def main():
    # 使用示例
    scraper = BilibiliUpScraper()
    
    # UP主mid
    up_mid = "134019082"  # 替换为实际的UP主mid
    
    # 开始处理
    scraper.process_up_videos(up_mid)

if __name__ == "__main__":
    main()