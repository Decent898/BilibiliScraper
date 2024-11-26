import os
import re
import csv
import time
import random
import requests
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer, 
    DataCollatorForLanguageModeling
)
from datasets import load_dataset

class BilibiliDanmakuCrawler:
    def __init__(self, keyword, max_videos=10, max_danmaku=1000):
        """
        B站弹幕爬虫
        
        Args:
            keyword (str): 搜索关键词
            max_videos (int): 最大爬取视频数
            max_danmaku (int): 最大爬取弹幕数
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'https://www.bilibili.com'
        }
        self.keyword = keyword
        self.max_videos = max_videos
        self.max_danmaku = max_danmaku
    
    def search_videos(self):
        """搜索相关视频"""
        search_url = 'https://api.bilibili.com/x/web-interface/search/type'
        params = {
            'search_type': 'video',
            'keyword': self.keyword,
            'order': 'totalrank'
        }
        try:
            response = requests.get(search_url, params=params, headers=self.headers)
            videos = response.json()['data']['result']
            return [video['bvid'] for video[:self.max_videos]]
        except Exception as e:
            print(f"搜索视频失败: {e}")
            return []
    
    def get_danmaku(self, bvid):
        """获取单个视频弹幕"""
        try:
            # 获取cid
            info_url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
            cid = requests.get(info_url, headers=self.headers).json()['data']['cid']
            
            # 获取弹幕
            danmaku_url = f'https://api.bilibili.com/x/v1/dm/list.so?oid={cid}'
            response = requests.get(danmaku_url, headers=self.headers)
            
            # 解析弹幕
            danmakus = re.findall(r'<d.*?>(.*?)</d>', response.text)
            return danmakus
        except Exception as e:
            print(f"获取{bvid}弹幕失败: {e}")
            return []
    
    def crawl_danmaku(self):
        """批量爬取弹幕"""
        all_danmakus = []
        videos = self.search_videos()
        
        for bvid in videos:
            danmakus = self.get_danmaku(bvid)
            all_danmakus.extend(danmakus)
            
            # 控制总弹幕数量
            if len(all_danmakus) >= self.max_danmaku:
                break
            
            # 避免请求过快
            time.sleep(random.uniform(1, 3))
        
        return all_danmakus[:self.max_danmaku]
    
    def save_danmaku(self, danmakus, filename='danmaku.csv'):
        """保存弹幕到CSV"""
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Danmaku'])
            for danmaku in danmakus:
                writer.writerow([danmaku])
        print(f"已保存 {len(danmakus)} 条弹幕到 {filename}")

class DanmakuModelTrainer:
    def __init__(self, model_name='gpt2-chinese', data_path='danmaku.csv'):
        """
        弹幕模型训练器
        
        Args:
            model_name (str): 基础模型名称
            data_path (str): 训练数据路径
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.data_path = data_path
        
        # 设置特殊token
        self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def prepare_dataset(self):
        """准备训练数据"""
        dataset = load_dataset('csv', data_files=self.data_path)
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples['Danmaku'], 
                truncation=True, 
                max_length=128
            )
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        return tokenized_dataset
    
    def train(self, output_dir='./danmaku_model'):
        """训练模型"""
        # 准备数据和数据收集器
        tokenized_dataset = self.prepare_dataset()
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, 
            mlm=False
        )
        
        # 训练参数
        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            save_steps=10_000,
            save_total_limit=2,
        )
        
        # 训练器
        trainer = Trainer(
            model=self.model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=tokenized_dataset['train']
        )
        
        # 开始训练
        trainer.train()
        trainer.save_model()
    
    def generate_danmaku(self, prompt, max_length=50):
        """
        生成弹幕
        
        Args:
            prompt (str): 生成提示
            max_length (int): 最大生成长度
        
        Returns:
            str: 生成的弹幕
        """
        inputs = self.tokenizer(prompt, return_tensors='pt')
        outputs = self.model.generate(
            inputs.input_ids, 
            max_length=max_length,
            num_return_sequences=5,
            temperature=0.7
        )
        
        generated_danmakus = [
            self.tokenizer.decode(output, skip_special_tokens=True) 
            for output in outputs
        ]
        return generated_danmakus

def main():
    # 设置随机种子
    torch.manual_seed(42)
    
    # 选择领域关键词
    keywords = ['数码', '科技', '游戏', '动漫']
    
    for keyword in keywords:
        # 爬取弹幕
        crawler = BilibiliDanmakuCrawler(keyword)
        danmakus = crawler.crawl_danmaku()
        crawler.save_danmaku(danmakus, f'{keyword}_danmaku.csv')
        
        # 训练模型
        trainer = DanmakuModelTrainer(
            data_path=f'{keyword}_danmaku.csv'
        )
        trainer.train(output_dir=f'./{keyword}_danmaku_model')
        
        # 生成示例
        print(f"\n{keyword}领域弹幕生成示例:")
        generated_danmakus = trainer.generate_danmaku(keyword)
        for i, danmaku in enumerate(generated_danmakus, 1):
            print(f"{i}. {danmaku}")

if __name__ == '__main__':
    main()