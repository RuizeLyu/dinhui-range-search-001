import time
import logging
from scholarly import scholarly
from src.core.config import config_manager

logger = logging.getLogger(__name__)

class ScholarCrawler:
    def __init__(self):
        self.config = config_manager
        self.domain = self.config.get_research_domain()
        self.keywords = self.config.get_keywords()
        self.start_year, self.end_year = self.config.get_time_range()
        self.max_results = self.config.get_max_results("google_scholar")
        self.request_interval = self.config.get("sources.google_scholar.request_interval", 3)
    
    def crawl(self):
        """爬取Google Scholar论文"""
        papers = []
        
        # 构建搜索查询
        query = self._build_query()
        logger.info(f"构建Google Scholar搜索查询: {query}")
        
        # 执行搜索
        try:
            # 使用scholarly库的搜索功能
            search_query = scholarly.search_pubs(query)
            
            # 获取结果
            count = 0
            while count < self.max_results:
                try:
                    result = next(search_query)
                    paper = self._parse_result(result)
                    
                    # 检查年份
                    if self._is_in_time_range(paper.get("publish_year")):
                        papers.append(paper)
                        count += 1
                        logger.debug(f"获取到论文: {paper.get('title')}")
                    
                    # 控制请求间隔，避免反爬
                    time.sleep(self.request_interval)
                except StopIteration:
                    logger.info("Google Scholar搜索结果已用完")
                    break
                except Exception as e:
                    logger.error(f"获取Google Scholar结果失败: {str(e)}")
                    # 遇到错误时增加间隔
                    time.sleep(self.request_interval * 2)
                    continue
            
            logger.info(f"成功获取 {len(papers)} 篇Google Scholar论文")
        except Exception as e:
            logger.error(f"Google Scholar搜索失败: {str(e)}")
        
        return papers
    
    def _build_query(self):
        """构建搜索查询字符串"""
        # 构建关键词查询
        if self.keywords:
            # 优先使用配置的关键词
            query = " ".join(self.keywords)
        else:
            # 使用研究领域名称
            query = self.domain
        
        # 添加时间范围
        if self.start_year:
            query += f" year:{self.start_year}-{self.end_year or ''}"
        
        return query
    
    def _parse_result(self, result):
        """解析Google Scholar搜索结果"""
        # 提取作者列表
        authors = []
        if "authors" in result:
            authors = [author.strip() for author in result["authors"].split(",")]
        
        # 提取发表年份
        publish_year = None
        if "pub_year" in result:
            try:
                publish_year = int(result["pub_year"])
            except (ValueError, TypeError):
                pass
        
        # 构建论文信息字典
        paper = {
            "title": result.get("title", ""),
            "authors": authors,
            "summary": result.get("abstract", ""),
            "publish_year": publish_year,
            "source": "Google Scholar",
            "venue": result.get("venue", ""),
            "pdf_url": result.get("eprint_url", None),
            "html_url": result.get("pub_url", None),
            "citations": result.get("num_citations", 0),
            "related_url": result.get("related_articles", None),
            "author_id": result.get("author_id", None),
            "pub_id": result.get("scholar_id", None)
        }
        
        return paper
    
    def _is_in_time_range(self, publish_year):
        """检查论文是否在时间范围内"""
        if not publish_year:
            return True  # 没有年份信息的论文也包含
        
        if self.start_year and publish_year < self.start_year:
            return False
        
        if self.end_year and publish_year > self.end_year:
            return False
        
        return True
