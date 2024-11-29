import requests
import time
import json
import os
import logging
import csv
from typing import Dict, Optional 

class BilibiliCrawler:
    def __init__(self, save_dir: str = 'bilibili_comment_data'):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.bilibili.com",
        }

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

    def sanitize_filename(self, filename: str) -> str:
        """清理文件名中的非法字符"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()[:100]  # 限制文件名长度

    def bv_to_aid(self, bvid: str) -> Optional[Dict]:
        """将BV号转换为aid并获取视频信息"""
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        try:
            response = requests.get(url, headers=self.headers)
            data = response.json()
            if data["code"] == 0:
                return data["data"]
            else:
                self.logger.error(f"获取视频信息失败: {data['message']}")
                return None
        except Exception as e:
            self.logger.error(f"获取视频信息时发生错误: {str(e)}")
            return None

    def get_comments(self, aid: int, pages: int = 1) -> list:
        """获取视频评论"""
        all_comments = []

        for page in range(1, pages + 1):
            url = "https://api.bilibili.com/x/v2/reply/main"
            params = {"oid": aid, "type": 1, "next": page, "mode": 3}

            try:
                response = requests.get(url, headers=self.headers, params=params)
                data = response.json()

                if data["code"] == 0:
                    replies = data["data"]["replies"]
                    if not replies:
                        break

                    for reply in replies:
                        comment = {
                            "user": reply["member"]["uname"],
                            "content": reply["content"]["message"],
                            "likes": reply["like"],
                            "reply_time": time.strftime(
                                "%Y-%m-%d %H:%M:%S", time.localtime(reply["ctime"])
                            ),
                            "rpid": str(reply["rpid"]),  # 添加评论ID
                            "mid": str(reply["member"]["mid"])  # 添加用户ID
                        }
                        all_comments.append(comment)

                    self.logger.info(f"成功获取第{page}页评论")
                    time.sleep(1)  # 避免请求过快
                else:
                    self.logger.error(f"获取评论失败: {data['message']}")
                    break

            except Exception as e:
                self.logger.error(f"获取评论时发生错误: {str(e)}")
                break

        return all_comments

    def save_comments(self, comments: list, video_info: Dict, save_format: str = 'both'):
        """保存评论数据"""
        try:
            # 使用视频标题作为文件名
            base_filename = self.sanitize_filename(video_info['title'])
            
            if save_format in ['json', 'both']:
                # 保存JSON格式
                json_path = os.path.join(self.save_dir, f'{base_filename}_comments.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'video_info': {
                            'title': video_info['title'],
                            'bvid': video_info['bvid'],
                            'aid': video_info['aid'],
                            'author': video_info['owner']['name'],
                            'pub_date': time.strftime('%Y-%m-%d %H:%M:%S', 
                                                    time.localtime(video_info['pubdate']))
                        },
                        'comments_data': comments,
                        'total_comments': len(comments)
                    }, f, ensure_ascii=False, indent=2)
                self.logger.info(f"已保存JSON文件: {json_path}")
            
            if save_format in ['csv', 'both']:
                # 保存CSV格式
                csv_path = os.path.join(self.save_dir, f'{base_filename}_comments.csv')
                with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:  # 使用 utf-8-sig 编码，支持Excel打开
                    writer = csv.writer(f, escapechar='\\', quoting=csv.QUOTE_ALL)  # 添加转义字符和引号
                    # 写入表头
                    writer.writerow([
                        '视频标题', '视频BV号', '视频AV号', '作者', '发布时间',
                        '评论用户名', '评论内容', '点赞数', '评论时间', '评论ID', '用户ID'
                    ])
                    # 写入评论数据
                    for comment in comments:
                        # 处理可能包含换行符的内容
                        content = comment['content'].replace('\n', ' ').replace('\r', ' ')
                        writer.writerow([
                            video_info['title'],
                            video_info['bvid'],
                            str(video_info['aid']),
                            video_info['owner']['name'],
                            time.strftime('%Y-%m-%d %H:%M:%S', 
                                        time.localtime(video_info['pubdate'])),
                            comment['user'],
                            content,  # 使用处理过的内容
                            comment['likes'],
                            comment['reply_time'],
                            comment.get('rpid', ''),
                            comment.get('mid', '')
                        ])
                self.logger.info(f"已保存CSV文件: {csv_path}")
                
        except Exception as e:
            self.logger.error(f"保存数据失败: {str(e)}")
            raise

    def process_video(self, bvid: str, save_format: str = 'both', pages: int = 100) -> bool:
        """处理单个视频"""
        self.logger.info(f"开始处理视频: {bvid}")
        
        # 获取视频信息
        video_info = self.bv_to_aid(bvid)
        if not video_info:
            return False
            
        # 获取评论
        comments = self.get_comments(video_info['aid'], pages=pages)  # 获取100页评论
        if not comments:
            self.logger.warning(f"未获取到评论: {video_info['title']} ({bvid})")
            return False
            
        # 保存数据
        self.save_comments(comments, video_info, save_format)
        
        self.logger.info(f"视频处理完成: {video_info['title']} ({bvid})")
        return True

    def process_from_file(self, input_file: str, save_format: str = "both",pages: int = 10):
        """从文件读取BV号并处理"""
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                bv_list = [line.strip() for line in f if line.strip()]

            total = len(bv_list)
            success = 0

            for i, bvid in enumerate(bv_list, 1):
                self.logger.info(f"处理进度: {i}/{total} - {bvid}")

                if self.process_video(bvid, save_format, pages):
                    success += 1

                time.sleep(2)  # 增加延时到2秒，避免请求过快

            self.logger.info(f"处理完成，成功: {success}/{total}")

        except Exception as e:
            self.logger.error(f"处理文件失败: {str(e)}")

def main():
    crawler = BilibiliCrawler()
    input_file = "results/bv_list.txt"  # BV号列表文件
    crawler.process_from_file(input_file, save_format='both', pages=5)

if __name__ == "__main__":
    main()