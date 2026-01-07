"""
各个Agent的定义和实现 | Definition and Implementation of Various Agents
包括: Product Researcher, Doc Assistant, Feasibility Evaluator
"""

import json
import os
import ssl
import httpx
from typing import Any, Dict

# 禁用 SSL 警告 | Disable SSL warnings
import warnings
import urllib3
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from config import API_KEY, API_BASE_URL, MODEL_NAME


class SimpleLLM:
    """
    简单的 LLM 包装类 | Simple LLM Wrapper Class
    直接使用 HTTP 请求调用 API，绕过 SSL 证书问题
    Directly use HTTP requests to call API, bypassing SSL certificate issues
    """
    
    def __init__(self, api_key: str, base_url: str, model_name: str, temperature: float = 0.7):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.temperature = temperature
        # 创建禁用 SSL 验证的客户端，设置更长的超时时间
        # Create client with SSL verification disabled and longer timeout
        # timeout: (connect_timeout, read_timeout, write_timeout, pool_timeout)
        self.client = httpx.Client(
            verify=False, 
            timeout=httpx.Timeout(300.0, connect=30.0)  # 总超时300秒，连接超时30秒
        )
    
    def invoke(self, prompt: str, max_retries: int = 3) -> str:
        """
        调用 LLM 生成响应 | Call LLM to generate response
        
        Args:
            prompt: 输入提示词 | Input prompt
            max_retries: 最大重试次数 | Maximum retry attempts
            
        Returns:
            生成的文本响应 | Generated text response
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": 4096
        }
        
        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.client.post(url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except httpx.TimeoutException as e:
                last_error = e
                print(f"API 调用超时，正在重试 ({attempt + 1}/{max_retries})...")
                import time
                time.sleep(2)  # 等待2秒后重试
                continue
            except httpx.HTTPStatusError as e:
                raise Exception(f"LLM API 调用失败 (HTTP {e.response.status_code}): {e.response.text}")
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"API 调用失败，正在重试 ({attempt + 1}/{max_retries})...")
                    import time
                    time.sleep(2)
                    continue
                break
        
        raise Exception(f"LLM 调用失败（已重试{max_retries}次）: {str(last_error)}")
    
    def predict(self, prompt: str) -> str:
        """兼容旧版 API | Compatible with old API"""
        return self.invoke(prompt)


# 初始化 LLM 模型 | Initialize LLM Model
def init_llm():
    """
    初始化语言模型 | Initialize Language Model
    使用硅基流动的 API | Using SiliconFlow API
    """
    llm = SimpleLLM(
        api_key=API_KEY,
        base_url=API_BASE_URL,
        model_name=MODEL_NAME,
        temperature=0.7
    )
    return llm


# 为了兼容性，定义类型别名
BaseLanguageModel = SimpleLLM


def parse_json_response(response: str, expected_keys: list) -> Dict[str, Any]:
    """
    解析 LLM 返回的 JSON 响应 | Parse JSON response from LLM
    
    Args:
        response: LLM 的原始响应 | Raw response from LLM
        expected_keys: 期望的 JSON 字段列表 | List of expected JSON keys
        
    Returns:
        解析后的字典 | Parsed dictionary
    """
    import re
    
    # 清理响应文本 | Clean response text
    cleaned = response.strip()
    
    # 移除 markdown 代码块标记 | Remove markdown code block markers
    # 匹配 ```json ... ``` 或 ``` ... ```
    code_block_pattern = r'```(?:json)?\s*\n?([\s\S]*?)\n?```'
    match = re.search(code_block_pattern, cleaned)
    if match:
        cleaned = match.group(1).strip()
    
    # 尝试直接解析 | Try direct parsing
    try:
        result = json.loads(cleaned)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    
    # 尝试找到 JSON 对象 | Try to find JSON object
    json_pattern = r'\{[\s\S]*\}'
    match = re.search(json_pattern, cleaned)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass
    
    # Parsing failed, return raw response as first field
    fallback = {expected_keys[0]: response}
    for key in expected_keys[1:]:
        fallback[key] = "See original response"
    return fallback


class ProductResearcher:
    """
    产品研究员智能体 | Product Researcher Agent
    负责用户需求调研和市场调研
    Responsible for user requirement research and market research
    """
    
    def __init__(self, llm):
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
        # Build prompt
        prompt = f"""
You are an experienced product researcher. The user has provided the following product requirements:

User Requirement:
{user_input}

Please conduct the following research:
1. Analyze core user requirements
2. Conduct competitive market analysis
3. Identify target user groups
4. Provide key market insights

Please return the research results in JSON format with the following fields (all content must be in English):
- core_requirements: Core requirement analysis (in English)
- market_analysis: Market analysis (in English)
- target_users: Target users description (in English)
- market_insights: Market insights (in English)

IMPORTANT: All text content in the JSON response must be in English only.
"""
        
        # 调用 LLM 获取调研结果 | Call LLM to get research results
        response = self.llm.invoke(prompt)
        
        # 尝试解析 JSON 响应 | Try to parse JSON response
        research_result = parse_json_response(response, [
            "core_requirements", "market_analysis", "target_users", "market_insights"
        ])
        
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
    
    def __init__(self, llm):
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
        # Build prompt including research results
        prompt = f"""
You are a professional product documentation expert. Based on the following information, generate a professional Product Requirements Document (PRD):

User Requirement:
{user_input}

Research Results:
{json.dumps(research_result, ensure_ascii=False)}

Please generate a professional Product Requirements Document that includes the following sections:
1. Product Overview
2. Core Feature Requirements
3. User Stories
4. Functional Specifications
5. Non-functional Requirements
6. Success Metrics

IMPORTANT: 
- Return the document content in Markdown format
- All content must be written in English only
- Use clear, professional English throughout the document
"""
        
        # 调用 LLM 生成文档 | Call LLM to generate document
        doc_content = self.llm.invoke(prompt)
        
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
    
    def __init__(self, llm):
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
        # Build prompt including previous outputs
        prompt = f"""
You are a senior technical architect and project evaluation expert. Based on the following information, conduct a comprehensive feasibility assessment:

User Requirement:
{user_input}

Research Results:
{json.dumps(research_result, ensure_ascii=False)}

Product Document:
{doc_content}

Please conduct a detailed feasibility assessment from the following aspects:

1. Technical Feasibility Assessment
   - Required technology stack
   - Technical risk analysis
   - Technical complexity

2. Technical Architecture Design
   - Recommended system architecture
   - Key module design
   - Scalability considerations

3. Cost Assessment
   - Development cost estimation
   - Infrastructure cost
   - Maintenance cost

4. Compliance Assessment
   - Data privacy compliance
   - Security requirements
   - Industry standard compliance

Please return the evaluation results in JSON format with the following main fields (all content must be in English):
- technical_feasibility: Technical feasibility analysis (in English)
- architecture_design: Architecture design description (in English)
- cost_estimation: Cost estimation details (in English)
- compliance_requirements: Compliance requirements (in English)
- risks_and_recommendations: Risks and recommendations (in English)

IMPORTANT: All text content in the JSON response must be in English only.
"""
        
        # 调用 LLM 进行评估 | Call LLM to conduct assessment
        response = self.llm.invoke(prompt)
        
        # 尝试解析 JSON 响应 | Try to parse JSON response
        evaluation_result = parse_json_response(response, [
            "technical_feasibility", "architecture_design", "cost_estimation",
            "compliance_requirements", "risks_and_recommendations"
        ])
        
        return {
            "agent": self.name,
            "evaluation_result": evaluation_result,
            "status": "completed"  # 完成状态 | Completed status
        }
