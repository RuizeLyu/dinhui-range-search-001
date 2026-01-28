import logging
import os
from datetime import datetime
from .config import config_manager

# 配置日志
logging.basicConfig(
    level=getattr(logging, config_manager.get("system.log_level", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Controller:
    def __init__(self):
        self.config = config_manager
        self.domain = self.config.get_research_domain()
        self.start_year, self.end_year = self.config.get_time_range()
        logger.info(f"初始化控制器: 研究领域={self.domain}, 时间范围={self.start_year}-{self.end_year}")
    
    def run_pipeline(self):
        """运行完整的工作流程"""
        try:
            logger.info("开始执行工作流程...")
            
            # 1. 爬取文献
            logger.info("步骤1: 爬取文献")
            papers = self._crawl_papers()
            logger.info(f"爬取完成，获取到 {len(papers)} 篇论文")
            
            # 2. 下载PDF
            logger.info("步骤2: 下载PDF")
            papers_with_pdf = self._download_pdfs(papers)
            logger.info(f"PDF下载完成，成功下载 {len(papers_with_pdf)} 篇")
            
            # 3. 解析PDF
            logger.info("步骤3: 解析PDF")
            papers_with_content = self._parse_pdfs(papers_with_pdf)
            logger.info(f"PDF解析完成，成功解析 {len(papers_with_content)} 篇")
            
            # 4. LLM分析
            logger.info("步骤4: LLM分析")
            papers_with_analysis = self._analyze_with_llm(papers_with_content)
            logger.info(f"LLM分析完成，成功分析 {len(papers_with_analysis)} 篇")
            
            # 5. 存储到数据库
            logger.info("步骤5: 存储到数据库")
            stored_count = self._store_to_database(papers_with_analysis)
            logger.info(f"数据库存储完成，成功存储 {stored_count} 篇")
            
            # 6. 生成报告
            logger.info("步骤6: 生成报告")
            report_path = self._generate_report()
            logger.info(f"报告生成完成，保存路径: {report_path}")
            
            logger.info("工作流程执行完成！")
            return True
        except Exception as e:
            logger.error(f"工作流程执行失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _crawl_papers(self):
        """爬取文献"""
        # 延迟导入，避免循环依赖
        from src.crawler.arxiv import ArxivCrawler
        from src.crawler.scholar import ScholarCrawler
        
        papers = []
        
        # 从arXiv爬取
        if self.config.get("sources.arxiv.enabled"):
            logger.info("从arXiv爬取文献...")
            arxiv_crawler = ArxivCrawler()
            arxiv_papers = arxiv_crawler.crawl()
            papers.extend(arxiv_papers)
            logger.info(f"从arXiv获取到 {len(arxiv_papers)} 篇论文")
        
        # 从Google Scholar爬取
        if self.config.get("sources.google_scholar.enabled"):
            logger.info("从Google Scholar爬取文献...")
            scholar_crawler = ScholarCrawler()
            scholar_papers = scholar_crawler.crawl()
            papers.extend(scholar_papers)
            logger.info(f"从Google Scholar获取到 {len(scholar_papers)} 篇论文")
        
        # 去重
        unique_papers = self._deduplicate_papers(papers)
        logger.info(f"去重后剩余 {len(unique_papers)} 篇论文")
        
        return unique_papers
    
    def _download_pdfs(self, papers):
        """下载PDF"""
        # 延迟导入
        from src.pdf.downloader import PDFDownloader
        
        downloader = PDFDownloader()
        papers_with_pdf = []
        
        for paper in papers:
            try:
                pdf_path = downloader.download(paper)
                if pdf_path:
                    paper["pdf_path"] = pdf_path
                    papers_with_pdf.append(paper)
            except Exception as e:
                logger.error(f"下载PDF失败: {paper.get('title')} - {str(e)}")
        
        return papers_with_pdf
    
    def _parse_pdfs(self, papers):
        """解析PDF"""
        # 延迟导入
        from src.pdf.parser import PDFParser
        
        parser = PDFParser()
        papers_with_content = []
        
        for paper in papers:
            try:
                content = parser.parse(paper["pdf_path"])
                if content:
                    paper["content"] = content
                    papers_with_content.append(paper)
            except Exception as e:
                logger.error(f"解析PDF失败: {paper.get('title')} - {str(e)}")
        
        return papers_with_content
    
    def _analyze_with_llm(self, papers):
        """使用LLM分析论文"""
        # 延迟导入
        from src.llm.analyzer import LLMAnalyzer
        
        analyzer = LLMAnalyzer()
        papers_with_analysis = []
        
        for paper in papers:
            try:
                analysis = analyzer.analyze(paper["content"])
                if analysis:
                    paper.update(analysis)
                    paper["llm_extract_time"] = datetime.now().isoformat()
                    papers_with_analysis.append(paper)
            except Exception as e:
                logger.error(f"LLM分析失败: {paper.get('title')} - {str(e)}")
        
        return papers_with_analysis
    
    def _store_to_database(self, papers):
        """存储到数据库"""
        # 延迟导入
        from src.database.db_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        stored_count = 0
        
        for paper in papers:
            try:
                db_manager.insert_paper(paper)
                stored_count += 1
            except Exception as e:
                logger.error(f"存储到数据库失败: {paper.get('title')} - {str(e)}")
        
        return stored_count
    
    def _generate_report(self):
        """生成报告"""
        # 延迟导入
        from src.report.generator import ReportGenerator
        
        generator = ReportGenerator()
        report_path = generator.generate()
        return report_path
    
    def _deduplicate_papers(self, papers):
        """去重论文"""
        seen_titles = set()
        unique_papers = []
        
        for paper in papers:
            title = paper.get("title", "").strip().lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)
        
        return unique_papers

# 创建全局控制器实例
controller = Controller()
