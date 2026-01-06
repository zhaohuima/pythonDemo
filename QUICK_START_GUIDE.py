"""
快速开始指南 | Quick Start Guide
用于快速了解和使用 Product Master 系统
Helps quickly understand and use the Product Master system
"""

# ============================================================================
# 第一步：项目设置 | Step 1: Project Setup
# ============================================================================
STEP_1_SETUP = """
【第一步】项目设置 | Step 1: Project Setup
================================================

1. 进入项目目录 | Enter project directory:
   cd /workspaces/pythonDemo

2. 查看项目结构 | View project structure:
   ls -la
   
   输出应该包含以下文件：
   Output should contain:
   - config.py              (配置文件 | Configuration)
   - agents.py              (Agent 定义 | Agent definitions)
   - orchestrator.py        (编排器 | Orchestrator)
   - langgraph_orchestrator.py  (LangGraph 编排器)
   - main.py                (基础演示 | Basic demo)
   - langgraph_demo.py      (LangGraph 演示 | LangGraph demo)
   - requirements.txt       (依赖 | Dependencies)
   - README.md              (文档 | Documentation)

3. 安装依赖 | Install dependencies:
   pip install -r requirements.txt
   
   这将安装：
   This will install:
   - langgraph：用于状态图管理 | For state graph management
   - langchain：用于 LLM 集成 | For LLM integration
   - python-dotenv：用于环境变量 | For environment variables
   - openai：用于 API 调用 | For API calls
"""

# ============================================================================
# 第二步：配置 API | Step 2: Configure API
# ============================================================================
STEP_2_CONFIGURE = """
【第二步】配置 API | Step 2: Configure API
================================================

打开 config.py 文件并确认以下配置：
Open config.py and confirm the following configuration:

API_KEY = "***REMOVED***"
# 硅基流动 API Key | SiliconFlow API Key
# 已设置为提供的 API Key
# Already set to the provided API key

API_BASE_URL = "https://api.siliconflow.cn/v1"
# API 端点 | API Endpoint
# 指向硅基流动的官方 API | Points to SiliconFlow official API

MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
# LLM 模型 | LLM Model
# 使用阿里通义千问 72B 指令模型
# Uses Alibaba Qwen2.5 72B Instruct model

✅ 所有配置已完成 | All configurations are complete
"""

# ============================================================================
# 第三步：了解架构 | Step 3: Understand Architecture
# ============================================================================
STEP_3_UNDERSTAND = """
【第三步】了解架构 | Step 3: Understand Architecture
================================================

系统由以下主要部分组成：
The system consists of the following main components:

1️⃣ 三个专业 Agent | Three Professional Agents:

   📚 Product Researcher (产品研究员)
   职责：
   - 分析用户需求 | Analyze user requirements
   - 进行市场研究 | Conduct market research
   - 竞品分析 | Competitive analysis
   - 用户洞察 | User insights
   
   📝 Doc Assistant (文档助手)
   职责：
   - 生成产品需求文档 (PRD) | Generate PRD
   - 规格说明 | Specifications
   - 用户故事 | User stories
   - 需求定义 | Requirements definition
   
   🔍 Feasibility Evaluator (可行性评估员)
   职责：
   - 技术可行性评估 | Technical feasibility
   - 架构设计 | Architecture design
   - 成本评估 | Cost estimation
   - 合规性评估 | Compliance assessment

2️⃣ 编排器 | Orchestrator:

   🎯 Product Master (产品主人)
   职责：
   - 协调三个 Agent | Coordinate three agents
   - 管理执行流程 | Manage execution flow
   - 汇总结果 | Aggregate results
   - 输出最终建议 | Output final recommendations

3️⃣ 执行模式 | Execution Modes:

   模式 A：基础模式 | Mode A: Basic
   - 使用 ProductMaster 编排器
   - 适合快速执行
   - 文件：main.py
   
   模式 B：LangGraph 模式 | Mode B: LangGraph
   - 使用状态图管理工作流
   - 提供可视化和详细日志
   - 文件：langgraph_demo.py
"""

