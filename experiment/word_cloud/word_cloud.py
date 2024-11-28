import os
import json
from wordcloud import WordCloud
import jieba
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# 定义要屏蔽的关键词列表
# 去掉所有的介词人称代词
stopwords = [
    "的",
    "了",
    "和",
    "是",
    "就",
    "都",
    "而",
    "及",
    "与",
    "着",
    "被",
    "给",
    "在",
    "也",
    "之",
    "中",
    "于",
    "由",
    "等",
    "把",
    "比",
    "向",
    "对",
    "从",
    "关于",
    "至于",
    "我",
    "你",
    "他",
    "她",
    "它",
    "我们",
    "你们",
    "他们",
    "她们",
    "它们",
    "自己",
    "人家",
    "大家",
    "别人",
    "俺",
    "咱",
    "诸位",
    "各位",
    "所有人",
    "每一个",
    "这",
    "那",
    "哪",
    "此",
    "这些",
    "那些",
    "这个",
    "那个",
    "什么",
    "怎么",
    "如何",
    "哪个",
    "哪儿",
    "哪里",
    "几",
    "多少",
    "有些",
    "某个",
    "某些",
    "可以",
    "能够",
    "会",
    "可能",
    "应该",
    "必须",
    "需要",
    "要",
    "得",
    "想",
    "希望",
    "愿意",
    "打算",
    "计划",
    "准备",
    "还是",
    "或者",
    "还是",
    "要么",
    "要么",
    "很",
    "非常",
    "特别",
    "尤其",
    "有点",
    "有些",
    "稍微",
    "太",
    "过于",
    "更",
    "比较",
    "还",
    "再",
    "又",
    "也",
    "并",
    "而",
    "但",
    "然而",
    "却",
    "不过",
    "虽然",
    "尽管",
    "如果",
    "假如",
    "假若",
    "倘若",
    "要是",
    "一旦",
    "那么",
    "因此",
    "所以",
    "于是",
    "因为",
    "由于",
    "鉴于",
    "为此",
    "一个",
    "视频",
    "游戏",
    "世界",
    "就是",
    "真的",
    "一下",
    "没有",
    "喜欢",
    "",
    "json",
]

# 读取文件夹路径
folder_path = "bilibili_data"
all_comments = []

# for filename in os.listdir(folder_path):
#     if filename.endswith('.json'):
#         with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
#             data = json.load(file)
#             comments = data.get("danmaku_data", {}).get("comments", [])
#             for comment in comments:
#                 content = comment.get("content", "")
#                 all_comments.append(content)

with open("results/namelist.txt", "r", encoding="utf-8") as f:
    all_comments = f.readlines()
    # print(all_comments)

# 分词并过滤掉屏蔽的关键词
text = " ".join(all_comments)
words = [word for word in jieba.lcut(text) if word not in stopwords and len(word) > 1]

# 打印词频
word_freq = {}
for word in words:
    if word in word_freq:
        word_freq[word] += 1
    else:
        word_freq[word] = 1
# 排序
sorted_word_freq = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
# 打印词频
with open("word_freq.txt", "w", encoding="utf-8") as f:
    for word, freq in sorted_word_freq:
        f.write(f"{word}: {freq}\n")

# 生成词云


# mask_image = np.array(Image.open("mask_image.jpg"))  # 替换成您的遮罩图像路径
# # print(mask_image)
# # 显示遮罩
# plt.imshow(mask_image, cmap='gray') # 效果不好

# 生成词云
filtered_text = " ".join(words)
wordcloud = WordCloud(
    font_path="src/simsun.ttc",
    width=800,
    height=400,
    background_color="white",
    # mask=mask_image,  # 使用形状遮罩
    contour_color="black",
    contour_width=1,
).generate(filtered_text)

# 显示词云
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("Bilibili Danmaku Word Cloud with Shape Mask")
plt.savefig("word_cloud.png")
plt.show()
