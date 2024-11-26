import requests
import xml.etree.ElementTree as ET
import json
import csv
import os
import logging
from datetime import datetime
from typing import Dict, Optional, List, Tuple
import time
import re

class BilibiliScraper:
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
        self.video_info_url = "https://api.bilibili.com/x/web-interface/view"
        self.danmaku_url = "https://comment.bilibili.com/{}.xml"
        
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com'
        }

    def get_video_info(self, bvid: str) -> Optional[Dict]:
        """获取视频信息，包括cid和标题"""
        try:
            params = {'bvid': bvid}
            response = requests.get(
                self.video_info_url, 
                params=params, 
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 0:  # 请求成功
                    return {
                        'title': data['data']['title'],
                        'cid': data['data']['cid'],
                        'bvid': bvid
                    }
                else:
                    self.logger.error(f"获取视频信息失败: {bvid}, 错误码: {data['code']}")
            else:
                self.logger.error(f"获取视频信息失败: {bvid}, 状态码: {response.status_code}")
                
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
            else:
                self.logger.error(f"获取弹幕失败: {cid}, 状态码: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"获取弹幕异常: {cid}, 错误: {str(e)}")
        
        return None

    def parse_xml(self, xml_content: str) -> Dict:
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
        # 移除或替换Windows文件名中的非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        # 限制文件名长度
        if len(filename) > 200:
            filename = filename[:197] + '...'
        return filename

    def save_data(self, data: Dict, video_info: Dict, save_format: str = 'both'):
        """保存弹幕数据"""
        try:
            # 使用视频标题作为文件名
            base_filename = self.sanitize_filename(video_info['title'])
            
            if save_format in ['json', 'both']:
                # 保存JSON格式
                json_path = os.path.join(self.save_dir, f'{base_filename}.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'video_info': video_info,
                        'danmaku_data': data
                    }, f, ensure_ascii=False, indent=2)
                self.logger.info(f"已保存JSON文件: {json_path}")
            
            if save_format in ['csv', 'both']:
                # 保存CSV格式
                csv_path = os.path.join(self.save_dir, f'{base_filename}.csv')
                with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        '视频标题', '视频BV号', '弹幕出现时间', '类型', '字体大小', 
                        '颜色', '发送时间', '弹幕池', '用户哈希', '弹幕ID', '弹幕内容'
                    ])
                    for comment in data['comments']:
                        writer.writerow([
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
                self.logger.info(f"已保存CSV文件: {csv_path}")
                
        except Exception as e:
            self.logger.error(f"保存数据失败: {str(e)}")

    def process_video(self, bvid: str, save_format: str = 'both') -> bool:
        """处理单个视频"""
        self.logger.info(f"开始处理视频: {bvid}")
        
        # 获取视频信息
        video_info = self.get_video_info(bvid)
        if not video_info:
            return False
            
        # 获取弹幕
        xml_content = self.get_danmaku(str(video_info['cid']))
        if not xml_content:
            return False
            
        # 解析弹幕
        danmaku_data = self.parse_xml(xml_content)
        if not danmaku_data:
            return False
            
        # 保存数据
        self.save_data(danmaku_data, video_info, save_format)
        
        self.logger.info(f"视频处理完成: {video_info['title']} ({bvid})")
        return True

    def process_from_file(self, input_file: str, save_format: str = 'both'):
        """从文件读取BV号并处理"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                bv_list = [line.strip() for line in f if line.strip()]
            
            total = len(bv_list)
            success = 0
            
            for i, bvid in enumerate(bv_list, 1):
                self.logger.info(f"处理进度: {i}/{total} - {bvid}")
                
                if self.process_video(bvid, save_format):
                    success += 1
                    
                # 添加延时，避免请求过快
                time.sleep(1)
            
            self.logger.info(f"处理完成，成功: {success}/{total}")
            
        except Exception as e:
            self.logger.error(f"处理文件失败: {str(e)}")

def main():
    # 使用示例
    scraper = BilibiliScraper()
    
    # 从文件读取BV号并处理
    input_file = "results/bv_list.txt"  # BV号列表文件
    scraper.process_from_file(input_file, save_format='both')

if __name__ == "__main__":
    main()