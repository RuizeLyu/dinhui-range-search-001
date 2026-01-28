#!/usr/bin/env python3
import sys
import logging
from src.core.config import config_manager
from src.crawler.arxiv import ArxivCrawler
from src.pdf.downloader import PDFDownloader
from src.pdf.parser import PDFParser
from src.llm.analyzer import LLMAnalyzer
from src.database.db_manager import DatabaseManager
from src.report.generator import ReportGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_config():
    """测试配置模块"""
    print("=== 测试配置模块 ===")
    print(f"研究领域: {config_manager.get_research_domain()}")
    print(f"关键词: {config_manager.get_keywords()}")
    start_year, end_year = config_manager.get_time_range()
    print(f"时间范围: {start_year}-{end_year}")
    print(f"arXiv分类号: {config_manager.get_arxiv_categories()}")
    print("配置模块测试完成！")

def test_crawler():
    """测试爬虫模块"""
    print("\n=== 测试爬虫模块 ===")
    crawler = ArxivCrawler()
    papers = crawler.crawl()
    print(f"获取到 {len(papers)} 篇论文")
    if papers:
        print(f"第一篇论文: {papers[0]['title']}")
    print("爬虫模块测试完成！")

def test_pdf_downloader():
    """测试PDF下载模块"""
    print("\n=== 测试PDF下载模块 ===")
    # 先获取一篇论文
    crawler = ArxivCrawler()
    papers = crawler.crawl()
    if papers:
        downloader = PDFDownloader()
        paper = papers[0]
        print(f"尝试下载: {paper['title']}")
        pdf_path = downloader.download(paper)
        if pdf_path:
            print(f"PDF下载成功: {pdf_path}")
        else:
            print("PDF下载失败")
    print("PDF下载模块测试完成！")

def test_pdf_parser():
    """测试PDF解析模块"""
    print("\n=== 测试PDF解析模块 ===")
    # 先获取并下载一篇论文
    crawler = ArxivCrawler()
    papers = crawler.crawl()
    if papers:
        downloader = PDFDownloader()
        paper = papers[0]
        pdf_path = downloader.download(paper)
        if pdf_path:
            parser = PDFParser()
            content = parser.parse(pdf_path)
            if content:
                print(f"PDF解析成功，内容长度: {len(content)}")
                print(f"前500字符: {content[:500]}...")
            else:
                print("PDF解析失败")
    print("PDF解析模块测试完成！")

def test_llm_analyzer():
    """测试LLM分析模块"""
    print("\n=== 测试LLM分析模块 ===")
    # 先获取、下载并解析一篇论文
    crawler = ArxivCrawler()
    papers = crawler.crawl()
    if papers:
        downloader = PDFDownloader()
        paper = papers[0]
        pdf_path = downloader.download(paper)
        if pdf_path:
            parser = PDFParser()
            content = parser.parse(pdf_path)
            if content:
                analyzer = LLMAnalyzer()
                analysis = analyzer.analyze(content)
                if analysis:
                    print("LLM分析成功！")
                    print(f"研究问题: {analysis.get('research_problem', '')[:100]}...")
                    print(f"提出方法: {analysis.get('method_summary', '')[:100]}...")
                else:
                    print("LLM分析失败")
    print("LLM分析模块测试完成！")

def test_database():
    """测试数据库模块"""
    print("\n=== 测试数据库模块 ===")
    db_manager = DatabaseManager()
    # 先获取一篇论文
    crawler = ArxivCrawler()
    papers = crawler.crawl()
    if papers:
        paper_id = db_manager.insert_paper(papers[0])
        if paper_id:
            print(f"论文插入成功，ID: {paper_id}")
            # 获取论文
            retrieved_paper = db_manager.get_paper(paper_id)
            if retrieved_paper:
                print(f"论文获取成功: {retrieved_paper['title']}")
    # 统计论文数量
    count = db_manager.get_papers_count()
    print(f"数据库中的论文数量: {count}")
    print("数据库模块测试完成！")

def test_report_generator():
    """测试报告生成模块"""
    print("\n=== 测试报告生成模块 ===")
    generator = ReportGenerator()
    report_path = generator.generate()
    if report_path:
        print(f"报告生成成功: {report_path}")
    else:
        print("报告生成失败")
    print("报告生成模块测试完成！")

def main():
    """主函数"""
    print("开始测试各个模块...")
    
    # 测试配置模块
    test_config()
    
    # 测试爬虫模块
    test_crawler()
    
    # 测试PDF下载模块
    test_pdf_downloader()
    
    # 测试PDF解析模块
    test_pdf_parser()
    
    # 测试LLM分析模块
    test_llm_analyzer()
    
    # 测试数据库模块
    test_database()
    
    # 测试报告生成模块
    test_report_generator()
    
    print("\n所有模块测试完成！")

if __name__ == "__main__":
    main()
