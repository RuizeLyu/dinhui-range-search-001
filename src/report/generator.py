import os
import datetime
import logging
from jinja2 import Template
from src.core.config import config_manager
from src.database.db_manager import DatabaseManager
from src.database.queries import PaperQueries
from src.llm.prompts import PromptManager
from .visualization import VisualizationManager

logger = logging.getLogger(__name__)

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.config = config_manager
        self.output_path = self.config.get_report_output_path()
        self.format = self.config.get("report.format", "markdown")
        self.generate_charts = self.config.get("report.generate_charts", True)
        self.db_manager = DatabaseManager()
        self.paper_queries = PaperQueries(self.db_manager.conn)
        self.prompt_manager = PromptManager()
        self.visualization = VisualizationManager()
    
    def generate(self):
        """生成报告"""
        try:
            # 获取研究领域和时间范围
            domain = self.config.get_research_domain()
            start_year, end_year = self.config.get_time_range()
            
            # 获取论文数据
            papers = self.db_manager.get_all_papers()
            if not papers:
                logger.warning("没有论文数据，无法生成报告")
                return None
            
            # 获取统计信息
            stats = self.paper_queries.get_papers_statistics()
            
            # 生成图表
            charts = {}
            if self.generate_charts:
                charts = self._generate_charts(stats)
            
            # 生成论文摘要
            papers_summary = self._generate_papers_summary(papers)
            
            # 生成报告内容
            report_content = self._generate_report_content(
                domain, start_year, end_year, papers, stats, charts, papers_summary
            )
            
            # 保存报告
            report_path = self._save_report(report_content, domain, start_year, end_year)
            
            logger.info(f"报告生成成功: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"生成报告失败: {str(e)}")
            return None
    
    def _generate_charts(self, stats):
        """生成图表"""
        charts = {}
        
        # 生成年度分布图表
        yearly_chart = self.visualization.generate_yearly_chart(stats.get("yearly_distribution", {}))
        if yearly_chart:
            charts["yearly"] = yearly_chart
        
        # 生成来源分布图表
        source_chart = self.visualization.generate_source_chart(stats.get("source_distribution", {}))
        if source_chart:
            charts["source"] = source_chart
        
        return charts
    
    def _generate_papers_summary(self, papers):
        """生成论文摘要"""
        summaries = []
        for paper in papers:
            if paper.get("research_problem") and paper.get("method_summary"):
                summary = f"""
                标题: {paper.get('title')}
                年份: {paper.get('publish_year')}
                来源: {paper.get('source')}
                研究问题: {paper.get('research_problem')}
                方法: {paper.get('method_summary')}
                创新点: {paper.get('innovation')}
                """
                summaries.append(summary)
        
        return "\n".join(summaries[:20])  # 限制摘要数量
    
    def _generate_report_content(self, domain, start_year, end_year, papers, stats, charts, papers_summary):
        """生成报告内容"""
        # 生成LLM提示词
        prompt = self.prompt_manager.get_report_generation_prompt(
            domain, start_year, end_year, papers_summary
        )
        
        # 这里应该调用LLM生成报告内容
        # 由于是示例，使用模板生成
        report_content = self._generate_from_template(
            domain, start_year, end_year, papers, stats, charts
        )
        
        return report_content
    
    def _generate_from_template(self, domain, start_year, end_year, papers, stats, charts):
        """从模板生成报告"""
        # 读取模板文件
        template_path = os.path.join(os.path.dirname(__file__), "templates", "report_template.md")
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        else:
            # 使用默认模板
            template_content = self._get_default_template()
        
        # 渲染模板
        template = Template(template_content)
        report_content = template.render(
            domain=domain,
            start_year=start_year,
            end_year=end_year,
            papers=papers,
            stats=stats,
            charts=charts,
            generation_date=datetime.datetime.now().strftime("%Y-%m-%d"),
            total_papers=len(papers),
            yearly_distribution=stats.get("yearly_distribution", {}),
            source_distribution=stats.get("source_distribution", {})
        )
        
        return report_content
    
    def _get_default_template(self):
        """获取默认报告模板"""
        return """
# {{ domain }} 领域综述报告

## 报告信息

- **研究领域**: {{ domain }}
- **时间范围**: {{ start_year }}-{{ end_year }}
- **报告生成日期**: {{ generation_date }}
- **论文总数**: {{ total_papers }}

## 1. 领域概述

本报告对{{ domain }}领域的研究现状进行了全面分析，基于{{ total_papers }}篇相关论文的数据。

## 2. 研究趋势分析

### 2.1 年度论文分布

{% if charts.yearly %}
![年度论文分布]({{ charts.yearly }})
{% else %}
| 年份 | 论文数量 |
|------|----------|
{% for year, count in yearly_distribution.items() %}
| {{ year }} | {{ count }} |
{% endfor %}
{% endif %}

### 2.2 来源分布

{% if charts.source %}
![来源分布]({{ charts.source }})
{% else %}
| 来源 | 论文数量 |
|------|----------|
{% for source, count in source_distribution.items() %}
| {{ source }} | {{ count }} |
{% endfor %}
{% endif %}

## 3. 主流方法与技术路线

## 4. 关键创新点

## 5. 存在的问题与挑战

## 6. 未来研究方向

## 7. 结论

## 8. 参考文献

{% for paper in papers %}
- {{ paper.title }} ({{ paper.publish_year }})
{% endfor %}
"""
    
    def _save_report(self, content, domain, start_year, end_year):
        """保存报告"""
        # 生成文件名
        safe_domain = "".join(c for c in domain if c.isalnum() or c in " -_")
        filename = f"{safe_domain}_{start_year}-{end_year}_{datetime.datetime.now().strftime('%Y%m%d')}.md"
        report_path = os.path.join(self.output_path, filename)
        
        # 保存文件
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return report_path
