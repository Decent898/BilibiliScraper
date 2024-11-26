import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import csv
import os
import logging
from typing import List, Dict, Optional
import time
import random
from fake_useragent import UserAgent

class BilibiliDanmaku:
    def __init__(self, save_dir: str = 'danmaku_data'):
        """初始化弹幕爬取器"""
        self.base_url = "https://comment.bilibili.com/{}.xml"
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(save_dir, 'danmaku.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 初始化 User-Agent 生成器
        self.ua = UserAgent()
        
    def get_headers(self):
        """生成随机请求头"""
        return {
            'User-Agent': self.ua.random,
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://www.bilibili.com',
            'Referer': 'https://www.bilibili.com/',
            'Connection': 'keep-alive'
        }
    
    def get_danmaku(self, video_id: str, max_retries: int = 3) -> Optional[str]:
        """获取视频弹幕XML内容，带重试机制"""
        retry_count = 0
        while retry_count < max_retries:
            try:
                url = self.base_url.format(video_id)
                # 使用随机请求头
                headers = self.get_headers()
                
                # 添加随机延时
                time.sleep(random.uniform(1, 3))
                
                response = requests.get(url, headers=headers, timeout=10)
                response.encoding = 'utf-8'
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 412:
                    self.logger.warning(f"请求被拦截(412)，正在进行第{retry_count + 1}次重试")
                    retry_count += 1
                    # 遇到412时等待更长时间
                    time.sleep(random.uniform(3, 5))
                else:
                    self.logger.error(f"获取弹幕失败: {video_id}, 状态码: {response.status_code}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"请求异常: {video_id}, 错误: {str(e)}")
                retry_count += 1
                time.sleep(random.uniform(2, 4))
                
        self.logger.error(f"达到最大重试次数，获取弹幕失败: {video_id}")
        return None
    
    def parse_xml(self, xml_content: str) -> Dict:
        """解析XML内容"""
        try:
            root = ET.fromstring(xml_content)
            
            # 获取基本信息
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
            
            # 解析所有弹幕
            for d in root.findall('d'):
                p = d.get('p', '').split(',')
                if len(p) >= 8:
                    comment = {
                        'time': float(p[0]),  # 弹幕出现时间
                        'type': int(p[1]),    # 弹幕类型
                        'size': int(p[2]),    # 字体大小
                        'color': int(p[3]),   # 颜色
                        'timestamp': int(p[4]), # 发送时间戳
                        'pool': int(p[5]),    # 弹幕池
                        'user_hash': p[6],    # 用户哈希
                        'dmid': p[7],         # 弹幕ID
                        'content': d.text     # 弹幕内容
                    }
                    info['comments'].append(comment)
            
            return info
            
        except Exception as e:
            self.logger.error(f"解析XML失败: {str(e)}")
            return None
    
    def save_to_json(self, data: Dict, video_id: str):
        """保存为JSON格式"""
        try:
            filename = os.path.join(self.save_dir, f'danmaku_{video_id}.json')
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"弹幕数据已保存到: {filename}")
        except Exception as e:
            self.logger.error(f"保存JSON失败: {str(e)}")
    
    def save_to_csv(self, data: Dict, video_id: str):
        """保存为CSV格式"""
        try:
            filename = os.path.join(self.save_dir, f'danmaku_{video_id}.csv')
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                # 写入头部
                writer.writerow(['出现时间', '类型', '字体大小', '颜色', '发送时间', '弹幕池', '用户哈希', '弹幕ID', '内容'])
                # 写入数据
                for comment in data['comments']:
                    writer.writerow([
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
            self.logger.info(f"弹幕数据已保存到: {filename}")
        except Exception as e:
            self.logger.error(f"保存CSV失败: {str(e)}")
    
    def process_video(self, video_id: str, save_format: str = 'both'):
        """处理单个视频的弹幕"""
        self.logger.info(f"开始处理视频弹幕: {video_id}")
        
        # 获取弹幕XML
        xml_content = self.get_danmaku(video_id)
        if not xml_content:
            return
        
        # 解析XML
        data = self.parse_xml(xml_content)
        if not data:
            return
            
        # 保存数据
        if save_format in ['json', 'both']:
            self.save_to_json(data, video_id)
        if save_format in ['csv', 'both']:
            self.save_to_csv(data, video_id)
            
        return data

def main():
    # 使用示例
    danmaku = BilibiliDanmaku()
    
    # 可以处理多个视频ID
    video_ids = ['123072475','26631471312']  # 替换为实际的视频ID
    
    for video_id in video_ids:
        data = danmaku.process_video(video_id)
        if data:
            print(f"视频 {video_id} 共获取到 {len(data['comments'])} 条弹幕")

if __name__ == "__main__":
    main()