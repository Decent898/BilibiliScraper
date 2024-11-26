
## 项目介绍

UCAS 小组作业

合法获取b站评论弹幕等信息，通过官方api，用于UCAS某小组作业。
研究bv号随机算法，研究aid与bv号关系。
正在尝试情感分析、中文分词等方法。
拟训练弹幕风格分类模型，欢迎交流。

## 使用方法

1. 下载项目到本地
2. 安装依赖：`pip install -r requirements.txt`
3. 在`results`文件夹下的`bv_list.txt`写下需要爬取的bv号，一行一个
4. 运行`scraper_comments.py`或`scraper_danmu.py`
5. 弹幕结果保存在`bilibili_data`文件夹下，评论结果保存在`bilibili_comment_data`文件夹下

## 文件说明

`scraper_comments.py`：爬取评论
`scraper_danmu.py`：爬取弹幕
在`results`文件夹下的`bv_list.txt`写下需要爬取的bv号，一行一个
运行`scraper_comments.py`或`scraper_danmu.py`
弹幕结果保存在`bilibili_data`文件夹下，评论结果保存在`bilibili_comment_data`文件夹下
`experiment`文件夹下有`C emotion`模型测试和`wordcloud`词频分析代码，还在完善中
`utils`文件夹下有`scraper_index_bv.py`，用于获取热榜视频bv号
`utils`文件夹下有`search_bv.py`，用于搜索视频，获取bv号


## 文件结构
## 项目结构

```
BilibiliCommentScraper-main/
├── README.md
├── requirements.txt # 项目依赖
├── scraper_comment.py # 爬取评论
├── scraper_danmu.py # 爬取弹幕
├── danmu_style_genertate_model.py # 弹幕风格生成模型（未完成）
├── bilibili_comment_data/
│   ├── ***
├── bilibili_data/
│   ├── ***
├── experiment/
│   ├── cemotion/
│   │   └── cemotion_test.py # 情感分析测试
│   └── word_cloud/
│       ├── cemotion_wordcloud.py # 基于Cemotion情感词云
│       └── word_cloud.py # 基于jieba词频的词云
├── results/
│   ├── bv_list.txt # 需要爬取的bv号列表
│   ├── bv_list1.txt
│   ├── comments.json # 爬取的评论数据（测试）
│   ├── namelist.txt # 视频名称列表（测试）
│   ├── seg_result.txt # 分词结果（测试）
│   ├── video_info_results.json # 爬取的视频信息数据（测试）
│   ├── mask_image.jpg # 词云背景图
│   ├── word_freq.txt # 词频统计结果
│   ├── keyword_'e'_bilibili_bv.txt
│   ├── keyword_'e'_bilibili_videos.csv
│   ├── keyword_的_bilibili_bv.txt
│   └── keyword_的_bilibili_videos.csv
├── utils/
│   ├── test/
│   │   ├── ***
├── ├── draw_tree.py # 绘制项目结构树生成md（好玩的）
│   ├── generate_bv.py # 生成随机bv号，算法不行
│   ├── get_namelist.py # 获取bv对应视频名称
│   ├── scraper_index_bv.py # 获取热榜视频bv号
│   ├── search_bv.py # 搜索视频，获取bv号
│   ├── test_bv_date.py # 测试bv号对应日期
│   └── time_density_graph.py # 保存在keyword.csv文件的视频发布时间密度图
```

## 注意事项

1. 本项目仅供学习交流使用，请勿用于非法用途。

