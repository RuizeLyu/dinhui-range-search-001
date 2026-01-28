import sqlite3
import logging
from .models import PaperModel

logger = logging.getLogger(__name__)

class PaperQueries:
    """论文查询工具"""
    
    def __init__(self, conn):
        self.conn = conn
    
    def search_papers(self, keyword, limit=100):
        """搜索论文"""
        try:
            cursor = self.conn.cursor()
            query = '''
                SELECT * FROM papers 
                WHERE title LIKE ? OR summary LIKE ? OR research_problem LIKE ? 
                LIMIT ?
            '''
            search_term = f"%{keyword}%"
            cursor.execute(query, (search_term, search_term, search_term, limit))
            rows = cursor.fetchall()
            papers = [PaperModel._row_to_dict(row) for row in rows]
            return papers
        except Exception as e:
            logger.error(f"搜索论文失败: {str(e)}")
            return []
    
    def get_papers_with_llm_analysis(self):
        """获取已完成LLM分析的论文"""
        try:
            cursor = self.conn.cursor()
            query = '''
                SELECT * FROM papers 
                WHERE research_problem IS NOT NULL 
                AND method_summary IS NOT NULL
            '''
            cursor.execute(query)
            rows = cursor.fetchall()
            papers = [PaperModel._row_to_dict(row) for row in rows]
            return papers
        except Exception as e:
            logger.error(f"获取已分析论文失败: {str(e)}")
            return []
    
    def get_papers_without_pdf(self):
        """获取没有PDF的论文"""
        try:
            cursor = self.conn.cursor()
            query = '''
                SELECT * FROM papers 
                WHERE pdf_path IS NULL OR pdf_path = ''
            '''
            cursor.execute(query)
            rows = cursor.fetchall()
            papers = [PaperModel._row_to_dict(row) for row in rows]
            return papers
        except Exception as e:
            logger.error(f"获取无PDF论文失败: {str(e)}")
            return []
    
    def get_most_cited_papers(self, limit=10):
        """获取引用最多的论文"""
        try:
            cursor = self.conn.cursor()
            query = '''
                SELECT * FROM papers 
                WHERE citations IS NOT NULL 
                ORDER BY citations DESC 
                LIMIT ?
            '''
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            papers = [PaperModel._row_to_dict(row) for row in rows]
            return papers
        except Exception as e:
            logger.error(f"获取高引用论文失败: {str(e)}")
            return []
    
    def get_recent_papers(self, limit=20):
        """获取最新的论文"""
        try:
            cursor = self.conn.cursor()
            query = '''
                SELECT * FROM papers 
                WHERE publish_year IS NOT NULL 
                ORDER BY publish_year DESC, id DESC 
                LIMIT ?
            '''
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            papers = [PaperModel._row_to_dict(row) for row in rows]
            return papers
        except Exception as e:
            logger.error(f"获取最新论文失败: {str(e)}")
            return []
    
    def get_papers_by_category(self, category):
        """根据分类获取论文"""
        try:
            cursor = self.conn.cursor()
            query = '''
                SELECT * FROM papers 
                WHERE categories LIKE ? OR primary_category = ?
            '''
            cursor.execute(query, (f"%{category}%", category))
            rows = cursor.fetchall()
            papers = [PaperModel._row_to_dict(row) for row in rows]
            return papers
        except Exception as e:
            logger.error(f"根据分类获取论文失败: {str(e)}")
            return []
    
    def get_papers_statistics(self):
        """获取论文统计信息"""
        try:
            stats = {
                "total_papers": self._get_count("SELECT COUNT(*) FROM papers"),
                "with_pdf": self._get_count("SELECT COUNT(*) FROM papers WHERE pdf_path IS NOT NULL"),
                "with_llm_analysis": self._get_count("SELECT COUNT(*) FROM papers WHERE research_problem IS NOT NULL"),
                "open_source": self._get_count("SELECT COUNT(*) FROM papers WHERE is_open_source = 1"),
                "average_citations": self._get_average("SELECT AVG(citations) FROM papers WHERE citations IS NOT NULL"),
                "yearly_distribution": self._get_yearly_distribution(),
                "source_distribution": self._get_source_distribution()
            }
            return stats
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {}
    
    def _get_count(self, query):
        """执行计数查询"""
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result else 0
    
    def _get_average(self, query):
        """执行平均值查询"""
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        return round(result[0], 2) if result and result[0] else 0
    
    def _get_yearly_distribution(self):
        """获取年度分布"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT publish_year, COUNT(*) FROM papers GROUP BY publish_year ORDER BY publish_year')
        rows = cursor.fetchall()
        return {row[0]: row[1] for row in rows}
    
    def _get_source_distribution(self):
        """获取来源分布"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT source, COUNT(*) FROM papers GROUP BY source')
        rows = cursor.fetchall()
        return {row[0]: row[1] for row in rows}
