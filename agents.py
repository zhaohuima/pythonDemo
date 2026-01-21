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

    async def ainvoke(self, prompt: str, max_retries: int = 3) -> str:
        """
        异步调用 LLM 生成响应 | Async call LLM to generate response

        用于并行 Skill 执行 | Used for parallel Skill execution
        """
        import asyncio

        logger.debug(f"LLM ainvoke called - Model: {self.model_name}, Prompt length: {len(prompt)}")
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

        last_error = None
        for attempt in range(max_retries):
            try:
                logger.info(f"LLM async API call attempt {attempt + 1}/{max_retries}")
                async with httpx.AsyncClient(
                    verify=False,
                    timeout=httpx.Timeout(300.0, connect=30.0)
                ) as client:
                    response = await client.post(url, headers=headers, json=data)
                    response.raise_for_status()
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    logger.info(f"✓ LLM async API call successful, response length: {len(content)}")
                    return content
            except httpx.TimeoutException as e:
                last_error = e
                wait_time = 2 * (attempt + 1)
                logger.warning(f"Async API call timeout, retrying in {wait_time}s ({attempt + 1}/{max_retries})...")
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)
                    continue
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                error_text = e.response.text

                try:
                    error_json = e.response.json()
                    error_code = error_json.get("code", "unknown")
                    error_msg = error_json.get("message", error_text)
                    logger.error(f"LLM async API call failed (HTTP {status_code}, Code: {error_code}): {error_msg}")
                except:
                    logger.error(f"LLM async API call failed (HTTP {status_code}): {error_text}")

                if status_code >= 500 or status_code == 429:
                    last_error = e
                    wait_time = 2 * (attempt + 1)
                    logger.warning(f"Server error or rate limit, retrying in {wait_time}s ({attempt + 1}/{max_retries})...")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(wait_time)
                        continue
                else:
                    logger.error(f"Client error (HTTP {status_code}), not retrying")
                    raise Exception(f"LLM async API call failed (HTTP {status_code}): {error_text}")
            except Exception as e:
                last_error = e
                wait_time = 2 * (attempt + 1)
                logger.warning(f"Async API call failed, retrying in {wait_time}s ({attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)
                    continue
                break

        logger.error(f"LLM async call failed after {max_retries} attempts: {str(last_error)}")
        raise Exception(f"LLM async call failed after {max_retries} retries: {str(last_error)}")


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

    支持两种模式 | Supports two modes:
    1. 并行 Skill 模式（推荐）| Parallel Skill mode (recommended)
    2. LangGraph ReAct Agent 模式 | LangGraph ReAct Agent mode
    """

    def __init__(self, llm: SimpleLLM, use_parallel_skills: bool = True):
        """
        初始化产品研究员 | Initialize Product Researcher

        Args:
            llm: 语言模型实例 | Language model instance
            use_parallel_skills: 是否使用并行 Skill 模式 | Whether to use parallel Skill mode
        """
        self.simple_llm = llm
        self.use_parallel_skills = use_parallel_skills
        self.name = "Product Researcher (LangGraph ReAct Agent)"
        self.react_agent = None
        self.parallel_orchestrator = None

        # 初始化并行 Skill 编排器
        if use_parallel_skills:
            try:
                from skills.parallel_orchestrator import ParallelSkillOrchestrator
                self.parallel_orchestrator = ParallelSkillOrchestrator(llm)
                logger.info("✓ Parallel Skill Orchestrator initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Parallel Skill Orchestrator: {e}")
                logger.warning("⚠️  Falling back to LangGraph ReAct Agent mode")
                self.use_parallel_skills = False

        # 创建 LangGraph ReAct Agent（作为 fallback 或主模式）
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

        # 优先使用并行 Skill 模式
        if self.use_parallel_skills and self.parallel_orchestrator is not None:
            try:
                logger.info("Using Parallel Skill mode...")
                import asyncio

                # 运行异步并行研究
                result = asyncio.run(self.parallel_orchestrator.research_with_timeout(user_input, timeout=120.0))
                logger.info("✓ Parallel Skill research completed successfully")
                # 包装成与原有格式一致的结构
                return {"research_result": result}
            except Exception as e:
                logger.warning(f"Parallel Skill mode failed: {e}")
                logger.warning("⚠️  Falling back to LangGraph ReAct Agent mode")

        # 尝试使用 LangGraph ReAct Agent
        if self.react_agent is not None:
            try:
                logger.info("Using LangGraph ReAct Agent...")
                
                # 构建任务描述
                task = f"""
You are an experienced product researcher conducting deep market and user research.

User Requirement:
{user_input}

═══════════════════════════════════════════════════════════════
SCORING CRITERIA (Your response will be evaluated on 4 dimensions, 10 points each):
═══════════════════════════════════════════════════════════════

Dimension A - User Requirements (10 points):
• 10 points: Identifies explicit AND implicit requirements, understands business problem, distinguishes must-have vs nice-to-have, considers strategic context
• 7 points: Identifies most requirements, good understanding, minor gaps in implicit needs
• 4 points: Surface-level needs only, partial understanding, misses implicit requirements
• 1 point: Fails to identify needs, misinterprets problem

Dimension B - Target Users (10 points):
• 10 points: Specific company size (employee count, revenue), detailed personas (job titles), 3+ unmet needs with evidence, pain point severity/frequency
• 7 points: Main segments with detail, 2 unmet needs, some evidence
• 4 points: Generic segment definition, 1 unmet need, vague pain points
• 1 point: Incorrect or no segments, no unmet needs

Dimension C - Market Analysis (10 points):
• 10 points: 5+ competitors with positioning, market share/customer count, pricing models, emerging competitors, market gaps
• 7 points: 3-4 competitors with positioning, some market data, key differentiators
• 4 points: 1-2 competitors with minimal detail, lacks market data
• 1 point: No competitors or completely irrelevant

Dimension D - Market Insights (10 points):
• 10 points: 3+ actionable positioning recommendations with rationale, TAM/SAM with $ estimates, pricing model with reasoning, beachhead market
• 7 points: 2 positioning recommendations, market opportunities with general sizing
• 4 points: 1 vague recommendation, mentions opportunities without sizing
• 1 point: No actionable insights, irrelevant recommendations

═══════════════════════════════════════════════════════════════
CRITICAL REQUIREMENTS FOR HIGH SCORES (10 points):
═══════════════════════════════════════════════════════════════

✓ Use SPECIFIC numbers: "50-500 employees, $5M-$50M revenue" NOT "mid-size companies"
✓ Name 5+ ACTUAL competitors with market data (market share, customer count, pricing)
✓ Provide $ estimates for TAM/SAM (e.g., "$2.8B addressable market with calculation")
✓ Include 3+ unmet needs with SUPPORTING EVIDENCE (percentages, costs, time data)
✓ Cite SPECIFIC pricing models (per-seat $X-Y/month, usage-based, freemium, etc.)
✓ Distinguish EXPLICIT vs IMPLICIT requirements (differentiation, PMF validation, strategic context)
✓ Provide ACTIONABLE strategies with clear rationale, NOT generic advice ("focus on quality")

Use the available tools to conduct comprehensive research across 4 dimensions:

1. analyze_requirements tool:
   - Identify BOTH explicit AND implicit requirements
   - Explicit: What features/capabilities were mentioned?
   - Implicit: Underlying business problem, differentiation opportunities, PMF validation needs
   - Determine must-have vs nice-to-have features
   - Consider strategic context and business constraints

2. target_users tool:
   - Define specific user segments (company size with employee count, revenue range, industry)
   - Create detailed personas (specific job titles, departments, decision authority)
   - Identify 3+ critical unmet needs with evidence
   - Explain pain point severity and frequency
   - Provide evidence (market data, user complaints)

3. market_analysis tool:
   - Research 5+ competitors with detailed positioning
   - Include market share or customer count for each
   - Document pricing models (per-seat, usage-based, etc.)
   - Identify market trends and white space opportunities
   - Note emerging competitors

4. market_insights tool:
   - Provide specific positioning strategies (vertical specialization with sub-segments)
   - Calculate TAM/SAM with $ estimates and data sources
   - Recommend pricing model with clear rationale
   - Suggest beachhead market and GTM approach
   - Include success metrics and benchmarks

After gathering information, synthesize into a comprehensive report.

═══════════════════════════════════════════════════════════════
CRITICAL FORMATTING REQUIREMENTS:
═══════════════════════════════════════════════════════════════

To ensure clear display in the UI, format your JSON field values with proper line breaks:

1. Use \\n\\n to separate major sections (e.g., between "Explicit requirements" and "Implicit requirements")
2. Use \\n- to create bullet points for list items
3. Ensure each distinct concept is on a new line
4. Do NOT combine multiple concepts in a single line without line breaks

Example of well-formatted JSON output:
{{
  "core_requirements": "Explicit requirements:\\n- Login functionality to enable personalized experiences\\n- AI-based coaching for tailored support\\n- Camera integration to scan homework\\n\\nImplicit requirements:\\n- Differentiation opportunity: deep curriculum integration\\n- PMF validation needed: prove scalability without compromising accuracy\\n- Must-have features: curriculum alignment, multi-language support\\n- Nice-to-have: gamification, sentiment analysis\\n\\nStrategic context:\\nRise of remote learning increases need for scalable, personalized tools.",

  "target_users": "Primary User Segment:\\n- Company size: 50-500 employees\\n- Revenue range: $5M-$50M annually\\n- Industry: E-commerce, SaaS\\n\\nUser Personas:\\n- Customer Support Managers (decision makers)\\n- CX Directors (budget owners)\\n- Operations VPs (ROI evaluators)\\n\\nCritical Unmet Needs:\\n- 24/7 multilingual support without proportional cost scaling (evidence: costs $180K/year for human agents vs $60K for AI)\\n- Order-specific context awareness (evidence: 73% of tickets require checking 3+ systems, taking 4-6 minutes)\\n- Seamless human handoff with context transfer (evidence: 34% satisfaction drop when context is lost)"
}}

Return in JSON format with these fields (all in English):
- core_requirements: Explicit + implicit requirements + strategic context + must-have vs nice-to-have (use \\n\\n between sections, \\n- for bullet points)
- target_users: Specific segments (size/revenue) + personas (roles) + 3+ evidence-based unmet needs (use \\n\\n between sections, \\n- for bullet points)
- market_analysis: 5+ competitors with positioning, market share, pricing, and differentiators (use \\n- for each competitor)
- market_insights: Actionable strategies with TAM/SAM estimates, pricing recommendations, and positioning (use \\n\\n between sections, \\n- for bullet points)

CRITICAL: Be specific with numbers, provide evidence, focus on differentiation and actionable insights. Use proper line breaks (\\n) to ensure clear formatting.
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
You are an experienced product researcher conducting deep market and user research.

User Requirement:
{user_input}

═══════════════════════════════════════════════════════════════
SCORING CRITERIA (Your response will be evaluated on 4 dimensions, 10 points each):
═══════════════════════════════════════════════════════════════

Dimension A - User Requirements (10 points):
• 10 points: Identifies explicit AND implicit requirements, understands business problem, distinguishes must-have vs nice-to-have, considers strategic context
• 7 points: Identifies most requirements, good understanding, minor gaps in implicit needs
• 4 points: Surface-level needs only, partial understanding, misses implicit requirements
• 1 point: Fails to identify needs, misinterprets problem

Dimension B - Target Users (10 points):
• 10 points: Specific company size (employee count, revenue), detailed personas (job titles), 3+ unmet needs with evidence, pain point severity/frequency
• 7 points: Main segments with detail, 2 unmet needs, some evidence
• 4 points: Generic segment definition, 1 unmet need, vague pain points
• 1 point: Incorrect or no segments, no unmet needs

Dimension C - Market Analysis (10 points):
• 10 points: 5+ competitors with positioning, market share/customer count, pricing models, emerging competitors, market gaps
• 7 points: 3-4 competitors with positioning, some market data, key differentiators
• 4 points: 1-2 competitors with minimal detail, lacks market data
• 1 point: No competitors or completely irrelevant

Dimension D - Market Insights (10 points):
• 10 points: 3+ actionable positioning recommendations with rationale, TAM/SAM with $ estimates, pricing model with reasoning, beachhead market
• 7 points: 2 positioning recommendations, market opportunities with general sizing
• 4 points: 1 vague recommendation, mentions opportunities without sizing
• 1 point: No actionable insights, irrelevant recommendations

═══════════════════════════════════════════════════════════════
CRITICAL REQUIREMENTS FOR HIGH SCORES (10 points):
═══════════════════════════════════════════════════════════════

✓ Use SPECIFIC numbers: "50-500 employees, $5M-$50M revenue" NOT "mid-size companies"
✓ Name 5+ ACTUAL competitors with market data (market share, customer count, pricing)
✓ Provide $ estimates for TAM/SAM (e.g., "$2.8B addressable market with calculation")
✓ Include 3+ unmet needs with SUPPORTING EVIDENCE (percentages, costs, time data)
✓ Cite SPECIFIC pricing models (per-seat $X-Y/month, usage-based, freemium, etc.)
✓ Distinguish EXPLICIT vs IMPLICIT requirements (differentiation, PMF validation, strategic context)
✓ Provide ACTIONABLE strategies with clear rationale, NOT generic advice ("focus on quality")

═══════════════════════════════════════════════════════════════
FEW-SHOT EXAMPLES (Use as quality guidelines, not templates to copy):
═══════════════════════════════════════════════════════════════

Example of EXCELLENT Response (Would Score 38-40/40):

User Question: "I'm building an AI customer support agent for e-commerce. What are the key user pain points?"

{{
  "core_requirements": "Explicit requirements: Automate tier-1 customer support queries for e-commerce (order status, returns, shipping). Implicit requirements: (1) Differentiation opportunity - most chatbots lack deep integration with inventory/shipping systems; (2) PMF validation needed - must prove 24/7 multilingual support scales without proportional cost increase; (3) Must-have features: order-specific context awareness, seamless human handoff with context transfer. Nice-to-have: sentiment analysis, proactive outreach. Strategic context: E-commerce operates on thin margins (5-10%), so ROI must be clear within 3-6 months.",

  "target_users": "Primary segment: E-commerce companies with 50-500 employees, handling 1,000-10,000 customer inquiries monthly, $5M-$50M annual revenue, primarily fashion, electronics, and food verticals. Personas: (1) Customer Support Managers (decision makers), (2) CX Directors (budget owners), (3) Operations VPs (ROI evaluators). Critical unmet needs with evidence: (1) 24/7 multilingual support without proportional cost scaling - current solutions require separate language models or 3x human agents for 3 languages, costing $180K/year vs $60K for AI solution; (2) Order-specific context awareness integrating real-time with inventory, shipping, payment systems - 73% of support tickets require checking order status across 3+ systems, taking 4-6 minutes per query; (3) Seamless human handoff when queries exceed AI capability with full context transfer - current chatbots lose conversation history, forcing customers to repeat information, causing 34% satisfaction drop.",

  "market_analysis": "1. Zendesk AI - Market leader with 30%+ enterprise share, $49-$99/agent/month, strong in ticketing integration, 100K+ customers, weakness: expensive for SMBs. 2. Intercom Fin - AI agent with $13B valuation, $74-$132/seat/month, focuses on mid-market SaaS, 25K+ customers, weakness: not e-commerce optimized. 3. Ada - Specialized in e-commerce, serves 400+ brands including Shopify merchants, $500-$2000/month based on volume, strength: deep Shopify integration. 4. Gorgias - E-commerce focused, integrated with Shopify/WooCommerce, $29M ARR, $10-$750/month tiered pricing, 13K+ customers, strength: e-commerce native. 5. Kustomer (Meta) - CRM-integrated agent, enterprise positioning, $89-$179/user/month, weakness: complex setup. Market trends: AI customer support growing at 29.5% CAGR, reaching $11.14B in 2026. White space: Mid-market e-commerce (50-500 employees) underserved - too small for Zendesk enterprise, outgrowing basic chatbots.",

  "market_insights": "Positioning strategies: (1) Vertical specialization - Focus exclusively on e-commerce sub-verticals (fashion: size/fit queries; electronics: technical specs; food: dietary restrictions) rather than horizontal customer support. Build domain-specific training data. (2) Integration-first approach - Launch with native Shopify, WooCommerce, BigCommerce integrations on day 1, not as afterthought. This is table stakes for e-commerce buyers. (3) Hybrid pricing model - Offer per-resolution pricing ($0.50-$1.50 per resolved ticket) instead of per-seat ($50-100/month), aligning with e-commerce's thin-margin ROI focus. Market sizing: TAM = $11.14B (global AI customer support market 2026). SAM = $2.8B (mid-market e-commerce segment with 50-500 employees, representing 45,000 companies globally × $62K average deal size). Target beachhead: Shopify Plus merchants (8,000+ stores with $1M+ revenue) as they have budget and integration needs. GTM approach: Partner with Shopify app store for distribution, offer 14-day free trial with guaranteed ROI calculator showing cost savings vs human agents."
}}

Why this scores 38-40/40: ✓ Explicit + implicit requirements ✓ Specific sizes (50-500 employees, $5M-$50M) ✓ 3 unmet needs with quantified evidence ✓ 5 competitors with market share, pricing ✓ TAM/SAM with calculation ✓ Specific positioning strategies

Example of WEAK Response (Would Score 15-20/40) - What NOT to Do:

{{
  "core_requirements": "The user wants to build an AI chatbot for customer support in e-commerce. This will help companies handle customer questions automatically and reduce costs. The main requirement is to automate responses to common questions.",

  "target_users": "The target users are e-commerce companies that need customer support. This includes online retailers and businesses that sell products online. They want to improve customer satisfaction and reduce support costs.",

  "market_analysis": "There are several competitors in this space including Zendesk and Intercom. These are popular customer support platforms. The market is growing as more companies adopt AI technology. There are opportunities for new entrants to compete on features and pricing.",

  "market_insights": "To succeed in this market, focus on providing good customer service and competitive pricing. Build a user-friendly interface and integrate with popular e-commerce platforms. Consider offering a free trial to attract customers. The market opportunity is significant as e-commerce continues to grow."
}}

Why this scores only 15-20/40: ✗ No implicit requirements ✗ Generic "e-commerce companies" ✗ No specific unmet needs or evidence ✗ Only 2 competitors, no market data ✗ No TAM/SAM estimates ✗ Vague recommendations

═══════════════════════════════════════════════════════════════

Now conduct comprehensive research across 4 dimensions:

═══════════════════════════════════════════════════════════════
1. CORE REQUIREMENTS ANALYSIS
═══════════════════════════════════════════════════════════════

Analyze BOTH explicit and implicit requirements:

A. Explicit Requirements:
   - What specific features/capabilities did the user mention?
   - What problem are they trying to solve?

B. Implicit Requirements (CRITICAL - don't skip):
   - What is the underlying business problem?
   - What differentiation opportunities exist in this market?
   - What product-market fit validation is needed before building?
   - What are the must-have vs nice-to-have features?
   - What technical or business constraints should be considered?

C. Strategic Context:
   - Why is this product needed NOW?
   - What would make this 10x better than alternatives?
   - What are the key success criteria?

═══════════════════════════════════════════════════════════════
2. TARGET USERS ANALYSIS
═══════════════════════════════════════════════════════════════

Define target users with SPECIFIC details:

A. Primary User Segment:
   - Company size (employee count range, e.g., 50-500 employees)
   - Revenue range or funding stage (e.g., $5M-$50M ARR)
   - Industry/vertical (be specific)
   - Geographic focus

B. User Personas:
   - Specific roles (job titles, e.g., "VP of Sales", "Customer Support Manager")
   - Department/function
   - Decision-making authority

C. Critical Unmet Needs (provide 3+ with evidence):
   - What specific pain points exist that current solutions don't address?
   - Why are existing solutions inadequate? (cite specific limitations)
   - How severe/frequent are these pain points?
   - What evidence supports these unmet needs? (market data, user complaints, etc.)

═══════════════════════════════════════════════════════════════
3. MARKET ANALYSIS
═══════════════════════════════════════════════════════════════

Identify 5+ competitors with detailed information:

For each competitor provide:
- Company name
- Market positioning (enterprise/mid-market/SMB)
- Market share or customer count (if available, e.g., "30% market share" or "10,000+ customers")
- Key strengths and differentiators
- Pricing model (per-seat, usage-based, freemium, etc.)
- Notable customers or use cases

Also include:
- Market trends and growth drivers
- Emerging competitors or threats
- Market gaps and white space opportunities

═══════════════════════════════════════════════════════════════
4. MARKET INSIGHTS & STRATEGY
═══════════════════════════════════════════════════════════════

Provide ACTIONABLE insights (not generic advice):

A. Positioning Strategies (be specific):
   - Vertical specialization: Which specific sub-segments to target? (e.g., "Focus on e-commerce fashion brands" not just "e-commerce")
   - Differentiation approach: What unique value proposition? (be specific about HOW it's different)
   - Competitive positioning: How to stand out from competitors? (specific strategies)

B. Market Sizing (include numbers):
   - TAM (Total Addressable Market): Provide estimate with $ amount (e.g., "$5.4B")
   - SAM (Serviceable Addressable Market): Provide estimate (e.g., "$2.8B")
   - Target segment: Number of companies with specific characteristics (e.g., "15,000 companies with 50-500 employees")
   - Cite data sources when possible or indicate if estimated

C. Go-to-Market Recommendations:
   - Pricing model: (per-seat/usage-based/freemium/hybrid) with clear rationale for why
   - Distribution channels: (direct sales/self-serve/partnerships) with reasoning
   - Beachhead market: Which specific segment to target first and why?

D. Success Metrics:
   - Key metrics to track (be specific)
   - Industry benchmarks (provide numbers if available)

═══════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════
CRITICAL FORMATTING REQUIREMENTS:
═══════════════════════════════════════════════════════════════

To ensure clear display in the UI, format your JSON field values with proper line breaks:

1. Use \\n\\n to separate major sections (e.g., between "Explicit requirements" and "Implicit requirements")
2. Use \\n- to create bullet points for list items
3. Ensure each distinct concept is on a new line
4. Do NOT combine multiple concepts in a single line without line breaks

Example of well-formatted JSON output:
{{
  "core_requirements": "Explicit requirements:\\n- Login functionality to enable personalized experiences\\n- AI-based coaching for tailored support\\n- Camera integration to scan homework\\n\\nImplicit requirements:\\n- Differentiation opportunity: deep curriculum integration\\n- PMF validation needed: prove scalability without compromising accuracy\\n- Must-have features: curriculum alignment, multi-language support\\n- Nice-to-have: gamification, sentiment analysis\\n\\nStrategic context:\\nRise of remote learning increases need for scalable, personalized tools.",

  "target_users": "Primary User Segment:\\n- Company size: 50-500 employees\\n- Revenue range: $5M-$50M annually\\n- Industry: E-commerce, SaaS\\n\\nUser Personas:\\n- Customer Support Managers (decision makers)\\n- CX Directors (budget owners)\\n- Operations VPs (ROI evaluators)\\n\\nCritical Unmet Needs:\\n- 24/7 multilingual support without proportional cost scaling (evidence: costs $180K/year for human agents vs $60K for AI)\\n- Order-specific context awareness (evidence: 73% of tickets require checking 3+ systems, taking 4-6 minutes)\\n- Seamless human handoff with context transfer (evidence: 34% satisfaction drop when context is lost)"
}}

═══════════════════════════════════════════════════════════════

Return results in JSON format with these exact fields (all in English):
{{
  "core_requirements": "Detailed analysis covering explicit requirements, implicit needs (differentiation, PMF validation), and strategic context (use \\n\\n between sections, \\n- for bullet points)",
  "target_users": "Specific user segments with company size/revenue ranges, detailed personas with roles, and 3+ evidence-based unmet needs with severity/frequency (use \\n\\n between sections, \\n- for bullet points)",
  "market_analysis": "5+ competitors with positioning, market share/customer count, pricing, and detailed differentiators. Include market trends and gaps. (use \\n- for each competitor)",
  "market_insights": "Actionable positioning strategies with specific vertical focus, TAM/SAM estimates with numbers, pricing model recommendations with rationale, and beachhead market suggestion (use \\n\\n between sections, \\n- for bullet points)"
}}

CRITICAL REQUIREMENTS:
- All content must be in English
- Be specific with numbers, company sizes, revenue ranges, and market data
- Provide actionable insights with clear rationale, not generic advice
- Include evidence and data sources when possible
- Focus on differentiation and strategic positioning
- Distinguish between must-have and nice-to-have features
- Identify implicit needs, not just explicit ones
- Use proper line breaks (\\n) to ensure clear formatting in the UI
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

def extract_used_citation_ids(text: str) -> set:
    """
    从文本中提取实际使用的引用编号 | Extract actually used citation IDs from text

    Args:
        text: LLM 生成的文本响应 | LLM generated text response

    Returns:
        实际使用的引用编号集合 | Set of actually used citation IDs
    """
    import re
    # 匹配 [1], [2], [3] 等格式的引用
    pattern = r'\[(\d+)\]'
    matches = re.findall(pattern, text)
    return set(int(m) for m in matches)


def filter_citations_by_usage(citations: List[Dict], used_ids: set) -> List[Dict]:
    """
    过滤引用列表，只保留实际使用的引用 | Filter citations to keep only actually used ones

    Args:
        citations: 原始引用列表 | Original citations list
        used_ids: 实际使用的引用编号集合 | Set of actually used citation IDs

    Returns:
        过滤后的引用列表 | Filtered citations list
    """
    if not used_ids:
        return []
    return [cite for cite in citations if cite.get('id') in used_ids]


class FeasibilityEvaluator:
    """
    可行性评估专家智能体 | Feasibility Evaluator Agent
    支持 RAG 检索增强，从知识库中获取相关参考资料
    Supports RAG retrieval augmentation to get relevant references from knowledge base
    """

    def __init__(self, llm, rag_retriever=None):
        """
        初始化可行性评估器 | Initialize Feasibility Evaluator

        Args:
            llm: 语言模型实例 | Language model instance
            rag_retriever: RAG检索器实例（可选）| RAG retriever instance (optional)
        """
        self.llm = llm
        self.name = "Feasibility Evaluator"
        self.rag_retriever = rag_retriever

        if self.rag_retriever:
            logger.info("✓ FeasibilityEvaluator initialized with RAG support")
        else:
            logger.info("FeasibilityEvaluator initialized without RAG support")

    @log_function_call
    def evaluate(self, user_input: str, research_result: Dict[str, Any], doc_content: str = "") -> Dict[str, Any]:
        """
        执行可行性评估 | Conduct feasibility assessment
        基于用户需求和研究结果进行评估（文档内容可选）
        如果启用了RAG，会从知识库中检索相关参考资料
        """
        logger.info(f"FeasibilityEvaluator.evaluate() called")

        # RAG: 检索相关文档
        rag_context = ""
        citations = []

        if self.rag_retriever:
            try:
                # 构建检索查询
                query = f"{user_input} technical feasibility cost architecture risk compliance"
                logger.info(f"RAG: Retrieving relevant documents for query...")

                # 检查vector store状态
                rag_status = self.rag_retriever.get_status()
                logger.info(f"RAG: Vector store has {rag_status['chunks_in_vector_store']} chunks")

                # 检索相关文档
                from config import RAG_TOP_K
                logger.info(f"RAG: Querying with top_k={RAG_TOP_K}")
                retrieved_docs = self.rag_retriever.retrieve(query, top_k=RAG_TOP_K)

                if retrieved_docs:
                    rag_context, citations = self.rag_retriever.format_context_with_citations(retrieved_docs)
                    logger.info(f"RAG: Retrieved {len(retrieved_docs)} relevant documents with {len(citations)} citations")
                    # 记录引用的文档名
                    for cite in citations:
                        logger.info(f"RAG: Citation [{cite['id']}] - {cite['document']}, Page {cite['page']}, Score: {cite['relevance_score']}")
                else:
                    logger.warning(f"RAG: No relevant documents found (vector store has {rag_status['chunks_in_vector_store']} chunks)")
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")
                rag_context = ""
                citations = []

        # 构建评估prompt（基于研究结果，可选包含RAG上下文）
        rag_section = ""
        if rag_context:
            rag_section = f"""
Reference Documents from Knowledge Base:
{rag_context}

IMPORTANT: When using information from the reference documents above, include citations in your response using the format [1], [2], etc. to indicate which reference document the information comes from.
"""

        prompt = f"""
You are a senior technical architect and project evaluation expert. Based on the following information, conduct a comprehensive feasibility assessment:

User Requirement:
{user_input}

Research Results:
{json.dumps(research_result, ensure_ascii=False)}
{rag_section}
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

IMPORTANT:
- All text content in the JSON response must be in English only.
- If you referenced any information from the knowledge base documents, include the citation numbers [1], [2], etc. in your response text.
"""

        response = self.llm.invoke(prompt)

        evaluation_result = parse_json_response(response, [
            "technical_feasibility", "architecture_design", "cost_estimation",
            "compliance_requirements", "risks_and_recommendations"
        ])

        # 过滤引用：只保留 LLM 实际在响应中使用的引用
        # Filter citations: only keep citations actually used by LLM in the response
        if citations:
            # 从 LLM 响应中提取实际使用的引用编号
            used_citation_ids = extract_used_citation_ids(response)
            logger.info(f"RAG: LLM used citation IDs: {sorted(used_citation_ids)}")

            # 过滤引用列表
            filtered_citations = filter_citations_by_usage(citations, used_citation_ids)
            logger.info(f"RAG: Filtered citations from {len(citations)} to {len(filtered_citations)}")

            evaluation_result["citations"] = filtered_citations
            logger.info(f"✓ FeasibilityEvaluator.evaluate() completed with {len(filtered_citations)} citations (filtered from {len(citations)})")
        else:
            evaluation_result["citations"] = []
            logger.info(f"✓ FeasibilityEvaluator.evaluate() completed without citations")

        return {
            "agent": self.name,
            "evaluation_result": evaluation_result,
            "status": "completed",
            "rag_enabled": self.rag_retriever is not None,
            "citations_count": len(evaluation_result["citations"])
        }
