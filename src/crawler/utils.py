import requests
import time
import random
import logging
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class RequestHandler:
    """请求处理器，处理HTTP请求和反爬"""
    
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.retry_count = 3
        self.retry_delay = 2
    
    def get(self, url, headers=None, params=None, timeout=30):
        """发送GET请求"""
        for i in range(self.retry_count):
            try:
                # 构建请求头
                request_headers = {
                    "User-Agent": self.ua.random,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive"
                }
                
                # 更新自定义请求头
                if headers:
                    request_headers.update(headers)
                
                # 发送请求
                response = self.session.get(
                    url, 
                    headers=request_headers, 
                    params=params, 
                    timeout=timeout,
                    allow_redirects=True
                )
                
                # 检查响应状态
                response.raise_for_status()
                
                # 随机延迟，避免反爬
                time.sleep(random.uniform(0.5, 1.5))
                
                return response
            except Exception as e:
                logger.warning(f"请求失败 ({i+1}/{self.retry_count}): {str(e)}")
                if i < self.retry_count - 1:
                    # 指数退避
                    time.sleep(self.retry_delay * (2 ** i))
                    continue
                else:
                    logger.error(f"请求最终失败: {str(e)}")
                    raise
    
    def post(self, url, data=None, json=None, headers=None, timeout=30):
        """发送POST请求"""
        for i in range(self.retry_count):
            try:
                # 构建请求头
                request_headers = {
                    "User-Agent": self.ua.random,
                    "Accept": "application/json, text/plain, */*",
                    "Content-Type": "application/json",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Connection": "keep-alive"
                }
                
                # 更新自定义请求头
                if headers:
                    request_headers.update(headers)
                
                # 发送请求
                response = self.session.post(
                    url, 
                    data=data, 
                    json=json, 
                    headers=request_headers, 
                    timeout=timeout
                )
                
                # 检查响应状态
                response.raise_for_status()
                
                # 随机延迟，避免反爬
                time.sleep(random.uniform(0.5, 1.5))
                
                return response
            except Exception as e:
                logger.warning(f"请求失败 ({i+1}/{self.retry_count}): {str(e)}")
                if i < self.retry_count - 1:
                    # 指数退避
                    time.sleep(self.retry_delay * (2 ** i))
                    continue
                else:
                    logger.error(f"请求最终失败: {str(e)}")
                    raise

def normalize_title(title):
    """标准化论文标题"""
    if not title:
        return ""
    # 去除首尾空白
    title = title.strip()
    # 统一大小写？不，保持原样
    return title

def extract_doi(text):
    """从文本中提取DOI"""
    import re
    # DOI格式正则
    doi_pattern = r"10\.[0-9]{4,}/[-._;()/:a-zA-Z0-9]+"
    match = re.search(doi_pattern, text)
    if match:
        return match.group(0)
    return None
