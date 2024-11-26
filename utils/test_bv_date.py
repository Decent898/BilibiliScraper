import requests
import json
from datetime import datetime
import time

def get_video_info(bv_number):
    """
    获取B站视频信息
    参数:
        bv_number: 视频的BV号
    返回:
        包含发布日期、作者信息和播放量的字典
    """
    # 构建API URL
    url = f'https://api.bilibili.com/x/web-interface/view?bvid={bv_number}'
    
    try:
        # 发送请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # 解析JSON响应
        data = response.json()
        
        # 检查API返回状态
        if data['code'] != 0:
            return {
                'error': f"API返回错误: {data['message']}"
            }
            
        # 提取视频信息
        video_data = data['data']
        
        # 将时间戳转换为可读格式
        publish_time = datetime.fromtimestamp(video_data['pubdate'])
        
        return {
            'title': video_data['title'],
            'publish_date': publish_time.strftime('%Y-%m-%d %H:%M:%S'),
            'author': {
                'name': video_data['owner']['name'],
                'uid': video_data['owner']['mid']
            },
            'view_count': video_data['stat']['view'],
            'like_count': video_data['stat']['like'],
            'coin_count': video_data['stat']['coin'],
            'favorite_count': video_data['stat']['favorite']
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'error': f"网络请求错误: {str(e)}"
        }
    except json.JSONDecodeError as e:
        return {
            'error': f"JSON解析错误: {str(e)}"
        }
    except Exception as e:
        return {
            'error': f"未知错误: {str(e)}"
        }

def process_video_list(input_file):
    """
    从文件中读取BV号列表并处理
    参数:
        input_file: 包含BV号的文件路径
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            bv_list = [line.strip() for line in f if line.strip()]
            
        results = []
        for bv in bv_list:
            print(f"正在处理: {bv}")
            info = get_video_info(bv)
            results.append({
                'bv': bv,
                'info': info
            })
            # 添加延时避免请求过快
            time.sleep(1)
            
        # 将结果保存到文件
        with open('results/video_info_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print("处理完成，结果已保存到 results/video_info_results.json")
        
    except Exception as e:
        print(f"处理过程出错: {str(e)}")

# 使用示例
if __name__ == "__main__":
    # 处理单个视频
    # info = get_video_info("BV1xx411c7mD")
    # print(json.dumps(info, ensure_ascii=False, indent=2))
    
    # 处理文件中的多个视频
    process_video_list("bv_list1.txt")
    pass