# ============================================================================
# 第四步：运行基础版本 | Step 4: Run Basic Version
# ============================================================================
STEP_4_RUN_BASIC = """
【第四步】运行基础版本 | Step 4: Run Basic Version
================================================

命令 | Command:
python main.py

预期输出 | Expected Output:
=====================================
1. 系统启动信息 | System startup information
2. Product Researcher 执行研究 | Researcher conducts research
3. Doc Assistant 生成文档 | Assistant generates document
4. Feasibility Evaluator 进行评估 | Evaluator conducts assessment
5. Product Master 汇总结果 | Master aggregates results
6. 执行图表 | Execution graphs
7. 最终汇总 | Final summary

输出文件 | Output Files:
- outputs/orchestration_result.json (完整的执行结果 | Full execution results)

执行时间 | Execution Time:
预计 3-5 分钟（取决于 API 响应速度）
Estimated 3-5 minutes (depends on API response speed)

查看结果 | View Results:
cat outputs/orchestration_result.json
# 或使用 JSON 查看器 | Or use a JSON viewer
"""

# ============================================================================
# 第五步：运行 LangGraph 版本 | Step 5: Run LangGraph Version
# ============================================================================
STEP_5_RUN_LANGGRAPH = """
【第五步】运行 LangGraph 版本 | Step 5: Run LangGraph Version
================================================

命令 | Command:
python langgraph_demo.py

特点 | Features:
=====================================
1. 详细的工作流图 | Detailed workflow graph
   ┌──────────────────────┐
   │   START              │
   └──────────────────────┘
         ▼
   ┌──────────────────────┐
   │  Researcher Node     │
   └──────────────────────┘
         ▼
   ┌──────────────────────┐
   │  Doc Assistant Node  │
   └──────────────────────┘
         ▼
   ┌──────────────────────┐
   │  Evaluator Node      │
   └──────────────────────┘
         ▼
   ┌──────────────────────┐
   │  Aggregation Node    │
   └──────────────────────┘
         ▼
   ┌──────────────────────┐
   │   END                │
   └──────────────────────┘

2. 清晰的执行日志 | Clear execution logs
3. 状态转移跟踪 | State transition tracking
4. 性能统计 | Performance statistics

输出文件 | Output Files:
- outputs/langgraph_results.json (LangGraph 执行结果)

执行时间 | Execution Time:
预计 3-5 分钟
Estimated 3-5 minutes
"""

# ============================================================================
# 第六步：自定义使用 | Step 6: Custom Usage
# ============================================================================
STEP_6_CUSTOM = """
【第六步】自定义使用 | Step 6: Custom Usage
================================================

修改用户输入 | Modify User Input:

打开 main.py 或 langgraph_demo.py，找到 user_requirement 变量，
修改为您自己的产品需求描述：

Open main.py or langgraph_demo.py, find user_requirement variable,
modify it with your own product requirement description:

# 示例 | Example:
user_requirement = \"\"\"
我想开发一个在线教育平台。
功能包括：
1. 课程管理和发布
2. 学生学习记录追踪
3. 在线评估和反馈
4. 社区互动功能

目标：
- 支持 10,000+ 并发用户
- 提供个性化学习体验
- 成本控制在 100 万以内
...
\"\"\"

然后运行 | Then run:
python main.py
或 | or
python langgraph_demo.py
"""

# ============================================================================
# 第七步：理解输出 | Step 7: Understand Output
# ============================================================================
STEP_7_UNDERSTAND_OUTPUT = """
【第七步】理解输出 | Step 7: Understand Output
================================================

执行图 | Execution Graph:
显示了 Agent 之间的协作流程
Shows the collaboration flow between agents

执行统计 | Execution Statistics:
- 执行时间 | Execution time
- Agent 执行状态 | Agent execution status
- 步骤数 | Number of steps

最终汇总 | Final Summary:
包含以下关键信息 | Contains key information:
- 项目可行性评分 | Project feasibility score (1-10)
- 核心价值主张 | Core value propositions
- 关键成功因素 | Key success factors
- 风险和缓解策略 | Risks and mitigation strategies
- 推荐的后续步骤 | Recommended next steps

JSON 输出结构 | JSON Output Structure:
{
  "timestamp": "执行时间戳 | Execution timestamp",
  "execution_time_seconds": "执行耗时 | Execution time in seconds",
  "user_input": "用户输入 | User input",
  "agents_outputs": {
    "product_researcher": { ... },
    "doc_assistant": { ... },
    "feasibility_evaluator": { ... }
  },
  "final_summary": {
    "feasibility_score": "评分 | Score",
    "value_propositions": [ ... ],
    "success_factors": [ ... ],
    "risks_and_mitigations": [ ... ],
    "next_steps": [ ... ]
  },
  "status": "completed"
}
"""

