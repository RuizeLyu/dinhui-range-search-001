import os
import matplotlib.pyplot as plt
import logging
from src.core.config import config_manager

logger = logging.getLogger(__name__)

class VisualizationManager:
    """数据可视化管理器"""
    
    def __init__(self):
        self.config = config_manager
        self.output_path = os.path.join(self.config.get_report_output_path(), "charts")
        # 确保图表目录存在
        os.makedirs(self.output_path, exist_ok=True)
    
    def generate_yearly_chart(self, yearly_distribution):
        """生成年度分布图表"""
        try:
            if not yearly_distribution:
                logger.warning("没有年度分布数据，无法生成图表")
                return None
            
            # 准备数据
            years = sorted(yearly_distribution.keys())
            counts = [yearly_distribution[year] for year in years]
            
            # 创建图表
            plt.figure(figsize=(10, 6))
            plt.bar(years, counts, color='skyblue')
            plt.title('Annual Paper Distribution')
            plt.xlabel('Year')
            plt.ylabel('Number of Papers')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            # 保存图表
            chart_path = os.path.join(self.output_path, "yearly_distribution.png")
            plt.savefig(chart_path)
            plt.close()
            
            logger.info(f"年度分布图表生成成功: {chart_path}")
            return chart_path
        except Exception as e:
            logger.error(f"生成年度分布图表失败: {str(e)}")
            return None
    
    def generate_source_chart(self, source_distribution):
        """生成来源分布图表"""
        try:
            if not source_distribution:
                logger.warning("没有来源分布数据，无法生成图表")
                return None
            
            # 准备数据
            sources = list(source_distribution.keys())
            counts = list(source_distribution.values())
            
            # 创建图表
            plt.figure(figsize=(10, 6))
            plt.pie(counts, labels=sources, autopct='%1.1f%%', startangle=90)
            plt.title('Source Distribution')
            plt.axis('equal')  # 确保饼图是圆形
            plt.tight_layout()
            
            # 保存图表
            chart_path = os.path.join(self.output_path, "source_distribution.png")
            plt.savefig(chart_path)
            plt.close()
            
            logger.info(f"来源分布图表生成成功: {chart_path}")
            return chart_path
        except Exception as e:
            logger.error(f"生成来源分布图表失败: {str(e)}")
            return None
    
    def generate_citations_chart(self, papers):
        """生成引用次数图表"""
        try:
            # 过滤有引用次数的论文
            cited_papers = [(paper.get('title'), paper.get('citations')) for paper in papers 
                          if paper.get('citations') is not None]
            
            if not cited_papers:
                logger.warning("没有引用次数数据，无法生成图表")
                return None
            
            # 按引用次数排序
            cited_papers.sort(key=lambda x: x[1], reverse=True)
            # 取前10篇
            top_papers = cited_papers[:10]
            titles = [paper[0][:30] + '...' if len(paper[0]) > 30 else paper[0] for paper in top_papers]
            citations = [paper[1] for paper in top_papers]
            
            # 创建图表
            plt.figure(figsize=(12, 8))
            plt.barh(titles, citations, color='lightgreen')
            plt.title('Top 10 Most Cited Papers')
            plt.xlabel('Number of Citations')
            plt.ylabel('Paper Title')
            plt.grid(axis='x', linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            # 保存图表
            chart_path = os.path.join(self.output_path, "citations_chart.png")
            plt.savefig(chart_path)
            plt.close()
            
            logger.info(f"引用次数图表生成成功: {chart_path}")
            return chart_path
        except Exception as e:
            logger.error(f"生成引用次数图表失败: {str(e)}")
            return None
