"""
各个Agent的定义和实现 | Definition and Implementation of Various Agents
包括: Product Researcher (LangGraph ReAct Agent), Doc Assistant, Feasibility Evaluator
"""

import json
import os
import ssl
import httpx
from typing import Any, Dict, List, Optional

# 禁用 SSL 警告 | Disable SSL warnings
import warnings
import urllib3
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from config import API_KEY, API_BASE_URL, MODEL_NAME
from logger_config import logger, log_function_call

# LangGraph imports for ReAct Agent
try:
    from langgraph.prebuilt import create_react_agent
    from langchain_core.tools import tool
    LANGGRAPH_REACT_AVAILABLE = True
except ImportError as e:
    LANGGRAPH_REACT_AVAILABLE = False
    logger.warning(f"LangGraph prebuilt not available: {e}")

# LangChain OpenAI for LLM
# 延迟导入以避免 SSL 权限问题
LANGCHAIN_OPENAI_AVAILABLE = False
try:
    # 尝试导入，但如果遇到 SSL 权限问题则延迟到使用时导入
    import ssl
    # 设置环境变量以避免 SSL 权限问题
    import os
    import certifi
    if 'SSL_CERT_FILE' not in os.environ:
        os.environ['SSL_CERT_FILE'] = certifi.where()
    if 'REQUESTS_CA_BUNDLE' not in os.environ:
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    
    # 延迟导入检查
    LANGCHAIN_OPENAI_AVAILABLE = None  # None 表示延迟检查
    logger.debug("LangChain OpenAI import will be checked when needed")
except Exception as e:
    LANGCHAIN_OPENAI_AVAILABLE = False
    logger.warning(f"⚠️  SSL setup warning: {e}")

