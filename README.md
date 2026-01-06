# Product Master - 多智能体编排系统

**Multi-Agent Orchestration System for Digital Product Managers**

## 📋 项目简介 | Project Overview

这是一个基于 Python 和 LangGraph 构建的多智能体编排系统，专门为数字化项目的产品经理设计。系统通过协调三个专业 AI Agent，帮助产品经理快速、全面地评估和规划新产品。

This is a multi-agent orchestration system built with Python and LangGraph, specifically designed for product managers of digital projects. The system helps product managers quickly and comprehensively evaluate and plan new products by coordinating three professional AI agents.

## 🏗️ 系统架构 | System Architecture

### 核心组件 | Core Components

```
┌─────────────────────────────────────────────────────────────┐
│              🎯 Product Master (Orchestrator)               │
│              产品主人 (编排器)                               │
└─────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
      ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
      │ Product          │ │ Doc              │ │ Feasibility      │
      │ Researcher       │ │ Assistant        │ │ Evaluator        │
      │                  │ │                  │ │                  │
      │ • Market Research│ │ • PRD Generation │ │ • Tech Feasibili │
      │ • User Analysis  │ │ • Spec Design    │ │ • Architecture   │
      │ • Competitive    │ │ • Requirements   │ │ • Cost Estimate  │
      │   Analysis       │ │   Documentation  │ │ • Compliance     │
      └──────────────────┘ └──────────────────┘ └──────────────────┘
```

### Agent 职责 | Agent Responsibilities

#### 1. **Product Researcher** (产品研究员)
- 分析用户的核心需求 | Analyze core user requirements
- 进行市场竞品分析 | Conduct competitive analysis
- 识别目标用户群体 | Identify target user groups
- 提供市场洞察 | Provide market insights

#### 2. **Doc Assistant** (文档助手)
- 生成专业的产品需求文档 (PRD) | Generate professional Product Requirement Document (PRD)
- 设计产品规格说明 | Design product specifications
- 撰写用户故事 | Write user stories
- 文档格式规范化 | Standardize document format

#### 3. **Feasibility Evaluator** (可行性评估员)
- **技术可行性评估** | Technical Feasibility Assessment
  - 技术栈需求 | Technology stack requirements
  - 技术风险分析 | Technical risk analysis
  - 技术复杂度评估 | Technical complexity assessment

- **架构设计** | Architecture Design
  - 推荐系统架构 | Recommended system architecture
  - 主要模块设计 | Key module design
  - 可扩展性考虑 | Scalability considerations

- **成本评估** | Cost Assessment
  - 开发成本预估 | Development cost estimation
  - 基础设施成本 | Infrastructure cost
  - 维护成本 | Maintenance cost

- **合规性评估** | Compliance Assessment
  - 数据隐私合规 | Data privacy compliance
  - 安全性要求 | Security requirements
  - 行业标准遵循 | Industry standard compliance

#### 4. **Product Master** (产品主人 - 编排器)
- 接收用户需求输入 | Receive user requirement input
- 协调三个 Agent 的执行 | Coordinate execution of three agents
- 汇总所有结果 | Aggregate all results
- 提炼关键要点并输出最终建议 | Extract key points and output final recommendations

## 📁 项目文件结构 | Project File Structure

```
pythonDemo/
├── config.py                    # 配置文件 | Configuration file
├── agents.py                    # Agent 定义和实现 | Agent definitions and implementations
├── orchestrator.py              # Product Master 编排器 | Product Master Orchestrator
├── langgraph_orchestrator.py    # LangGraph 版本编排器 | LangGraph version orchestrator
├── main.py                      # 主程序 | Main program
├── langgraph_demo.py            # LangGraph 演示 | LangGraph demo
├── requirements.txt             # 依赖管理 | Dependency management
├── README.md                    # 项目文档 | Project documentation
└── outputs/                     # 输出结果目录 | Output results directory
    ├── orchestration_result.json
    └── langgraph_results.json
```

## 🚀 快速开始 | Quick Start

### 环境准备 | Environment Setup

```bash
# 1. 克隆或创建项目目录 | Clone or create project directory
cd pythonDemo

# 2. 创建虚拟环境 | Create virtual environment
python -m venv venv

# 3. 激活虚拟环境 | Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. 安装依赖 | Install dependencies
pip install -r requirements.txt
```

### 运行示例 | Run Examples

