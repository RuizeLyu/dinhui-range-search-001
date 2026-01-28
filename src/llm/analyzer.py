import os
import logging
import json
import random
from src.core.config import config_manager
from .prompts import PromptManager

logger = logging.getLogger(__name__)

class SPOptimizer:
    """Self-Play Optimization 提示词优化器"""
    
    def __init__(self):
        self.config = config_manager
        self.spo_enabled = self.config.get("llm.spo.enabled", False)
        self.optimization_rounds = self.config.get("llm.spo.optimization_rounds", 10)
        self.samples_per_round = self.config.get("llm.spo.samples_per_round", 3)
        self.evaluation_model_type = self.config.get("llm.spo.evaluation_model", "local")
        self.optimizer_model_type = self.config.get("llm.spo.optimizer_model", "api")
        self.prompt_manager = PromptManager()
        
    def optimize_prompt(self, initial_prompt, sample_texts):
        """优化提示词"""
        if not self.spo_enabled:
            return initial_prompt
        
        logger.info("开始使用SPO优化提示词")
        best_prompt = initial_prompt
        best_score = 0
        
        # 初始化评估模型
        evaluation_model = self._get_model(self.evaluation_model_type)
        # 初始化优化器模型
        optimizer_model = self._get_model(self.optimizer_model_type)
        
        for round_idx in range(self.optimization_rounds):
            logger.info(f"SPO优化轮次: {round_idx+1}/{self.optimization_rounds}")
            
            # 生成候选提示词
            candidate_prompt = self._generate_candidate_prompt(optimizer_model, best_prompt)
            
            # 采样评估文本
            sampled_texts = random.sample(sample_texts, min(self.samples_per_round, len(sample_texts)))
            
            # 评估候选提示词
            candidate_score = self._evaluate_prompt(evaluation_model, candidate_prompt, sampled_texts)
            current_score = self._evaluate_prompt(evaluation_model, best_prompt, sampled_texts)
            
            logger.info(f"当前最佳提示词得分: {current_score}, 候选提示词得分: {candidate_score}")
            
            # 更新最佳提示词
            if candidate_score > current_score:
                best_prompt = candidate_prompt
                best_score = candidate_score
                logger.info("更新最佳提示词")
        
        logger.info("SPO提示词优化完成")
        return best_prompt
    
    def _get_model(self, model_type):
        """获取模型实例"""
        if model_type == "local":
            return LocalLLMModel()
        else:
            return APILocalModel()
    
    def _generate_candidate_prompt(self, model, current_prompt):
        """生成候选提示词"""
        prompt = f"""
你是一位提示词优化专家。请基于以下当前提示词，生成一个改进版本，使其更适合分析skill evolution相关的论文：

当前提示词：
{current_prompt}

改进要求：
1. 保持原有的结构和格式
2. 增强对skill evolution、强化学习、self-evoagent等相关概念的关注
3. 提高提取信息的准确性和完整性
4. 确保提示词清晰明了，易于LLM理解

请直接输出改进后的完整提示词，不要添加任何解释或注释。
"""
        
        response = model.generate(prompt)
        return response.strip()
    
    def _evaluate_prompt(self, model, prompt, sample_texts):
        """评估提示词"""
        total_score = 0
        
        for text in sample_texts:
            # 生成分析结果
            evaluation_prompt = prompt.replace("{extracted_text}", text[:2000])  # 使用文本前2000字符
            response = model.generate(evaluation_prompt)
            
            # 评估响应质量
            score = self._score_response(response)
            total_score += score
        
        return total_score / len(sample_texts)
    
    def _score_response(self, response):
        """评分响应质量"""
        # 简单的评分机制：检查是否包含所有必要部分
        sections = ["【研究问题】：", "【提出方法】：", "【关键技术】：", "【实验效果】：", "【局限性】：", "【是否开源】："]
        score = 0
        
        for section in sections:
            if section in response:
                section_content = response.split(section)[1].split("【")[0].strip()
                if len(section_content) > 10:  # 内容长度至少10字符
                    score += 1
        
        return score / len(sections)