def _check_langchain_openai():
    """检查并导入 LangChain OpenAI，延迟执行以避免 SSL 权限问题"""
    global LANGCHAIN_OPENAI_AVAILABLE
    if LANGCHAIN_OPENAI_AVAILABLE is not None:
        return LANGCHAIN_OPENAI_AVAILABLE
    
    try:
        from langchain_openai import ChatOpenAI
        LANGCHAIN_OPENAI_AVAILABLE = True
        logger.info("✓ LangChain OpenAI available")
        return True
    except ImportError as e:
        LANGCHAIN_OPENAI_AVAILABLE = False
        logger.warning(f"⚠️  LangChain OpenAI not available: {e}")
        logger.warning("⚠️  To enable ReAct Agent, please install: pip install langchain-openai")
        return False
    except PermissionError as e:
        LANGCHAIN_OPENAI_AVAILABLE = False
        logger.warning(f"⚠️  LangChain OpenAI SSL permission error: {e}")
        logger.warning("⚠️  This may be due to macOS security restrictions")
        return False
    except Exception as e:
        LANGCHAIN_OPENAI_AVAILABLE = False
        logger.warning(f"⚠️  LangChain OpenAI import failed: {e}")
        return False


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
        self.client = httpx.Client(
            verify=False, 
            timeout=httpx.Timeout(300.0, connect=30.0)
        )
    
    @log_function_call
    def invoke(self, prompt: str, max_retries: int = 3) -> str:
        """
        调用 LLM 生成响应 | Call LLM to generate response
        """
        logger.debug(f"LLM invoke called - Model: {self.model_name}, Prompt length: {len(prompt)}")
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": 4096
        }
        
        import time
        last_error = None
        for attempt in range(max_retries):
            try:
                logger.info(f"LLM API call attempt {attempt + 1}/{max_retries}")
                response = self.client.post(url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                logger.info(f"✓ LLM API call successful, response length: {len(content)}")
                return content
            except httpx.TimeoutException as e:
                last_error = e
                wait_time = 2 * (attempt + 1)  # 指数退避：2, 4, 6 秒
                logger.warning(f"API call timeout, retrying in {wait_time}s ({attempt + 1}/{max_retries})...")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                error_text = e.response.text
                
                # 尝试解析错误响应
                try:
                    error_json = e.response.json()
                    error_code = error_json.get("code", "unknown")
                    error_msg = error_json.get("message", error_text)
                    logger.error(f"LLM API call failed (HTTP {status_code}, Code: {error_code}): {error_msg}")
                except:
                    logger.error(f"LLM API call failed (HTTP {status_code}): {error_text}")
                
                # 对于服务器错误（5xx）和限流（429），进行重试
                if status_code >= 500 or status_code == 429:
                    last_error = e
                    wait_time = 2 * (attempt + 1)  # 指数退避
                    logger.warning(f"Server error or rate limit, retrying in {wait_time}s ({attempt + 1}/{max_retries})...")
                    if attempt < max_retries - 1:
                        time.sleep(wait_time)
                        continue
                else:
                    # 对于客户端错误（4xx，除了429），不重试
                    logger.error(f"Client error (HTTP {status_code}), not retrying")
                    raise Exception(f"LLM API call failed (HTTP {status_code}): {error_text}")
            except Exception as e:
                last_error = e
                wait_time = 2 * (attempt + 1)
                logger.warning(f"API call failed, retrying in {wait_time}s ({attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
                break
        
        logger.error(f"LLM call failed after {max_retries} attempts: {str(last_error)}")
        raise Exception(f"LLM call failed after {max_retries} retries: {str(last_error)}")
    
    def predict(self, prompt: str) -> str:
        """兼容旧版 API | Compatible with old API"""
        return self.invoke(prompt)


def init_llm():
    """
    初始化语言模型 | Initialize Language Model
    """
    llm = SimpleLLM(
        api_key=API_KEY,
        base_url=API_BASE_URL,
        model_name=MODEL_NAME,
        temperature=0.7
    )
    return llm


def parse_json_response(response: str, expected_keys: list) -> Dict[str, Any]:
    """
    解析 LLM 返回的 JSON 响应 | Parse JSON response from LLM
    """
    import re
    
    cleaned = response.strip()
    original_response = cleaned
    
    # 移除 markdown 代码块标记
    code_block_pattern = r'```(?:json)?\s*\n?([\s\S]*?)\n?```'
    match = re.search(code_block_pattern, cleaned)
    if match:
        cleaned = match.group(1).strip()
    
    # 尝试直接解析
    try:
        result = json.loads(cleaned)
        if isinstance(result, dict) and len(result) > 0:
            logger.debug(f"Successfully parsed JSON with {len(result)} keys")
            return result
    except json.JSONDecodeError as e:
        logger.debug(f"Direct JSON parse failed: {e}")
        pass
    
    # 尝试找到 JSON 对象（更宽松的匹配）
    json_pattern = r'\{[\s\S]*\}'
    matches = re.finditer(json_pattern, cleaned)
    for match in matches:
        try:
            result = json.loads(match.group())
            if isinstance(result, dict) and len(result) > 0:
                logger.debug(f"Successfully parsed JSON from pattern match with {len(result)} keys")
                return result
        except json.JSONDecodeError:
            continue
    
    # 如果所有解析都失败，尝试从文本中提取结构化信息
    logger.warning("JSON parsing failed, attempting to extract structured information from text")
    
    # 尝试按字段名提取内容（支持多种格式变体）
    extracted = {}
    for key in expected_keys:
        # 生成字段名的多种变体
        key_variants = [
            key,  # core_requirements
            key.replace('_', ' '),  # core requirements
            key.replace('_', '-'),  # core-requirements
        ]
        
        found = False
        for variant in key_variants:
            # 转义特殊字符用于正则表达式
            escaped_variant = re.escape(variant)
            
            # 模式1: "Key: value" 单行
            pattern1 = escaped_variant + r'["\']?\s*[:：]\s*["\']?([^"\'\n]+)'
            match = re.search(pattern1, cleaned, re.IGNORECASE)
            if match:
                value = match.group(1).strip().strip('"\'')
                if value and len(value) > 5:
                    extracted[key] = value
                    logger.debug(f"Extracted {key} using pattern1 with variant '{variant}'")
                    found = True
                    break
            
            # 模式2: "Key: value\nmore text" 多行（直到下一个字段或段落结束）
            # 构建下一个字段的正则（用于停止匹配）
            other_keys = [k.replace('_', ' ') for k in expected_keys if k != key]
            stop_pattern = '|'.join([re.escape(k) for k in other_keys[:3]])  # 限制长度避免过长
            
            pattern2 = escaped_variant + r'["\']?\s*[:：]\s*["\']?([^\n]+(?:\n(?!\s*(?:' + stop_pattern + r')[:：])[^\n]+)*)'
            match = re.search(pattern2, cleaned, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip().strip('"\'')
                if value and len(value) > 5:
                    extracted[key] = value
                    logger.debug(f"Extracted {key} using pattern2 with variant '{variant}'")
                    found = True
                    break
            
            # 模式3: "**Key:** value" (Markdown格式)
            pattern3 = r'\*\*' + escaped_variant + r'\*\*\s*[:：]?\s*([^\n]+(?:\n(?!\*\*)[^\n]+)*)'
            match = re.search(pattern3, cleaned, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip().strip('"\'')
                if value and len(value) > 5:
                    extracted[key] = value
                    logger.debug(f"Extracted {key} using pattern3 with variant '{variant}'")
                    found = True
                    break
        
        if not found:
            logger.debug(f"Could not extract {key} from text")
    
    if len(extracted) >= 2:  # 至少提取到2个字段才认为成功
        logger.info(f"Extracted {len(extracted)} fields from text: {list(extracted.keys())}")
        return extracted
    elif len(extracted) == 1:
        logger.warning(f"Only extracted 1 field from text, may not be reliable")
        return extracted
    
    # 最后的fallback：返回原始响应作为第一个字段
    logger.warning(f"All parsing attempts failed, using fallback with original response")
    fallback = {expected_keys[0]: original_response}
    for key in expected_keys[1:]:
        fallback[key] = "See original response"
    return fallback


# ============================================================================
# LangGraph ReAct Agent Tools
# ============================================================================

@tool
def analyze_requirements(user_input: str) -> str:
    """
    Analyzes core user requirements from product requirements.
    Use this tool to break down and understand the essential needs and functional requirements.
    
    Args:
        user_input: The product requirements text to analyze
    """
    logger.info("Tool: analyze_requirements called")
    return f"""
Core Requirements Analysis:
- User requirement: {user_input[:300]}...
- Analysis: Conducting deep requirement analysis to identify core needs, 
  functional requirements, and non-functional requirements.
- Key findings: Breaking down requirements into actionable components.
- Status: Tool executed successfully
"""


@tool
def market_analysis(user_input: str) -> str:
    """
    Conducts competitive market analysis.
    Use this tool to research market trends, competitors, and market opportunities.
    
    Args:
        user_input: The product concept to analyze in the market context
    """
    logger.info("Tool: market_analysis called")
    return f"""
Market Analysis:
- Product concept: {user_input[:300]}...
- Competitive landscape: Analyzing key competitors and market positioning.
- Market trends: Identifying relevant industry trends and growth areas.
- Opportunities: Highlighting potential market opportunities.
- Status: Tool executed successfully
"""


@tool
def target_users(user_input: str) -> str:
    """
    Identifies and analyzes target user groups.
    Use this tool to define user personas, demographics, and user needs.
    
    Args:
        user_input: The product concept for user analysis
    """
    logger.info("Tool: target_users called")
    return f"""
Target Users Analysis:
- Product requirement: {user_input[:300]}...
- User segmentation: Identifying primary and secondary user groups.
- Demographics: Age, profession, location, and behavior patterns.
- User needs: Pain points and desired outcomes.
- Status: Tool executed successfully
"""


@tool
def market_insights(user_input: str) -> str:
    """
    Extracts key market insights and strategic recommendations.
    Use this tool to synthesize findings into actionable insights.
    
    Args:
        user_input: The product concept for insight extraction
    """
    logger.info("Tool: market_insights called")
    return f"""
Market Insights:
- Product domain: {user_input[:300]}...
- Key insights: Strategic observations from market and user analysis.
- Recommendations: Actionable suggestions for product development.
- Risk factors: Potential challenges and mitigation strategies.
- Status: Tool executed successfully
"""


# ============================================================================
# ProductResearcher - LangGraph ReAct Agent
# ============================================================================

class ProductResearcher:
    """
    产品研究员智能体（LangGraph ReAct Agent）| Product Researcher Agent (LangGraph ReAct Agent)
    使用 LangGraph 的 prebuilt create_react_agent
    Uses LangGraph's prebuilt create_react_agent
    """
    
    def __init__(self, llm: SimpleLLM):
        """
        初始化产品研究员 | Initialize Product Researcher
        
        Args:
            llm: 语言模型实例 | Language model instance
        """
        self.simple_llm = llm
        self.name = "Product Researcher (LangGraph ReAct Agent)"
        self.react_agent = None
        
        # 创建 LangGraph ReAct Agent
        # 延迟检查 LangChain OpenAI 以避免 SSL 权限问题
        if LANGGRAPH_REACT_AVAILABLE:
            # 尝试导入 ChatOpenAI（延迟导入）
            if _check_langchain_openai():
                try:
                    from langchain_openai import ChatOpenAI
                    
                    # 使用 ChatOpenAI 作为 LLM（LangGraph 需要）
                    langchain_llm = ChatOpenAI(
                        model=MODEL_NAME,
                        api_key=API_KEY,
                        base_url=API_BASE_URL,
                        temperature=0.7,
                        timeout=300,
                        max_retries=3
                    )
                    
                    # 定义工具列表
                    tools = [analyze_requirements, market_analysis, target_users, market_insights]
                    
                    # 使用 LangGraph 的 create_react_agent
                    self.react_agent = create_react_agent(langchain_llm, tools)
                    logger.info("✓ LangGraph ReAct Agent created successfully")
                    
                except PermissionError as e:
                    logger.warning(f"SSL permission error when creating ReAct Agent: {e}")
                    logger.warning("⚠️  This may be due to macOS security restrictions")
                    logger.warning("⚠️  Using fallback mode instead")
                    self.react_agent = None
                except Exception as e:
                    logger.warning(f"Failed to create LangGraph ReAct Agent: {e}")
                    self.react_agent = None
            else:
                logger.info("LangGraph ReAct Agent not available (LangChain OpenAI not available), using fallback mode")
        else:
            logger.info("LangGraph ReAct Agent not available (LangGraph prebuilt not available), using fallback mode")
    
    @log_function_call
    def research(self, user_input: str) -> Dict[str, Any]:
        """
        执行需求调研 | Conduct requirement research
        
        Args:
            user_input: 用户输入的产品需求 | User input product requirements
            
        Returns:
            包含调研结果的字典 | Dictionary containing research results
        """
        logger.info(f"ProductResearcher.research() called - Input length: {len(user_input)}")
        
        # 尝试使用 LangGraph ReAct Agent
        if self.react_agent is not None:
            try:
                logger.info("Using LangGraph ReAct Agent...")
                
                # 构建任务描述
                task = f"""
You are an experienced product researcher. The user has provided the following product requirements:

{user_input}

Please conduct comprehensive research:
1. Use the analyze_requirements tool to analyze core requirements
2. Use the market_analysis tool to conduct market analysis
3. Use the target_users tool to identify target users
4. Use the market_insights tool to extract insights

After gathering information, synthesize the results into a comprehensive research report.

Return the final results in JSON format with these fields (all in English):
- core_requirements: Core requirement analysis
- market_analysis: Market analysis
- target_users: Target users description  
- market_insights: Market insights

IMPORTANT: All text content must be in English only.
"""
                
                # 调用 LangGraph ReAct Agent
                result = self.react_agent.invoke({"messages": [("user", task)]})
                
                # 提取最终消息
                final_message = result["messages"][-1].content if result.get("messages") else ""
                logger.info(f"ReAct Agent output length: {len(final_message)}")
                logger.debug(f"ReAct Agent final_message preview: {final_message[:1000]}")
                
                # 解析 JSON 响应
                research_result = parse_json_response(final_message, [
                    "core_requirements", "market_analysis", "target_users", "market_insights"
                ])
                
                logger.debug(f"Parsed research_result keys: {list(research_result.keys())}")
                
                # 验证解析结果 - 如果解析失败，使用LLM重新格式化为JSON
                parsed_keys = list(research_result.keys())
                required_keys = ["core_requirements", "market_analysis", "target_users", "market_insights"]
                
                # 检查是否解析成功（至少要有2个以上的字段，或者所有必需字段都存在）
                if len(parsed_keys) < 2 or not all(key in parsed_keys for key in required_keys):
                    logger.warning("JSON parsing failed or incomplete, using LLM to reformat response...")
                    # 使用LLM将文本响应转换为JSON格式
                    reformat_prompt = f"""
The following is a research report that needs to be converted to JSON format:

{final_message}

Please extract and format the information into a JSON object with these exact fields:
- core_requirements: Core requirement analysis
- market_analysis: Market analysis  
- target_users: Target users description
- market_insights: Market insights

If any information is missing, provide a reasonable analysis based on the context.

Return ONLY valid JSON, no other text:
"""
                    try:
                        reformatted_response = self.simple_llm.invoke(reformat_prompt)
                        logger.debug(f"Reformatted response length: {len(reformatted_response)}")
                        research_result = parse_json_response(reformatted_response, required_keys)
                        logger.info(f"Reformatting succeeded, got {len(research_result)} keys")
                    except Exception as e:
                        logger.error(f"Reformatting failed: {e}")
                
                # 确保所有必需的字段都存在
                for key in required_keys:
                    if key not in research_result:
                        logger.warning(f"Missing key in research_result: {key}")
                        # 尝试从原始消息中提取
                        import re
                        # 尝试找到该字段的内容（支持多种格式）
                        key_variant = key.replace("_", " ")
                        pattern1 = re.escape(key) + r'["\']?\s*[:：]\s*["\']?([^"\'}}]+(?:\n[^"\'}}]+)*)'
                        pattern2 = re.escape(key_variant) + r'["\']?\s*[:：]\s*["\']?([^"\'}}]+(?:\n[^"\'}}]+)*)'
                        match = re.search(pattern1, final_message, re.IGNORECASE | re.MULTILINE) or \
                                re.search(pattern2, final_message, re.IGNORECASE | re.MULTILINE)
                        if match:
                            extracted = match.group(1).strip().strip('"\'')
                            if extracted and len(extracted) > 10:
                                research_result[key] = extracted
                                logger.info(f"Extracted {key} from original message")
                            else:
                                research_result[key] = "Not available"
                        else:
                            research_result[key] = "Not available"
                
                logger.info(f"✓ ProductResearcher.research() completed with ReAct Agent")
                logger.debug(f"Final research_result keys: {list(research_result.keys())}")
                
                return {
                    "agent": self.name,
                    "research_result": research_result,
                    "status": "completed",
                    "agent_type": "langgraph_react"
                }
                
            except Exception as e:
                logger.warning(f"LangGraph ReAct Agent failed, using fallback: {e}")
        
        # Fallback: 直接使用 LLM
        logger.info("Using fallback LLM mode...")
        return self._fallback_research(user_input)
    
    def _fallback_research(self, user_input: str) -> Dict[str, Any]:
        """
        回退模式：直接使用 LLM | Fallback mode: Direct LLM call
        """
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
        
        response = self.simple_llm.invoke(prompt)
        logger.debug(f"LLM response length: {len(response)}")
        logger.debug(f"LLM response preview: {response[:500]}")
        
        research_result = parse_json_response(response, [
            "core_requirements", "market_analysis", "target_users", "market_insights"
        ])
        
        logger.debug(f"Parsed research_result keys: {list(research_result.keys())}")
        
        # 验证解析结果 - 如果解析失败或不完整，使用LLM重新格式化
        parsed_keys = list(research_result.keys())
        required_keys = ["core_requirements", "market_analysis", "target_users", "market_insights"]
        
        if len(parsed_keys) < 2 or not all(key in parsed_keys for key in required_keys):
            logger.warning("JSON parsing failed or incomplete, using LLM to reformat response...")
            # 使用LLM将文本响应转换为JSON格式
            reformat_prompt = f"""
The following is a research report that needs to be converted to JSON format:

{response}

Please extract and format the information into a JSON object with these exact fields:
- core_requirements: Core requirement analysis
- market_analysis: Market analysis  
- target_users: Target users description
- market_insights: Market insights

If any information is missing, provide a reasonable analysis based on the context.

Return ONLY valid JSON, no other text:
"""
            try:
                reformatted_response = self.simple_llm.invoke(reformat_prompt)
                logger.debug(f"Reformatted response length: {len(reformatted_response)}")
                research_result = parse_json_response(reformatted_response, required_keys)
                logger.info(f"Reformatting succeeded, got {len(research_result)} keys")
            except Exception as e:
                logger.error(f"Reformatting failed: {e}")
        
        # 确保所有必需的字段都存在
        for key in required_keys:
            if key not in research_result:
                logger.warning(f"Missing key in research_result: {key}")
                # 尝试从原始响应中提取（支持多种格式）
                import re
                key_variant = key.replace("_", " ")
                pattern1 = re.escape(key) + r'["\']?\s*[:：]\s*["\']?([^"\'}}]+(?:\n[^"\'}}]+)*)'
                pattern2 = re.escape(key_variant) + r'["\']?\s*[:：]\s*["\']?([^"\'}}]+(?:\n[^"\'}}]+)*)'
                match = re.search(pattern1, response, re.IGNORECASE | re.MULTILINE) or \
                        re.search(pattern2, response, re.IGNORECASE | re.MULTILINE)
                if match:
                    extracted = match.group(1).strip().strip('"\'')
                    if extracted and len(extracted) > 10:
                        research_result[key] = extracted
                        logger.info(f"Extracted {key} from original response")
                    else:
                        research_result[key] = "Not available"
                else:
                    research_result[key] = "Not available"
        
        logger.info(f"✓ ProductResearcher.research() completed with fallback")
        logger.debug(f"Final research_result keys: {list(research_result.keys())}")
        
        return {
            "agent": self.name,
            "research_result": research_result,
            "status": "completed",
            "agent_type": "fallback"
        }


# ============================================================================
# DocAssistant
# ============================================================================

class DocAssistant:
    """
    产品文档助手智能体 | Doc Assistant Agent
    负责产品需求文档的生成
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "Doc Assistant"
    
    @log_function_call
    def generate_doc(self, user_input: str, research_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成产品需求文档 | Generate product requirement document
        """
        logger.info(f"DocAssistant.generate_doc() called")
        
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
"""
        
        doc_content = self.llm.invoke(prompt)
        logger.info(f"✓ DocAssistant.generate_doc() completed - Document length: {len(doc_content)}")
        
        return {
            "agent": self.name,
            "document": doc_content,
            "status": "completed"
        }


# ============================================================================
# FeasibilityEvaluator
# ============================================================================

class FeasibilityEvaluator:
    """
    可行性评估专家智能体 | Feasibility Evaluator Agent
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "Feasibility Evaluator"
    
    @log_function_call
    def evaluate(self, user_input: str, research_result: Dict[str, Any], doc_content: str = "") -> Dict[str, Any]:
        """
        执行可行性评估 | Conduct feasibility assessment
        基于用户需求和研究结果进行评估（文档内容可选）
        """
        logger.info(f"FeasibilityEvaluator.evaluate() called")
        
        # 构建评估prompt（基于研究结果）
        prompt = f"""
You are a senior technical architect and project evaluation expert. Based on the following information, conduct a comprehensive feasibility assessment:

User Requirement:
{user_input}

Research Results:
{json.dumps(research_result, ensure_ascii=False)}

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
        
        response = self.llm.invoke(prompt)
        
        evaluation_result = parse_json_response(response, [
            "technical_feasibility", "architecture_design", "cost_estimation",
            "compliance_requirements", "risks_and_recommendations"
        ])
        logger.info(f"✓ FeasibilityEvaluator.evaluate() completed")
        
        return {
            "agent": self.name,
            "evaluation_result": evaluation_result,
            "status": "completed"
        }
