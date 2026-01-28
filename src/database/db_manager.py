import sqlite3
import os
import logging
from src.core.config import config_manager
from .models import PaperModel

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.config = config_manager
        self.db_path = self.config.get_database_path()
        self.conn = None
        self._connect()
        self._initialize_database()
    
    def _connect(self):
        """连接到数据库"""
        try:
            # 确保数据库目录存在
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            
            # 连接到SQLite数据库
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            # 设置行_factory为sqlite3.Row，方便后续操作
            self.conn.row_factory = sqlite3.Row
            logger.info(f"数据库连接成功: {self.db_path}")
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            self.conn = None
    
    def _initialize_database(self):
        """初始化数据库"""
        if self.conn:
            PaperModel.create_table(self.conn)
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            try:
                self.conn.close()
                logger.info("数据库连接已关闭")
            except Exception as e:
                logger.error(f"关闭数据库连接失败: {str(e)}")
    
    def insert_paper(self, paper):
        """插入论文"""
        if not self.conn:
            logger.error("数据库连接未建立")
            return None
        
        return PaperModel.insert_paper(self.conn, paper)
    
    def get_paper(self, paper_id):
        """根据ID获取论文"""
        if not self.conn:
            logger.error("数据库连接未建立")
            return None
        
        return PaperModel.get_paper(self.conn, paper_id)
    
    def get_all_papers(self):
        """获取所有论文"""
        if not self.conn:
            logger.error("数据库连接未建立")
            return []
        
        return PaperModel.get_all_papers(self.conn)
    
    def get_papers_by_year(self, year):
        """根据年份获取论文"""
        if not self.conn:
            logger.error("数据库连接未建立")
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM papers WHERE publish_year = ?', (year,))
            rows = cursor.fetchall()
            papers = [PaperModel._row_to_dict(row) for row in rows]
            return papers
        except Exception as e:
            logger.error(f"根据年份获取论文失败: {str(e)}")
            return []
    
    def get_papers_by_source(self, source):
        """根据来源获取论文"""
        if not self.conn:
            logger.error("数据库连接未建立")
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM papers WHERE source = ?', (source,))
            rows = cursor.fetchall()
            papers = [PaperModel._row_to_dict(row) for row in rows]
            return papers
        except Exception as e:
            logger.error(f"根据来源获取论文失败: {str(e)}")
            return []
    
    def get_papers_count(self):
        """获取论文总数"""
        if not self.conn:
            logger.error("数据库连接未建立")
            return 0
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM papers')
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            logger.error(f"获取论文总数失败: {str(e)}")
            return 0
    
    def get_yearly_stats(self):
        """获取年度论文统计"""
        if not self.conn:
            logger.error("数据库连接未建立")
            return {}
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT publish_year, COUNT(*) FROM papers GROUP BY publish_year ORDER BY publish_year')
            rows = cursor.fetchall()
            stats = {row[0]: row[1] for row in rows}
            return stats
        except Exception as e:
            logger.error(f"获取年度统计失败: {str(e)}")
            return {}
    
    def get_source_stats(self):
        """获取来源统计"""
        if not self.conn:
            logger.error("数据库连接未建立")
            return {}
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT source, COUNT(*) FROM papers GROUP BY source')
            rows = cursor.fetchall()
            stats = {row[0]: row[1] for row in rows}
            return stats
        except Exception as e:
            logger.error(f"获取来源统计失败: {str(e)}")
            return {}
    
    def update_pdf_path(self, paper_id, pdf_path):
        """更新PDF路径"""
        if not self.conn:
            logger.error("数据库连接未建立")
            return False
        
        return PaperModel.update_pdf_path(self.conn, paper_id, pdf_path)
    
    def __del__(self):
        """析构函数，关闭数据库连接"""
        self.close()
