import requests
import csv
from urllib.parse import quote
import time
import random
from datetime import datetime, timezone
# import tqdm # tqdm用于显示进度条
from tqdm import tqdm


def convert_to_timestamp(date_str):
    """
    将标准时间格式转换为1970年制时间戳

    :param date_str: 标准时间格式 (YYYY-MM-DD HH:MM:SS)
    :return: Unix时间戳
    """
    try:
        # 解析输入的日期时间字符串
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

        # 转换为UTC时间戳
        timestamp = int(dt.replace(tzinfo=timezone.utc).timestamp())
        return timestamp
    except ValueError:
        print("时间格式错误，请使用 YYYY-MM-DD HH:MM:SS 格式")
        return None


def get_bilibili_search_results(keyword, start_time, end_time, max_pages=10):
    """
    爬取B站搜索结果

    :param keyword: 搜索关键词
    :param start_time: 开始时间戳（1970年制）
    :param end_time: 结束时间戳（1970年制）
    :param max_pages: 最大爬取页数
    :return: 视频信息列表
    """

    encoded_keyword = quote(keyword)

    video_list = []

    # 请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Referer": "https://search.bilibili.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": "",
        "Origin": "https://search.bilibili.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }
    # tqdm用于显示进度条
    # for page in tqdm(range(1, max_pages + 1)):
    for page in range(1, max_pages + 1):
        # print(f"正在爬取第 {page} 页...")
        # tqdm.write(f"正在爬取第 {page} 页...")
        
        url = (
            f"https://api.bilibili.com/x/web-interface/search/type?"
            f"keyword={encoded_keyword}"
            f"&from_source=webtop_search&spm_id_from=333.1007&search_source=5"
            f"&search_type=video"
            f"&page={page}"
            f"&order=pubdate"
            f"&pubtime_begin_s={start_time}"
            f"&pubtime_end_s={end_time}"
        )
        # print(url)
        
        try:
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                print(f"请求失败，状态码：{response.status_code}")
                break

            data = response.json()

            if data.get("code") != 0:
                print(f"API返回错误：{data.get('message')}")
                break

            results = data.get("data", {}).get("result", [])

            if not results:
                print(f"at page {page} no results")
                break

            for video in results:
                video_info = {
                    "BV号": video.get("bvid", ""),
                    "标题": video.get("title", "")
                    .replace('<em class="keyword">', "")
                    .replace("</em>", ""),
                    "作者": video.get("author", ""),
                    "播放量": video.get("play", 0),
                    "弹幕数": video.get("video_review", 0),
                    "发布时间": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(video.get("pubdate", 0))
                    ),
                    "视频链接": f"https://www.bilibili.com/video/{video.get('bvid', '')}",
                }
                video_list.append(video_info)

            # 随机延时，避免被封
            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"发生错误：{e}")
            break

    return video_list


def save_to_csv(video_list, filename="bilibili_videos.csv"):
    """
    保存视频信息到CSV文件
    """
    try:
        keys = video_list[0].keys()
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(video_list)
        print(f"数据已保存到 {filename}")
    except Exception as e:
        print(f"保存CSV文件时发生错误：{e}")


def save_bv_to_txt(video_list, filename="bilibili_bv.txt"):
    """
    只保存BV号到txt文件
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for video in video_list:
                f.write(f"{video['BV号']}\n")
        print(f"BV号已保存到 {filename}")
    except Exception as e:
        print(f"保存BV号文件时发生错误：{e}")


def main():
    # keyword = input("搜索关键词：")

    # 输入时间范围（标准时间格式）
    # print("请输入起止时间（格式：YYYY-MM-DD HH:MM:SS）")
    # start_time_str = input("开始时间：")
    # end_time_str = input("结束时间：")
    # 最大页数
    # max_pages = int(input("请输入最大爬取页数"))
    
    # *args, *kwargs = None, None
    keyword = "1"
    start_time_str = "2024-11-01 00:00:00"
    end_time_str = "2024-11-27 23:59:59"
    max_pages = 10

    start_time = convert_to_timestamp(start_time_str)-8*60*60 # 实验发现是按照utc-8时间来计算的
    end_time = convert_to_timestamp(end_time_str)-8*60*60
    
    print(f"开始时间：{start_time}, {start_time_str}")
    print(f"结束时间：{end_time}, {end_time_str}")
    print(f"最大页数：{max_pages}")

    # 检查时间转换是否成功
    if start_time is None or end_time is None:
        return

    # video_list = get_bilibili_search_results(keyword, start_time, end_time, max_pages)

    video_list = []
    
    # for time_stride in range(start_time, end_time, 86400):

    # tqdm
    for time_stride in tqdm(range(start_time, end_time, 86400)):
        video_list += get_bilibili_search_results(keyword, time_stride, time_stride+86400, max_pages)


    print(f"共找到 {len(video_list)} 个视频")
    save_to_csv(video_list, f"results/keyword_'{keyword}'_bilibili_videos.csv")
    save_bv_to_txt(video_list, f"results/keyword_'{keyword}'_bilibili_bv.txt")


if __name__ == "__main__":
    main()