# ============================================================================
# 第八步：进阶使用 | Step 8: Advanced Usage
# ============================================================================
STEP_8_ADVANCED = """
【第八步】进阶使用 | Step 8: Advanced Usage
================================================

创建自定义 Agent | Create Custom Agent:

from config import API_KEY, API_BASE_URL, MODEL_NAME
from langchain_community.llms import OpenAI

class MyCustomAgent:
    \"\"\"
    我的自定义 Agent | My Custom Agent
    专门用于处理特定的任务 | Specialized for specific tasks
    \"\"\"
    
    def __init__(self, llm):
        # 初始化 LLM | Initialize LLM
        self.llm = llm
        # 设置 Agent 名称 | Set agent name
        self.name = "My Custom Agent"
    
    def process(self, input_data):
        \"\"\"
        处理输入数据 | Process input data
        \"\"\"
        # 构建提示词 | Build prompt
        prompt = f\"处理以下数据：{input_data}\"
        # 调用 LLM | Call LLM
        result = self.llm.predict(prompt)
        # 返回结果 | Return result
        return result

集成自定义 Agent | Integrate Custom Agent:

from orchestrator import ProductMaster
from agents import init_llm

# 初始化 LLM | Initialize LLM
llm = init_llm()

# 创建自定义 Agent | Create custom agent
custom_agent = MyCustomAgent(llm)

# 在编排器中使用 | Use in orchestrator
product_master = ProductMaster()
# 添加自定义 Agent 到编排器
# Add custom agent to orchestrator

修改工作流 | Modify Workflow:

创建新的编排器类，自定义执行顺序和逻辑
Create new orchestrator class with custom execution order and logic

支持条件分支 | Support Conditional Branching:

基于前一个 Agent 的输出，决定执行哪个 Agent
Based on previous agent's output, decide which agent to execute

支持反馈循环 | Support Feedback Loops:

如果不满足质量标准，可以重新执行某个 Agent
Re-execute an agent if quality standards are not met
"""

# ============================================================================
# 常见问题解决 | Troubleshooting
# ============================================================================
TROUBLESHOOTING = """
常见问题解决 | Troubleshooting
================================================

问题 1: 导入错误 | Issue 1: Import Error
错误信息：ModuleNotFoundError: No module named 'langchain'
解决方案 | Solution:
  pip install -r requirements.txt

问题 2: API 连接失败 | Issue 2: API Connection Failed
错误信息：Connection refused, 403 Unauthorized
解决方案 | Solution:
  1. 检查 API Key 是否正确 | Check if API key is correct
  2. 检查网络连接 | Check internet connection
  3. 检查 API 端点是否可访问 | Check if API endpoint is accessible

问题 3: LLM 响应超时 | Issue 3: LLM Response Timeout
错误信息：Request timeout
解决方案 | Solution:
  1. 增加超时时间 | Increase timeout
  2. 简化输入内容 | Simplify input
  3. 检查 API 服务状态 | Check API service status

问题 4: 内存占用过高 | Issue 4: High Memory Usage
解决方案 | Solution:
  1. 减少并发数 | Reduce concurrency
  2. 清理临时文件 | Clean temporary files
  3. 使用流式处理 | Use streaming

问题 5: 输出文件无法保存 | Issue 5: Cannot Save Output Files
错误信息：Permission denied
解决方案 | Solution:
  1. 检查 outputs 目录权限 | Check outputs directory permission
  2. 创建 outputs 目录 | Create outputs directory
     mkdir outputs
     chmod 755 outputs
"""

