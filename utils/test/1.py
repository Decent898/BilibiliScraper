from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import logging
from datetime import datetime

class BilibiliCommentsScraper:
    def __init__(self):
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # 设置Chrome选项
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--start-maximized')
        
        # 添加解决DNS错误的配置
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('--disable-web-security')
        self.options.add_argument('--allow-running-insecure-content')
        
        # 禁用日志输出
        self.options.add_argument('--log-level=3')
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # 添加性能优化配置
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        
        # 设置代理（如果需要）
        # self.options.add_argument('--proxy-server=http://your-proxy-address')
        
        # 添加登录cookies所需的参数
        # self.cookies = [
        #     {"name": "SESSDATA", "value": "9e152dd0%2C1747375191%2C57a23%2Ab2CjBgE1MIwvuBpb4T4f7nO7S3JjhmJZyrniak5t677iThZyfGR7LbyBIakEsiib7um7ISVkVvSVNYSDh1N3d1d3ducXMyV1QzN1MwSUtJeEtabnJrX1hNdXFVUm1XRVY5TzRqZ2xKSnJCdEZ0YXJSbVFESFExeEFlb3VzSWJVR3FuLVBpOFcxbzFBIIEC", "domain": ".bilibili.com"},
        #     {"name": "bili_jct", "value": "6cefe2346da7b9ca6d3928c78d5ccd5f", "domain": ".bilibili.com"},
        #     {"name": "DedeUserID", "value": "364311362", "domain": ".bilibili.com"},
        #     {"name": "buvid3", "value": "5496E07F-7123-00EB-A9B8-28037097DFA572651infoc", "domain": ".bilibili.com"},
        #     {"name": "buvid4", "value": "67976837-3742-AC70-F0B0-9FA4717EF65957671-023061610-KW7HkkBuEznCq1Vq030bPQ==", "domain": ".bilibili.com"}
        # ]
        
        self.driver = None

    def setup_driver(self):
        """初始化浏览器"""
        try:
            self.driver = webdriver.Chrome(options=self.options)
            self.logger.info("Chrome浏览器启动成功")
            return True
        except Exception as e:
            self.logger.error(f"浏览器启动失败: {str(e)}")
            return False

    def wait_for_comments(self, timeout=20):
        """等待评论区加载完成"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "bili-comments"))
            )
            time.sleep(2)  # 额外等待以确保评论完全加载
            return True
        except TimeoutException:
            self.logger.error("评论区加载超时")
            return False

    def get_comments(self, url, max_comments=100):
        """获取视频评论"""
        try:
            # 访问页面
            self.driver.get(url)
            time.sleep(3)  # 等待页面初始加载
            
            # # 添加cookies
            # for cookie in self.cookies:
            #     try:
            #         self.driver.add_cookie(cookie)
            #     except Exception as e:
            #         self.logger.warning(f"添加cookie失败: {str(e)}")
            
            # 刷新页面
            self.driver.refresh()
            
            # 等待评论区加载
            if not self.wait_for_comments():
                return []
            
            comments = []
            processed_comments = set()  # 用于去重
            retry_count = 3  # 设置重试次数
            
            # 滚动到评论区
            comments_section = self.driver.find_element(By.TAG_NAME, "bili-comments")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", comments_section)
            time.sleep(2)
            
            for i in range(1, max_comments + 1):
                for attempt in range(retry_count):
                    try:
                        comment_xpath = f"//bili-comment-thread-renderer[{i}]//bili-comment-renderer//div/div/div[2]/bili-rich-text//p/span"
                        
                        # 等待评论元素出现
                        comment_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, comment_xpath))
                        )
                        
                        # 滚动到评论位置
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", comment_element)
                        time.sleep(0.5)
                        
                        comment_text = comment_text = comment_element.text.strip()
                        if not comment_text or comment_text in processed_comments:
                            continue
                            
                        # 获取用户信息
                        user_xpath = f"//bili-comment-thread-renderer[{i}]//bili-comment-renderer//div[contains(@class, 'user-name')]"
                        time_xpath = f"//bili-comment-thread-renderer[{i}]//bili-comment-renderer//span[contains(@class, 'time')]"
                        
                        username = self.driver.find_element(By.XPATH, user_xpath).text.strip()
                        comment_time = self.driver.find_element(By.XPATH, time_xpath).text.strip()
                        
                        comment_info = {
                            "index": len(comments) + 1,
                            "username": username,
                            "content": comment_text,
                            "time": comment_time
                        }
                        
                        comments.append(comment_info)
                        processed_comments.add(comment_text)
                        self.logger.info(f"成功获取第 {len(comments)} 条评论")
                        break
                        
                    except Exception as e:
                        if attempt == retry_count - 1:
                            self.logger.warning(f"获取第 {i} 条评论失败: {str(e)}")
                            continue
                        time.sleep(1)
                
                # 每获取10条评论后保存一次
                if len(comments) % 10 == 0:
                    self.save_comments(comments, filename="bilibili_comments_temp.json")
            
            return comments
            
        except Exception as e:
            self.logger.error(f"获取评论失败: {str(e)}")
            return []

    def save_comments(self, comments, filename=None):
        """保存评论到文件"""
        if not filename:
            filename = f"bilibili_comments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(comments, f, ensure_ascii=False, indent=2)
            self.logger.info(f"评论已保存到文件: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"保存评论失败: {str(e)}")
            return False

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.logger.info("浏览器已关闭")

def main():
    scraper = BilibiliCommentsScraper()
    
    if scraper.setup_driver():
        try:
            # 目标视频URL
            video_url = "https://www.bilibili.com/video/BV1hryGYzEC1"
            
            # 获取评论
            comments = scraper.get_comments(video_url, max_comments=100)
            
            # 保存评论
            if comments:
                scraper.save_comments(comments)
                
                # 打印评论摘要
                print(f"\n成功获取 {len(comments)} 条评论")
                print("\n前5条评论预览:")
                for comment in comments[:5]:
                    print(f"\n评论 #{comment['index']}")
                    print(f"用户: {comment['username']}")
                    print(f"时间: {comment['time']}")
                    print(f"内容: {comment['content']}")
            else:
                print("未获取到评论")
                
        finally:
            scraper.close()

if __name__ == "__main__":
    main()