class LLMAnalyzer:
    def __init__(self):
        self.config = config_manager
        self.prompt_manager = PromptManager()
        self.model_type = self.config.get("llm.model_type", "local")
        self.spo_optimizer = SPOptimizer()
        self.model = self._initialize_model()
        self.optimized_prompt = None
    
    def _initialize_model(self):
        """初始化LLM模型"""
        if self.model_type == "local":
            # 尝试初始化本地模型
            try:
                # 这里应该集成DeepSeek-R1的本地部署
                # 由于DeepSeek-R1的具体部署方式可能不同，这里提供一个占位符
                logger.info("使用本地LLM模型")
                return LocalLLMModel()
            except Exception as e:
                logger.error(f"初始化本地模型失败: {str(e)}")
                logger.info("回退到API模型")
                return APILocalModel()
        else:
            # 使用API模型
            logger.info("使用API LLM模型")
            return APILocalModel()
    
    def analyze(self, text):
        """使用LLM分析论文内容"""
        try:
            # 获取提示词
            if not self.optimized_prompt:
                # 首次运行，优化提示词
                initial_prompt = self.prompt_manager.get_paper_analysis_prompt("示例文本")
                # 使用当前文本作为样本进行优化
                self.optimized_prompt = self.spo_optimizer.optimize_prompt(initial_prompt, [text])
            
            # 使用优化后的提示词
            prompt = self.optimized_prompt.replace("{extracted_text}", text)
            
            # 调用模型
            response = self.model.generate(prompt)
            
            # 解析响应
            analysis = self._parse_response(response)
            
            return analysis
        except Exception as e:
            logger.error(f"LLM分析失败: {str(e)}")
            return None
    
    def _parse_response(self, response):
        """解析LLM响应"""
        try:
            # 提取各个部分
            analysis = {
                "research_problem": self._extract_section(response, "【研究问题】："),
                "method_summary": self._extract_section(response, "【提出方法】："),
                "innovation": self._extract_section(response, "【关键技术】："),
                "experimental_results": self._extract_section(response, "【实验效果】："),
                "limitations": self._extract_section(response, "【局限性】："),
                "is_open_source": self._extract_boolean(response, "【是否开源】：")
            }
            
            return analysis
        except Exception as e:
            logger.error(f"解析LLM响应失败: {str(e)}")
            return {}
    
    def _extract_section(self, text, section_header):
        """提取响应中的特定部分"""
        start_idx = text.find(section_header)
        if start_idx == -1:
            return ""
        
        start_idx += len(section_header)
        
        # 查找下一个部分的开始
        next_sections = ["【研究问题】：", "【提出方法】：", "【关键技术】：", "【实验效果】：", "【局限性】：", "【是否开源】："]
        end_idx = len(text)
        
        for section in next_sections:
            if section == section_header:
                continue
            idx = text.find(section, start_idx)
            if idx != -1 and idx < end_idx:
                end_idx = idx
        
        # 提取内容并清理
        content = text[start_idx:end_idx].strip()
        return content
    
    def _extract_boolean(self, text, section_header):
        """提取布尔值"""
        content = self._extract_section(text, section_header).lower()
        if any(word in content for word in ["是", "yes", "开源", "open source", "true"]):
            return True
        elif any(word in content for word in ["否", "no", "closed", "false"]):
            return False
        else:
            return None

class LocalLLMModel:
    """本地LLM模型接口"""
    def generate(self, prompt):
        """生成响应"""
        # 这里应该集成DeepSeek-R1的调用代码
        # 由于是占位符，返回一个模拟的响应
        logger.warning("使用本地模型占位符，返回模拟响应")
        return """【研究问题】：
Skill evolution在强化学习中的自主技能获取问题

【提出方法】：
提出了一种基于self-evoagent的技能演化框架，通过强化学习实现自主技能获取和优化

【关键技术】：
1. 深度强化学习算法
2. 自主探索机制
3. 技能迁移学习
4. 元学习策略

【实验效果】：
在多个技能任务上实现了90%以上的成功率，技能获取速度比传统方法提高了30%

【局限性】：
1. 需要大量的计算资源
2. 在复杂环境中的表现有待提升
3. 技能泛化能力有限

【是否开源】：
是
"""

class APILocalModel:
    """API LLM模型接口"""
    def generate(self, prompt):
        """生成响应"""
        # 这里应该集成API调用代码（如OpenAI API）
        # 由于是占位符，返回一个模拟的响应
        logger.warning("使用API模型占位符，返回模拟响应")
        return """【研究问题】：
Skill evolution在多任务学习中的技能迁移和泛化问题

【提出方法】：
开发了一个基于强化学习的self-evoagent系统，实现跨任务的技能演化

【关键技术】：
1. 多任务强化学习
2. 技能表示学习
3. 自适应探索策略
4. 终身学习机制

【实验效果】：
在连续任务学习中，技能迁移成功率达到85%，学习效率提升40%

【局限性】：
1. 对任务相似度有一定要求
2. 计算开销较大
3. 需要精心设计奖励函数

【是否开源】：
否
"""
