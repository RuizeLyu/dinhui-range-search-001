import os
import logging
from src.core.config import config_manager

logger = logging.getLogger(__name__)

class PromptManager:
    def __init__(self):
        self.config = config_manager
        self.prompts_dir = "config/prompts"
    
    def get_paper_analysis_prompt(self, text):
        """获取论文分析提示词"""
        # 尝试从文件中读取提示词模板
        prompt_template_path = os.path.join(self.prompts_dir, "paper_analysis_prompt.txt")
        
        if os.path.exists(prompt_template_path):
            try:
                with open(prompt_template_path, 'r', encoding='utf-8') as f:
                    prompt_template = f.read()
                # 替换文本占位符
                prompt = prompt_template.replace("{extracted_text}", text[:80000])  # 限制文本长度
                return prompt
            except Exception as e:
                logger.error(f"读取提示词模板失败: {str(e)}")
        
        # 如果文件不存在，使用默认提示词
        default_prompt = f"""你是一位资深科研人员。请阅读以下论文全文，并按以下格式回答：

【研究问题】：
【提出方法】：
【关键技术】：
【实验效果】：
【局限性】：
【是否开源】：

论文内容：
{text[:80000]}
"""
        return default_prompt
    
    def get_report_generation_prompt(self, domain, start_year, end_year, papers_summary):
        """获取报告生成提示词"""
        prompt = f"""你是一位领域专家，请基于以下论文摘要，生成一份关于"{domain}"领域的综述报告。

时间范围：{start_year}-{end_year}

论文摘要：
{papers_summary}

报告应包括以下部分：
1. 领域概述
2. 研究趋势分析
3. 主流方法与技术路线
4. 关键创新点
5. 存在的问题与挑战
6. 未来研究方向
7. 结论

请确保报告内容全面、客观、深入，能够反映该领域的最新发展现状。
"""
        return prompt
    
    def get_method_comparison_prompt(self, methods):
        """获取方法比较提示词"""
        methods_text = "\n".join([f"- {method}" for method in methods])
        prompt = f"""请对以下研究方法进行比较分析：

{methods_text}

分析应包括：
1. 各方法的核心思想
2. 优缺点比较
3. 适用场景
4. 性能对比
5. 发展趋势

请提供详细、客观的比较分析。
"""
        return prompt
