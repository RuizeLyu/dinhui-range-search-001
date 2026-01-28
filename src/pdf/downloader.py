import os
import requests
import logging
from src.core.config import config_manager
from src.crawler.utils import RequestHandler

logger = logging.getLogger(__name__)

class PDFDownloader:
    def __init__(self):
        self.config = config_manager
        self.storage_path = self.config.get_pdf_storage_path()
        self.timeout = self.config.get("pdf.timeout", 30)
        self.max_retries = self.config.get("pdf.max_retries", 3)
        self.request_handler = RequestHandler()
    
    def download(self, paper):
        """下载PDF文件"""
        try:
            # 生成存储路径
            pdf_path = self._generate_pdf_path(paper)
            
            # 检查文件是否已存在
            if os.path.exists(pdf_path):
                logger.info(f"PDF文件已存在: {pdf_path}")
                return pdf_path
            
            # 尝试从不同来源下载
            # 1. 从arXiv下载
            if paper.get("source") == "arXiv" and paper.get("pdf_url"):
                if self._download_from_url(paper["pdf_url"], pdf_path):
                    return pdf_path
            
            # 2. 从其他PDF URL下载
            if paper.get("pdf_url") and paper.get("source") != "arXiv":
                if self._download_from_url(paper["pdf_url"], pdf_path):
                    return pdf_path
            
            # 3. 尝试从DOI获取（如果有）
            if paper.get("doi"):
                doi_url = f"https://doi.org/{paper['doi']}"
                if self._download_from_url(doi_url, pdf_path):
                    return pdf_path
            
            # 4. 尝试从Unpaywall获取（开放获取）
            if paper.get("doi"):
                if self._download_from_unpaywall(paper["doi"], pdf_path):
                    return pdf_path
            
            logger.warning(f"无法下载PDF: {paper.get('title')}")
            return None
        except Exception as e:
            logger.error(f"下载PDF失败: {str(e)}")
            return None
    
    def _download_from_url(self, url, pdf_path):
        """从URL下载PDF"""
        try:
            logger.info(f"从URL下载PDF: {url}")
            
            # 发送请求
            response = self.request_handler.get(url, timeout=self.timeout)
            
            # 检查响应内容类型
            content_type = response.headers.get("Content-Type", "")
            if "pdf" not in content_type.lower():
                logger.warning(f"响应不是PDF: {content_type}")
                return False
            
            # 保存文件
            with open(pdf_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"PDF下载成功: {pdf_path}")
            return True
        except Exception as e:
            logger.error(f"从URL下载失败: {str(e)}")
            return False
    
    def _download_from_unpaywall(self, doi, pdf_path):
        """从Unpaywall获取开放获取的PDF"""
        try:
            logger.info(f"从Unpaywall获取PDF: {doi}")
            
            # 构建Unpaywall API URL
            unpaywall_url = f"https://api.unpaywall.org/v2/{doi}?email=your-email@example.com"
            
            # 发送请求
            response = self.request_handler.get(unpaywall_url, timeout=self.timeout)
            data = response.json()
            
            # 检查是否有开放获取的PDF
            if data.get("is_oa") and data.get("best_oa_location"):
                pdf_url = data["best_oa_location"].get("url_for_pdf")
                if pdf_url:
                    return self._download_from_url(pdf_url, pdf_path)
            
            logger.info(f"Unpaywall没有找到开放获取的PDF: {doi}")
            return False
        except Exception as e:
            logger.error(f"从Unpaywall获取失败: {str(e)}")
            return False
    
    def _generate_pdf_path(self, paper):
        """生成PDF存储路径"""
        # 生成文件名
        if paper.get("arxiv_id"):
            # arXiv论文使用arXiv ID作为文件名
            filename = f"{paper['arxiv_id']}.pdf"
        else:
            # 其他论文使用标题的简化版本
            title = paper.get("title", "")
            # 移除特殊字符
            filename = "".join(c for c in title if c.isalnum() or c in " -_")
            # 限制文件名长度
            filename = filename[:100] + ".pdf"
        
        # 构建完整路径
        pdf_path = os.path.join(self.storage_path, filename)
        
        return pdf_path
