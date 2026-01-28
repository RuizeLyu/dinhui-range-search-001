import os
import requests
import logging
import fitz  # PyMuPDF
from src.core.config import config_manager

logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self):
        self.config = config_manager
        self.grobid_url = self.config.get("pdf_parsing.grobid_url", "http://localhost:8070")
        self.default_parser = self.config.get("pdf_parsing.default_parser", "grobid")
    
    def parse(self, pdf_path):
        """解析PDF文件，提取文本内容"""
        try:
            if not os.path.exists(pdf_path):
                logger.error(f"PDF文件不存在: {pdf_path}")
                return None
            
            # 根据配置选择解析器
            if self.default_parser == "grobid" and self._is_grobid_available():
                logger.info(f"使用Grobid解析PDF: {pdf_path}")
                content = self._parse_with_grobid(pdf_path)
            else:
                logger.info(f"使用PyMuPDF解析PDF: {pdf_path}")
                content = self._parse_with_pymupdf(pdf_path)
            
            if content:
                logger.info(f"成功解析PDF: {pdf_path}")
                return content
            else:
                logger.warning(f"解析PDF失败，内容为空: {pdf_path}")
                return None
        except Exception as e:
            logger.error(f"解析PDF失败: {str(e)}")
            return None
    
    def _is_grobid_available(self):
        """检查Grobid服务是否可用"""
        try:
            response = requests.get(f"{self.grobid_url}/api/isalive", timeout=5)
            return response.status_code == 200
        except Exception:
            logger.warning("Grobid服务不可用，将使用PyMuPDF")
            return False
    
    def _parse_with_grobid(self, pdf_path):
        """使用Grobid解析PDF"""
        try:
            # 构建请求URL
            url = f"{self.grobid_url}/api/processFulltextDocument"
            
            # 准备文件
            with open(pdf_path, 'rb') as f:
                files = {'input': f}
                
                # 发送请求
                response = requests.post(
                    url, 
                    files=files,
                    data={'consolidateCitations': '1'},
                    timeout=60
                )
                
                # 检查响应
                response.raise_for_status()
                
                # 处理XML响应
                xml_content = response.text
                return self._extract_text_from_grobid_xml(xml_content)
        except Exception as e:
            logger.error(f"使用Grobid解析失败: {str(e)}")
            # 失败时回退到PyMuPDF
            return self._parse_with_pymupdf(pdf_path)
    
    def _extract_text_from_grobid_xml(self, xml_content):
        """从Grobid XML中提取文本"""
        try:
            import xml.etree.ElementTree as ET
            
            # 解析XML
            root = ET.fromstring(xml_content)
            
            # 提取标题
            title = ""
            title_elem = root.find('.//{http://www.tei-c.org/ns/1.0}titleStmt/{http://www.tei-c.org/ns/1.0}title')
            if title_elem is not None:
                title = ' '.join(title_elem.itertext())
            
            # 提取摘要
            abstract = ""
            abstract_elem = root.find('.//{http://www.tei-c.org/ns/1.0}profileDesc/{http://www.tei-c.org/ns/1.0}abstract')
            if abstract_elem is not None:
                abstract = ' '.join(abstract_elem.itertext())
            
            # 提取正文
            body_text = ""
            body_elem = root.find('.//{http://www.tei-c.org/ns/1.0}text/{http://www.tei-c.org/ns/1.0}body')
            if body_elem is not None:
                body_text = ' '.join(body_elem.itertext())
            
            # 组合内容
            content = f"Title: {title}\n\nAbstract: {abstract}\n\n{body_text}"
            return content
        except Exception as e:
            logger.error(f"处理Grobid XML失败: {str(e)}")
            return None
    
    def _parse_with_pymupdf(self, pdf_path):
        """使用PyMuPDF解析PDF"""
        try:
            # 打开PDF文件
            doc = fitz.open(pdf_path)
            
            # 提取文本
            text_parts = []
            
            # 提取标题（通常在第一页）
            if doc.page_count > 0:
                first_page = doc[0]
                title_text = first_page.get_text("text")
                # 取前几行作为标题
                title_lines = title_text.strip().split('\n')[:3]
                title = ' '.join(title_lines)
                text_parts.append(f"Title: {title}")
            
            # 提取摘要（通常在标题之后）
            if doc.page_count > 0:
                first_page = doc[0]
                abstract_text = first_page.get_text("text")
                # 简单处理，假设摘要在标题之后
                text_parts.append(f"Abstract: {abstract_text}")
            
            # 提取正文
            body_text = []
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text = page.get_text("text")
                body_text.append(text)
            
            text_parts.append('\n'.join(body_text))
            
            # 关闭文档
            doc.close()
            
            # 组合内容
            content = '\n\n'.join(text_parts)
            return content
        except Exception as e:
            logger.error(f"使用PyMuPDF解析失败: {str(e)}")
            return None
    
    def extract_metadata(self, pdf_path):
        """提取PDF元数据"""
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            doc.close()
            
            # 处理元数据
            extracted_metadata = {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", ""),
                "page_count": doc.page_count if 'doc' in locals() else 0
            }
            
            return extracted_metadata
        except Exception as e:
            logger.error(f"提取元数据失败: {str(e)}")
            return {}
    
    def extract_tables(self, pdf_path):
        """提取PDF中的表格"""
        try:
            import pdfplumber
            
            tables = []
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    for table_idx, table in enumerate(page_tables):
                        tables.append({
                            "page": page_num + 1,
                            "index": table_idx + 1,
                            "data": table
                        })
            
            return tables
        except Exception as e:
            logger.error(f"提取表格失败: {str(e)}")
            return []