#### 方式 1: 运行基础版本 | Method 1: Run Basic Version

```bash
python main.py
```

这将运行 Product Master 编排器的基础版本，输出包括：
This will run the basic version of Product Master orchestrator with output including:
- 各 Agent 的执行结果 | Execution results from each agent
- 执行图表 | Execution graphs
- 最终汇总 | Final summary
- 保存结果到 `outputs/orchestration_result.json`

#### 方式 2: 运行 LangGraph 版本 | Method 2: Run LangGraph Version

```bash
python langgraph_demo.py
```

这将展示基于 LangGraph 的状态图实现：
This will demonstrate the LangGraph state graph implementation:
- 可视化的工作流图 | Visualized workflow graph
- 清晰的状态转移 | Clear state transitions
- 完整的执行日志 | Complete execution log
- 保存结果到 `outputs/langgraph_results.json`

## 📊 执行流程 | Execution Flow

### 标准工作流 | Standard Workflow

```
用户输入 | User Input
    │
    ▼
┌──────────────────────┐
│ Product Researcher   │  (1-2 分钟 | 1-2 minutes)
│ 需求调研和市场分析   │
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│ Doc Assistant        │  (1-2 分钟 | 1-2 minutes)
│ 生成产品文档         │
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│ Feasibility          │  (1-2 分钟 | 1-2 minutes)
│ Evaluator            │
│ 可行性评估           │
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│ Product Master       │  (1 分钟 | 1 minute)
│ 汇总和优化输出       │
└──────────────────────┘
    │
    ▼
最终输出 | Final Output
(完整的产品战略文档 | Complete Product Strategy Document)
```

## 💡 使用示例 | Usage Examples

### 示例 1: 电商供应链系统 | Example 1: E-commerce Supply Chain System

```python
from orchestrator import ProductMaster

# 创建编排器 | Create orchestrator
product_master = ProductMaster()

# 用户需求输入 | User requirement input
user_requirement = """
我们想要开发一个针对电商企业的供应链管理系统。
功能需求包括：
1. 实时库存追踪
2. 供应商协作平台
3. 订单预测和优化
4. 成本分析报告
...
"""

# 执行编排流程 | Execute orchestration
result = product_master.orchestrate(user_requirement)

# 打印结果 | Print results
product_master.print_execution_summary(result)
```

### 示例 2: 客户服务 AI 平台 | Example 2: Customer Service AI Platform

```python
from langgraph_orchestrator import LangGraphOrchestrator
from agents import ProductResearcher, DocAssistant, FeasibilityEvaluator, init_llm

# 初始化 | Initialize
llm = init_llm()
researcher = ProductResearcher(llm)
doc_assistant = DocAssistant(llm)
evaluator = FeasibilityEvaluator(llm)

# 创建 LangGraph 编排器 | Create LangGraph orchestrator
orchestrator = LangGraphOrchestrator(researcher, doc_assistant, evaluator)

# 执行工作流 | Execute workflow
user_input = "我们需要开发一个 AI 驱动的客户服务平台..."
final_state = orchestrator.execute_workflow(user_input)

# 打印工作流图 | Print workflow graph
orchestrator.visualize_workflow_graph()
```

## 📝 代码特点 | Code Features

### 全面的中英文注释 | Comprehensive Chinese and English Comments
每一行代码都配有详细的中英文注释，帮助新手理解代码逻辑。
Each line of code has detailed Chinese and English comments to help beginners understand the code logic.

### 清晰的模块结构 | Clear Module Structure
- `config.py`: 集中管理配置信息 | Centralized configuration management
- `agents.py`: Agent 的定义和实现 | Agent definitions and implementations
- `orchestrator.py`: 编排逻辑 | Orchestration logic
- `langgraph_orchestrator.py`: LangGraph 状态图实现 | LangGraph state graph implementation

### 可视化输出 | Visual Output
```
📊 EXECUTION GRAPH - 执行图
执行流程图 | Execution flow graph
状态转移 | State transitions
性能统计 | Performance statistics
```

## 🔧 配置说明 | Configuration Guide

### API 配置 | API Configuration

编辑 `config.py` 修改 API 设置：

```python
# 硅基流动 API Key
API_KEY = "***REMOVED***"

# API 端点
API_BASE_URL = "https://api.siliconflow.cn/v1"

# LLM 模型
MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
```