# ============================================================================
# 下一步建议 | Next Steps
# ============================================================================
NEXT_STEPS = """
下一步建议 | Next Steps
================================================

✅ 基础使用完成后 | After basic usage:

1. 阅读详细文档 | Read detailed documentation:
   - README.md (项目文档 | Project documentation)
   - 各 Python 文件中的注释 | Comments in Python files

2. 探索高级功能 | Explore advanced features:
   - 添加自定义 Agent | Add custom agents
   - 修改工作流逻辑 | Modify workflow logic
   - 集成外部数据源 | Integrate external data sources

3. 性能优化 | Performance optimization:
   - 添加缓存 | Add caching
   - 实现异步处理 | Implement async processing
   - 优化提示词 | Optimize prompts

4. 扩展应用 | Expand applications:
   - 构建 Web 界面 | Build web UI
   - 集成到现有系统 | Integrate with existing systems
   - 部署到生产环境 | Deploy to production

5. 贡献改进 | Contribute improvements:
   - 提供反馈 | Provide feedback
   - 报告问题 | Report issues
   - 提交改进建议 | Submit improvements

📚 推荐阅读顺序 | Recommended Reading Order:

1. README.md (项目概述 | Project overview) - 5 分钟
2. config.py (配置说明 | Configuration) - 2 分钟
3. agents.py (Agent 定义 | Agent definitions) - 10 分钟
4. orchestrator.py (编排逻辑 | Orchestration logic) - 10 分钟
5. langgraph_orchestrator.py (状态管理 | State management) - 10 分钟
6. PROJECT_SUMMARY.py (项目总结 | Project summary) - 10 分钟

总计 | Total: 约 45 分钟 | ~45 minutes
"""

# ============================================================================
# 快速参考卡 | Quick Reference Card
# ============================================================================
QUICK_REFERENCE_CARD = """
快速参考卡 | Quick Reference Card
================================================

命令 | Commands:
  python main.py              # 运行基础版本 | Run basic version
  python langgraph_demo.py    # 运行 LangGraph 版本 | Run LangGraph version
  cat outputs/*.json          # 查看结果 | View results

关键文件 | Key Files:
  config.py                   # API 配置 | API configuration
  agents.py                   # Agent 定义 | Agent definitions
  orchestrator.py             # 基础编排器 | Basic orchestrator
  langgraph_orchestrator.py   # LangGraph 编排器 | LangGraph orchestrator

API 配置 | API Configuration:
  API_KEY = "***REMOVED***"
  API_BASE_URL = "https://api.siliconflow.cn/v1"
  MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"

核心类 | Core Classes:
  ProductMaster               # 基础编排器 | Basic orchestrator
  LangGraphOrchestrator       # LangGraph 编排器 | LangGraph orchestrator
  ProductResearcher           # 产品研究员 | Product researcher
  DocAssistant                # 文档助手 | Document assistant
  FeasibilityEvaluator        # 可行性评估员 | Feasibility evaluator

主要方法 | Main Methods:
  orchestrate(user_input)     # 执行编排 | Execute orchestration
  execute_workflow(user_input)# 执行工作流 | Execute workflow
  visualize_workflow_graph()  # 可视化工作流 | Visualize workflow

输出文件 | Output Files:
  outputs/orchestration_result.json   # 基础版本结果 | Basic version results
  outputs/langgraph_results.json      # LangGraph 版本结果 | LangGraph results
"""

# ============================================================================
# 主函数 | Main Function
# ============================================================================
if __name__ == "__main__":
    """
    打印快速开始指南 | Print quick start guide
    """
    print("\n" + "="*80)
    print("Product Master - 快速开始指南")
    print("Product Master - Quick Start Guide")
    print("="*80 + "\n")
    
    print(STEP_1_SETUP)
    print("\n" + "-"*80 + "\n")
    
    print(STEP_2_CONFIGURE)
    print("\n" + "-"*80 + "\n")
    
    print(STEP_3_UNDERSTAND)
    print("\n" + "-"*80 + "\n")
    
    print(STEP_4_RUN_BASIC)
    print("\n" + "-"*80 + "\n")
    
    print(STEP_5_RUN_LANGGRAPH)
    print("\n" + "-"*80 + "\n")
    
    print(STEP_6_CUSTOM)
    print("\n" + "-"*80 + "\n")
    
    print(STEP_7_UNDERSTAND_OUTPUT)
    print("\n" + "-"*80 + "\n")
    
    print(STEP_8_ADVANCED)
    print("\n" + "-"*80 + "\n")
    
    print(TROUBLESHOOTING)
    print("\n" + "-"*80 + "\n")
    
    print(NEXT_STEPS)
    print("\n" + "-"*80 + "\n")
    
    print(QUICK_REFERENCE_CARD)
    
    print("\n" + "="*80)
    print("✨ 快速开始指南完成 | Quick Start Guide Complete")
    print("="*80 + "\n")
