import os
import shutil
import logging
from src.core.config import config_manager

logger = logging.getLogger(__name__)

class PDFManager:
    def __init__(self):
        self.config = config_manager
        self.storage_path = self.config.get_pdf_storage_path()
    
    def get_pdf_path(self, paper_id):
        """根据论文ID获取PDF路径"""
        # 构建可能的文件名
        possible_filenames = [
            f"{paper_id}.pdf",
            f"{paper_id.replace('/', '_')}.pdf"
        ]
        
        # 查找文件
        for filename in possible_filenames:
            pdf_path = os.path.join(self.storage_path, filename)
            if os.path.exists(pdf_path):
                return pdf_path
        
        # 如果没有找到，尝试搜索包含ID的文件
        for filename in os.listdir(self.storage_path):
            if paper_id in filename and filename.endswith(".pdf"):
                return os.path.join(self.storage_path, filename)
        
        return None
    
    def list_pdfs(self):
        """列出所有PDF文件"""
        pdf_files = []
        
        if os.path.exists(self.storage_path):
            for filename in os.listdir(self.storage_path):
                if filename.endswith(".pdf"):
                    pdf_path = os.path.join(self.storage_path, filename)
                    pdf_files.append({
                        "filename": filename,
                        "path": pdf_path,
                        "size": os.path.getsize(pdf_path),
                        "mtime": os.path.getmtime(pdf_path)
                    })
        
        return pdf_files
    
    def count_pdfs(self):
        """统计PDF文件数量"""
        return len(self.list_pdfs())
    
    def clean_up(self, dry_run=False):
        """清理无效的PDF文件"""
        cleaned_count = 0
        
        for pdf_info in self.list_pdfs():
            pdf_path = pdf_info["path"]
            
            # 检查文件大小
            if pdf_info["size"] < 1024:  # 小于1KB的文件可能是无效的
                logger.warning(f"清理小文件: {pdf_path}")
                if not dry_run:
                    os.remove(pdf_path)
                    cleaned_count += 1
            
            # 检查文件是否是有效的PDF
            if not self._is_valid_pdf(pdf_path):
                logger.warning(f"清理无效PDF: {pdf_path}")
                if not dry_run:
                    os.remove(pdf_path)
                    cleaned_count += 1
        
        logger.info(f"清理完成，处理了 {cleaned_count} 个文件")
        return cleaned_count
    
    def _is_valid_pdf(self, pdf_path):
        """检查文件是否是有效的PDF"""
        try:
            with open(pdf_path, 'rb') as f:
                # 检查PDF文件头
                header = f.read(4)
                return header == b'%PDF'
        except Exception:
            return False
    
    def organize_by_year(self):
        """按年份组织PDF文件"""
        # 注意：此功能需要论文的年份信息，可能需要从数据库获取
        # 这里仅提供框架实现
        logger.info("按年份组织PDF文件")
        
        # 从数据库获取论文信息
        from src.database.db_manager import DatabaseManager
        db_manager = DatabaseManager()
        papers = db_manager.get_all_papers()
        
        for paper in papers:
            pdf_path = paper.get("pdf_path")
            if not pdf_path or not os.path.exists(pdf_path):
                continue
            
            year = paper.get("publish_year")
            if not year:
                continue
            
            # 创建年份目录
            year_dir = os.path.join(self.storage_path, str(year))
            os.makedirs(year_dir, exist_ok=True)
            
            # 移动文件
            filename = os.path.basename(pdf_path)
            new_path = os.path.join(year_dir, filename)
            
            if not os.path.exists(new_path):
                try:
                    shutil.move(pdf_path, new_path)
                    logger.info(f"移动文件: {pdf_path} → {new_path}")
                    # 更新数据库中的路径
                    db_manager.update_pdf_path(paper.get("id"), new_path)
                except Exception as e:
                    logger.error(f"移动文件失败: {str(e)}")
    
    def get_storage_usage(self):
        """获取存储使用情况"""
        total_size = 0
        
        for pdf_info in self.list_pdfs():
            total_size += pdf_info["size"]
        
        return {
            "total_files": self.count_pdfs(),
            "total_size": total_size,
            "total_size_human": self._format_size(total_size),
            "storage_path": self.storage_path
        }
    
    def _format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
