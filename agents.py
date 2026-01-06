"""
各个Agent的定义和实现 | Definition and Implementation of Various Agents
包括: Product Researcher, Doc Assistant, Feasibility Evaluator
"""

import json
from typing import Any, Dict
from langchain.base_language_model import BaseLanguageModel
from langchain_community.llms import OpenAI
from config import API_KEY, API_BASE_URL, MODEL_NAME

# 初始化 LLM 模型 | Initialize LLM Model
def init_llm():
    """
    初始化语言模型 | Initialize Language Model
    使用硅基流动的 API | Using SiliconFlow API
    """
    llm = OpenAI(
        api_key=API_KEY,
        api_base=API_BASE_URL,
        model_name=MODEL_NAME,
        temperature=0.7,  # 温度参数（0-1），控制生成的随机性 | Temperature parameter (0-1), controls randomness
    )
    return llm


class ProductResearcher:
    """
    产品研究员智能体 | Product Researcher Agent
    负责用户需求调研和市场调研
    Responsible for user requirement research and market research
    """
    
    def __init__(self, llm: BaseLanguageModel):
        """
        初始化产品研究员 | Initialize Product Researcher
        
        Args:
            llm: 语言模型实例 | Language model instance
        """
        self.llm = llm
        self.name = "Product Researcher"
    
    def research(self, user_input: str) -> Dict[str, Any]:
        """
        执行需求调研 | Conduct requirement research
        
        Args:
            user_input: 用户输入的产品需求 | User input product requirements
            
        Returns:
            包含调研结果的字典 | Dictionary containing research results
        """
        # 构建提示词 | Build prompt
        prompt = f"""
你是一位资深的产品研究员。用户提出了以下产品需求：

用户需求 | User Requirement:
{user_input}

请执行以下调研工作：
1. 分析用户的核心需求 | Analyze core user requirements
2. 进行市场竞品分析 | Conduct competitive analysis
3. 识别目标用户群体 | Identify target user groups
4. 提出关键的市场洞察 | Provide key market insights

请以JSON格式返回调研结果，包含以下字段：
- core_requirements: 核心需求分析
- market_analysis: 市场分析
- target_users: 目标用户
- market_insights: 市场洞察

Return in JSON format with the following fields:
- core_requirements: Core requirement analysis
- market_analysis: Market analysis
- target_users: Target users
- market_insights: Market insights
"""
        
        # 调用 LLM 获取调研结果 | Call LLM to get research results
        response = self.llm.predict(prompt)
        
        # 尝试解析 JSON 响应 | Try to parse JSON response
        try:
            research_result = json.loads(response)
        except:
            # 如果解析失败，将响应包装成字典 | If parsing fails, wrap response as dictionary
            research_result = {
                "core_requirements": response,
                "market_analysis": "详见原始响应 | See original response",
                "target_users": "待进一步分析 | To be analyzed further",
                "market_insights": "待进一步分析 | To be analyzed further"
            }
        
        return {
            "agent": self.name,
            "research_result": research_result,
            "status": "completed"  # 完成状态 | Completed status
        }