### 自定义模型温度 | Customize Model Temperature

在 `agents.py` 中调整温度参数：

```python
llm = OpenAI(
    api_key=API_KEY,
    api_base=API_BASE_URL,
    model_name=MODEL_NAME,
    temperature=0.7,  # 调整这个值 (0-1) | Adjust this value (0-1)
)
```

## 📈 输出说明 | Output Description

### 执行结果 JSON 结构 | Execution Result JSON Structure

```json
{
  "timestamp": "2024-01-02T10:30:45.123456",
  "execution_time_seconds": 245.5,
  "user_input": "用户需求详情...",
  "agents_outputs": {
    "product_researcher": {
      "agent": "Product Researcher",
      "research_result": {...},
      "status": "completed"
    },
    "doc_assistant": {
      "agent": "Doc Assistant",
      "document": "# 产品需求文档...",
      "status": "completed"
    },
    "feasibility_evaluator": {
      "agent": "Feasibility Evaluator",
      "evaluation_result": {...},
      "status": "completed"
    }
  },
  "final_summary": {
    "feasibility_score": 8.5,
    "value_propositions": [...],
    "success_factors": [...],
    "risks_and_mitigations": [...],
    "next_steps": [...]
  },
  "status": "completed"
}
```

## 🔐 安全性说明 | Security Notes

- API Key 已配置在 `config.py` 中 | API Key is configured in config.py
- 生产环境建议使用环境变量 | Use environment variables in production
- 敏感信息不应提交到版本控制 | Don't commit sensitive information to version control

```bash
# 使用环境变量 | Using environment variables
export SILICONFLOW_API_KEY="your-api-key"
```

## 🎓 学习路径 | Learning Path

### 初级 | Beginner
1. 阅读 `config.py` 理解配置 | Read config.py for configuration
2. 查看 `agents.py` 中的 Agent 实现 | Check Agent implementations in agents.py
3. 运行 `main.py` 看基础效果 | Run main.py to see basic results

### 中级 | Intermediate
1. 研究 `orchestrator.py` 的编排逻辑 | Study orchestration logic in orchestrator.py
2. 修改 Agent 的提示词 | Modify agent prompts
3. 添加自定义 Agent | Add custom agents

### 高级 | Advanced
1. 理解 `langgraph_orchestrator.py` 的状态管理 | Understand state management in langgraph_orchestrator.py
2. 实现条件分支和循环 | Implement conditional branching and loops
3. 集成外部数据源 | Integrate external data sources

## 🤝 扩展功能 | Extension Features

### 添加新 Agent | Add New Agent

```python
class MyCustomAgent:
    def __init__(self, llm):
        self.llm = llm
        self.name = "My Custom Agent"
    
    def process(self, input_data):
        # 实现自定义逻辑 | Implement custom logic
        pass
```

### 集成其他 LLM | Integrate Other LLMs

支持 OpenAI、Anthropic、Ollama 等多种 LLM 提供商。
Supports multiple LLM providers like OpenAI, Anthropic, Ollama, etc.

## 📞 故障排除 | Troubleshooting

### 问题 1: API 连接失败 | Issue 1: API Connection Failed

**解决方案 | Solution:**
```bash
# 检查 API Key | Check API Key
# 检查网络连接 | Check network connection
# 验证 API 端点是否正确 | Verify API endpoint
```

### 问题 2: 内存占用过高 | Issue 2: High Memory Usage

**解决方案 | Solution:**
- 减少 batch size
- 使用流式处理替代一次性处理
- 定期清理临时文件

### 问题 3: 生成内容质量不理想 | Issue 3: Poor Content Quality

**解决方案 | Solution:**
- 调整模型温度参数
- 优化提示词
- 增加上下文信息

## 📚 参考资源 | References

- [LangGraph Documentation](https://github.com/langchain-ai/langgraph)
- [LangChain Documentation](https://python.langchain.com/)
- [硅基流动 API 文档](https://docs.siliconflow.cn/)

## 📄 许可证 | License

MIT License - 自由使用和修改 | Free to use and modify

## 🙏 致谢 | Acknowledgments

感谢 LangChain、LangGraph 和硅基流动团队的支持。
Thanks to LangChain, LangGraph, and SiliconFlow teams for their support.

---

**最后更新 | Last Updated:** 2024-01-02
**版本 | Version:** 1.0.0
