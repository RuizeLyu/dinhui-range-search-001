import yaml
import os
from datetime import datetime

class ConfigManager:
    def __init__(self, config_path="config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    
    def get(self, key, default=None):
        """获取配置项，支持嵌套路径"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key, value):
        """设置配置项"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save(self):
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
    
    def get_research_domain(self):
        """获取研究领域"""
        return self.get("research.domain")
    
    def get_keywords(self):
        """获取关键词列表"""
        return self.get("research.keywords", [])
    
    def get_time_range(self):
        """获取时间范围"""
        start_year = self.get("research.start_year")
        end_year = self.get("research.end_year") or datetime.now().year
        return start_year, end_year
    
    def get_arxiv_categories(self):
        """获取arXiv分类号"""
        return self.get("sources.arxiv.categories", [])
    
    def get_max_results(self, source):
        """获取最大结果数"""
        if source == "arxiv":
            return self.get("sources.arxiv.max_results", 100)
        elif source == "google_scholar":
            return self.get("sources.google_scholar.max_results", 50)
        return 100
    
    def get_pdf_storage_path(self):
        """获取PDF存储路径"""
        path = self.get("pdf.storage_path", "data/pdf")
        # 确保目录存在
        os.makedirs(path, exist_ok=True)
        return path
    
    def get_database_path(self):
        """获取数据库路径"""
        if self.get("database.type") == "sqlite":
            path = self.get("database.sqlite.db_path", "data/db/papers.db")
            # 确保目录存在
            os.makedirs(os.path.dirname(path), exist_ok=True)
            return path
        return None
    
    def get_report_output_path(self):
        """获取报告输出路径"""
        path = self.get("report.output_path", "data/reports")
        # 确保目录存在
        os.makedirs(path, exist_ok=True)
        return path

# 创建全局配置实例
config_manager = ConfigManager()
