import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# 中文
plt.rcParams['font.family'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = False

file_name = "results/keyword_'1'_bilibili_videos.csv"

df = pd.read_csv(file_name, encoding='utf-8-sig')
df['发布时间'] = pd.to_datetime(df['发布时间']) 

plt.figure(figsize=(12, 6))

# 密度直方图
sns.histplot(data=df, x='发布时间', kde=True, bins=150)

plt.title(f'{file_name} density', fontsize=15)
plt.xlabel('发布时间', fontsize=12)
plt.ylabel('视频数量', fontsize=12)

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# plt.savefig('results/bilibili_time_density.png', dpi=300)

print("视频总数:", len(df))
print("最早发布时间:", df['发布时间'].min())
print("最晚发布时间:", df['发布时间'].max())