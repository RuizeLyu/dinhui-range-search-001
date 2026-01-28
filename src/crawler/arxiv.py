import arxiv
import logging
from src.core.config import config_manager

logger = logging.getLogger(__name__)

class ArxivCrawler:
    def __init__(self):
        self.config = config_manager
        self.domain = self.config.get_research_domain()
        self.keywords = self.config.get_keywords()
        self.start_year, self.end_year = self.config.get_time_range()
        self.categories = self.config.get_arxiv_categories()
        self.max_results = self.config.get_max_results("arxiv")
        self.results_per_page = self.config.get("sources.arxiv.results_per_page", 50)
    
    def crawl(self):
        """爬取arXiv论文"""
        papers = []
        
        # 构建搜索查询
        query = self._build_query()
        logger.info(f"构建arXiv搜索查询: {query}")
        
        # 执行搜索
        try:
            # 使用arxiv库的搜索功能
            search = arxiv.Search(
                query=query,
                max_results=self.max_results,
                sort_by=arxiv.SortCriterion.Relevance,
                sort_order=arxiv.SortOrder.Descending
            )
            
            # 获取结果
            for result in arxiv.Client().results(search):
                paper = self._parse_result(result)
                papers.append(paper)
                
                if len(papers) >= self.max_results:
                    break
            
            logger.info(f"成功获取 {len(papers)} 篇arXiv论文")
        except Exception as e:
            logger.error(f"arXiv搜索失败: {str(e)}")
        
        return papers
    
    def _build_query(self):
        """构建搜索查询字符串"""
        # 构建关键词查询
        keyword_query = " OR ".join([f"{keyword}" for keyword in self.keywords])
        
        # 构建分类号查询
        if self.categories:
            category_query = " OR ".join([f"cat:{category}" for category in self.categories])
            query = f"({keyword_query}) AND ({category_query})"
        else:
            query = keyword_query
        
        # 添加时间范围
        if self.start_year:
            query += f" AND submittedDate:[{self.start_year}0101 TO {(self.end_year or 2099) + 1}0101]"
        
        return query
    
    def _parse_result(self, result):
        """解析arXiv搜索结果"""
        # 提取作者列表
        authors = [author.name for author in result.authors]
        
        # 提取发表年份
        publish_year = None
        if result.published:
            publish_year = result.published.year
        
        # 构建论文信息字典
        paper = {
            "title": result.title,
            "authors": authors,
            "summary": result.summary,
            "publish_year": publish_year,
            "source": "arXiv",
            "arxiv_id": result.get_short_id(),
            "pdf_url": result.pdf_url,
            "html_url": f"https://arxiv.org/abs/{result.get_short_id()}",
            "categories": result.categories,
            "doi": getattr(result, "doi", None),
            "primary_category": result.primary_category
        }
        
        return paper
