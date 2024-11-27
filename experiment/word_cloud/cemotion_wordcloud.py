import os
from cemotion import Cegmentor
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# 定义要屏蔽的关键词列表（保留原有的停用词列表）
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
]


def load_comments(file_path):
    """
    读取评论文件
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readlines()

def segment_and_filter_words(comments, segmenter):
    """
    分词并过滤关键词
    """
    words = []
    for comment in comments:
        # 使用 Cemotion 的分词器
        segmentation_result = segmenter.segment(comment.strip())
        
        # 过滤停用词和单字词
        filtered_words = [
            word for word in segmentation_result 
            if word not in stopwords and len(word) > 1
        ]
        
        with open("seg_result.txt", "a", encoding="utf-8") as f:
            f.write(str(segmentation_result) + "\n")
                
        
        words.extend(filtered_words)
    
    return words

def generate_word_freq(words):
    """
    生成词频统计
    """
    word_freq = Counter(words)
    return word_freq.most_common()

def save_word_freq(word_freq, output_file):
    """
    保存词频到文件
    """
    with open(output_file, "w", encoding="utf-8") as f:
        for word, freq in word_freq:
            f.write(f"{word}: {freq}\n")

def create_word_cloud(words):
    """
    生成词云
    """
    filtered_text = " ".join(words)
    
    wordcloud = WordCloud(
        font_path="results/simsun.ttc",
        width=800,
        height=400,
        background_color="white",
        contour_color="black",
        contour_width=1,
    ).generate(filtered_text)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("Bilibili Comments Word Cloud")
    plt.show()

def main():
    # 初始化分词器
    segmenter = Cegmentor()
    
    # 读取评论
    comments = load_comments("namelist.txt")
    
    # 分词和过滤
    words = segment_and_filter_words(comments, segmenter)
    
    # 生成词频
    word_freq = generate_word_freq(words)
    
    # 保存词频
    save_word_freq(word_freq, "word_freq.txt")
    
    
    # 生成词云
    create_word_cloud(words)

if __name__ == "__main__":
    main()