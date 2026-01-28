import sqlite3
import json
import logging

logger = logging.getLogger(__name__)

class PaperModel:
    """论文数据模型"""
    
    @staticmethod
    def create_table(conn):
        """创建论文表"""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS papers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    authors TEXT,  -- JSON格式存储作者列表
                    summary TEXT,
                    publish_year INTEGER,
                    source TEXT,
                    arxiv_id TEXT,
                    pdf_url TEXT,
                    html_url TEXT,
                    categories TEXT,  -- JSON格式存储分类列表
                    doi TEXT,
                    primary_category TEXT,
                    venue TEXT,
                    citations INTEGER,
                    pdf_path TEXT,
                    content TEXT,
                    research_problem TEXT,
                    method_summary TEXT,
                    innovation TEXT,
                    experimental_results TEXT,
                    limitations TEXT,
                    is_open_source INTEGER,  -- 0或1
                    llm_extract_time TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_title ON papers(title)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(publish_year)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_source ON papers(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_arxiv_id ON papers(arxiv_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_doi ON papers(doi)')
            
            conn.commit()
            logger.info("论文表创建成功")
        except Exception as e:
            logger.error(f"创建论文表失败: {str(e)}")
            conn.rollback()
    
    @staticmethod
    def insert_paper(conn, paper):
        """插入论文数据"""
        try:
            cursor = conn.cursor()
            
            # 准备数据
            data = {
                'title': paper.get('title', ''),
                'authors': json.dumps(paper.get('authors', [])) if paper.get('authors') else None,
                'summary': paper.get('summary', ''),
                'publish_year': paper.get('publish_year'),
                'source': paper.get('source', ''),
                'arxiv_id': paper.get('arxiv_id'),
                'pdf_url': paper.get('pdf_url'),
                'html_url': paper.get('html_url'),
                'categories': json.dumps(paper.get('categories', [])) if paper.get('categories') else None,
                'doi': paper.get('doi'),
                'primary_category': paper.get('primary_category'),
                'venue': paper.get('venue'),
                'citations': paper.get('citations'),
                'pdf_path': paper.get('pdf_path'),
                'content': paper.get('content'),
                'research_problem': paper.get('research_problem'),
                'method_summary': paper.get('method_summary'),
                'innovation': paper.get('innovation'),
                'experimental_results': paper.get('experimental_results'),
                'limitations': paper.get('limitations'),
                'is_open_source': 1 if paper.get('is_open_source') else 0,
                'llm_extract_time': paper.get('llm_extract_time')
            }
            
            # 执行插入
            cursor.execute('''
                INSERT INTO papers (
                    title, authors, summary, publish_year, source, arxiv_id, pdf_url, html_url,
                    categories, doi, primary_category, venue, citations, pdf_path, content,
                    research_problem, method_summary, innovation, experimental_results, limitations,
                    is_open_source, llm_extract_time
                ) VALUES (
                    :title, :authors, :summary, :publish_year, :source, :arxiv_id, :pdf_url, :html_url,
                    :categories, :doi, :primary_category, :venue, :citations, :pdf_path, :content,
                    :research_problem, :method_summary, :innovation, :experimental_results, :limitations,
                    :is_open_source, :llm_extract_time
                )
            ''', data)
            
            paper_id = cursor.lastrowid
            conn.commit()
            logger.debug(f"论文插入成功，ID: {paper_id}")
            return paper_id
        except Exception as e:
            logger.error(f"插入论文失败: {str(e)}")
            conn.rollback()
            return None
    
    @staticmethod
    def get_paper(conn, paper_id):
        """根据ID获取论文"""
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM papers WHERE id = ?', (paper_id,))
            row = cursor.fetchone()
            if row:
                return PaperModel._row_to_dict(row)
            return None
        except Exception as e:
            logger.error(f"获取论文失败: {str(e)}")
            return None
    
    @staticmethod
    def get_all_papers(conn):
        """获取所有论文"""
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM papers')
            rows = cursor.fetchall()
            papers = [PaperModel._row_to_dict(row) for row in rows]
            return papers
        except Exception as e:
            logger.error(f"获取所有论文失败: {str(e)}")
            return []
    
    @staticmethod
    def update_pdf_path(conn, paper_id, pdf_path):
        """更新PDF路径"""
        try:
            cursor = conn.cursor()
            cursor.execute('UPDATE papers SET pdf_path = ? WHERE id = ?', (pdf_path, paper_id))
            conn.commit()
            logger.debug(f"更新PDF路径成功，ID: {paper_id}")
            return True
        except Exception as e:
            logger.error(f"更新PDF路径失败: {str(e)}")
            conn.rollback()
            return False
    
    @staticmethod
    def _row_to_dict(row):
        """将数据库行转换为字典"""
        columns = [
            'id', 'title', 'authors', 'summary', 'publish_year', 'source', 'arxiv_id', 'pdf_url',
            'html_url', 'categories', 'doi', 'primary_category', 'venue', 'citations', 'pdf_path',
            'content', 'research_problem', 'method_summary', 'innovation', 'experimental_results',
            'limitations', 'is_open_source', 'llm_extract_time', 'created_at', 'updated_at'
        ]
        
        paper = dict(zip(columns, row))
        
        # 解析JSON字段
        if paper.get('authors'):
            try:
                paper['authors'] = json.loads(paper['authors'])
            except Exception:
                paper['authors'] = []
        
        if paper.get('categories'):
            try:
                paper['categories'] = json.loads(paper['categories'])
            except Exception:
                paper['categories'] = []
        
        # 转换布尔值
        paper['is_open_source'] = bool(paper.get('is_open_source'))
        
        return paper