class DocAssistant:
    """
    产品文档助手智能体 | Doc Assistant Agent
    负责产品需求文档的生成
    Responsible for generating product requirement documents
    """
    
    def __init__(self, llm: BaseLanguageModel):
        """
        初始化文档助手 | Initialize Doc Assistant
        
        Args:
            llm: 语言模型实例 | Language model instance
        """
        self.llm = llm
        self.name = "Doc Assistant"
    
    def generate_doc(self, user_input: str, research_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成产品需求文档 | Generate product requirement document
        
        Args:
            user_input: 用户的初始输入 | User's initial input
            research_result: 产品研究员的调研结果 | Product Researcher's research results
            
        Returns:
            包含文档内容的字典 | Dictionary containing document content
        """
        # 构建包含调研结果的提示词 | Build prompt including research results
        prompt = f"""
你是一位专业的产品文档撰写专家。基于以下信息生成专业的产品需求文档（PRD）：

用户需求 | User Requirement:
{user_input}

调研结果 | Research Results:
{json.dumps(research_result, ensure_ascii=False)}

请生成一份专业的产品需求文档，包含以下部分：
1. 产品概述 | Product Overview
2. 核心功能需求 | Core Feature Requirements
3. 用户故事 | User Stories
4. 功能规格 | Functional Specifications
5. 非功能需求 | Non-functional Requirements
6. 成功指标 | Success Metrics

请以Markdown格式返回文档内容。
Return document content in Markdown format.
"""
        
        # 调用 LLM 生成文档 | Call LLM to generate document
        doc_content = self.llm.predict(prompt)
        
        return {
            "agent": self.name,
            "document": doc_content,  # 文档内容 | Document content
            "status": "completed"  # 完成状态 | Completed status
        }


class FeasibilityEvaluator:
    """
    可行性评估专家智能体 | Feasibility Evaluator Agent
    负责用户需求的可行性评估，包括技术可行性、技术架构设计、成本考量和合规性考量
    Responsible for feasibility assessment including technical feasibility, 
    technical architecture design, cost considerations, and compliance considerations
    """
    
    def __init__(self, llm: BaseLanguageModel):
        """
        初始化可行性评估员 | Initialize Feasibility Evaluator
        
        Args:
            llm: 语言模型实例 | Language model instance
        """
        self.llm = llm
        self.name = "Feasibility Evaluator"
    
    def evaluate(self, user_input: str, research_result: Dict[str, Any], doc_content: str) -> Dict[str, Any]:
        """
        执行可行性评估 | Conduct feasibility assessment
        
        Args:
            user_input: 用户的初始输入 | User's initial input
            research_result: 产品研究员的调研结果 | Product Researcher's research results
            doc_content: 文档助手生成的文档 | Document generated by Doc Assistant
            
        Returns:
            包含评估结果的字典 | Dictionary containing assessment results
        """
        # 构建包含前期输出的提示词 | Build prompt including previous outputs
        prompt = f"""
你是一位资深的技术架构师和项目评估专家。基于以下信息进行全面的可行性评估：

用户需求 | User Requirement:
{user_input}

调研结果 | Research Results:
{json.dumps(research_result, ensure_ascii=False)}

产品文档 | Product Document:
{doc_content}

请从以下方面进行详细的可行性评估：

1. 技术可行性评估 | Technical Feasibility Assessment
   - 所需技术栈 | Required technology stack
   - 技术风险分析 | Technical risk analysis
   - 技术复杂度 | Technical complexity

2. 技术架构设计 | Technical Architecture Design
   - 推荐的系统架构 | Recommended system architecture
   - 主要模块设计 | Key module design
   - 扩展性考虑 | Scalability considerations

3. 成本评估 | Cost Assessment
   - 开发成本预估 | Development cost estimation
   - 基础设施成本 | Infrastructure cost
   - 维护成本 | Maintenance cost

4. 合规性评估 | Compliance Assessment
   - 数据隐私合规 | Data privacy compliance
   - 安全性要求 | Security requirements
   - 行业标准遵循 | Industry standard compliance

请以JSON格式返回评估结果，包含以下主要字段：
- technical_feasibility: 技术可行性
- architecture_design: 架构设计
- cost_estimation: 成本预估
- compliance_requirements: 合规要求
- risks_and_recommendations: 风险和建议

Return in JSON format with the above main fields.
"""
        
        # 调用 LLM 进行评估 | Call LLM to conduct assessment
        response = self.llm.predict(prompt)
        
        # 尝试解析 JSON 响应 | Try to parse JSON response
        try:
            evaluation_result = json.loads(response)
        except:
            # 如果解析失败，将响应包装成字典 | If parsing fails, wrap response as dictionary
            evaluation_result = {
                "technical_feasibility": response,
                "architecture_design": "详见原始响应 | See original response",
                "cost_estimation": "待评估 | To be evaluated",
                "compliance_requirements": "待评估 | To be evaluated",
                "risks_and_recommendations": "待评估 | To be evaluated"
            }
        
        return {
            "agent": self.name,
            "evaluation_result": evaluation_result,
            "status": "completed"  # 完成状态 | Completed status
        }
