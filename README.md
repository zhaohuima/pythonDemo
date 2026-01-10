# 🚀 Product Master - LangGraph Multi-Agent Orchestration System

基于 LangGraph 的多智能体编排系统，专为数字化项目的产品经理设计。

A LangGraph-based multi-agent orchestration system designed for product managers in digital projects.

---

## 📋 项目概述 | Project Overview

本系统通过协调三个专业 AI Agent，帮助产品经理快速、全面地评估和规划新产品：

1. **Product Researcher** - 产品研究员：进行市场调研和需求分析
2. **Doc Assistant** - 文档助手：生成产品需求文档（PRD）
3. **Feasibility Evaluator** - 可行性评估员：评估技术可行性、成本和风险

---

## 🛠 技术栈 | Technology Stack

- **Python 3.9+**
- **LangGraph** - 状态图工作流管理
- **LangChain** - LLM 集成
- **Flask** - Web 应用框架
- **硅基流动 API** - LLM 服务

---

## 📁 项目结构 | Project Structure

```
pythonDemo/
├── main.py                      # 命令行入口 | CLI Entry Point
├── web_app.py                   # Web 应用入口 | Web App Entry Point
├── langgraph_orchestrator.py    # LangGraph 编排器 | LangGraph Orchestrator
├── agents.py                    # Agent 定义 | Agent Definitions
├── config.py                    # 配置文件 | Configuration
├── logger_config.py             # 日志配置 | Logger Configuration
├── requirements.txt             # 依赖列表 | Dependencies
├── templates/
│   └── index.html               # Web 前端页面 | Web Frontend
├── static/
│   ├── css/style.css            # 样式文件 | Styles
│   └── js/app.js                # 前端脚本 | Frontend Script
├── logs/                        # 日志目录 | Log Directory
└── outputs/                     # 输出结果 | Output Results
```

---

## 🚀 快速开始 | Quick Start

### 1. 安装依赖 | Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. 配置 API | Configure API

编辑 `config.py`，设置您的 API 密钥：

```python
API_KEY = "your-api-key"
API_BASE_URL = "https://api.siliconflow.cn/v1"
MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
```

### 3. 运行方式 | Run Methods

#### 方式 A: 命令行模式 | CLI Mode

```bash
python main.py
```

#### 方式 B: Web 应用模式 | Web App Mode

```bash
python web_app.py
```

然后访问：http://localhost:5000

---

## 🌐 Web 应用使用 | Web App Usage

1. 在输入框中输入产品需求
2. 点击 "Start Orchestration" 按钮
3. 实时查看执行进度
4. 查看最终结果（研究结果、文档、评估、汇总）

---

## 📊 LangGraph 工作流 | LangGraph Workflow

### 工作流执行顺序 | Workflow Execution Order

```
┌──────────────────────────────────────────────────────────────────┐
│                    LangGraph Orchestration Flow                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│    [User Input]                                                   │
│         │                                                         │
│         ▼                                                         │
│    ┌─────────────────┐                                           │
│    │   researcher    │  ← Product Research Node                   │
│    │   Output:       │     • Conduct market research              │
│    │   research_result│     • Analyze requirements                │
│    └────────┬────────┘                                           │
│             │                                                     │
│             ▼                                                     │
│    ┌─────────────────┐                                           │
│    │    evaluator    │  ← Feasibility Evaluation Node             │
│    │   Input:        │     • Technical feasibility                │
│    │   research_result│     • Cost assessment                     │
│    │   Output:       │     • Risk analysis                        │
│    │   evaluation_result│                                          │
│    └────────┬────────┘                                           │
│             │                                                     │
│             ▼                                                     │
│    ┌─────────────────┐                                           │
│    │   aggregation   │  ← Result Aggregation Node                 │
│    │   Input:        │     • Summarize findings                   │
│    │   research_result│     • Synthesize insights                 │
│    │   evaluation_result│   • Generate recommendations             │
│    │   Output:       │                                            │
│    │   final_summary │                                            │
│    └────────┬────────┘                                           │
│             │                                                     │
│             ▼                                                     │
│    ┌─────────────────┐                                           │
│    │  doc_assistant  │  ← Documentation Node                      │
│    │   Input:        │     • Generate PRD                         │
│    │   all previous  │     • Create product docs                  │
│    │   outputs       │     • Based on all results                 │
│    │   Output:       │                                            │
│    │   document_content│                                          │
│    └────────┬────────┘                                           │
│             │                                                     │
│             ▼                                                     │
│       [Final Output]                                              │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 节点依赖关系 | Node Dependencies

| 节点 | 输入 | 输出 |
|------|------|------|
| `researcher_node` | `user_input` | `research_result` |
| `evaluator_node` | `user_input`, `research_result` | `evaluation_result` |
| `aggregation_node` | `research_result`, `evaluation_result` | `final_summary` |
| `doc_assistant_node` | `user_input`, `research_result`, `evaluation_result`, `final_summary` | `document_content` |

**工作流说明 | Workflow Description:**
1. **Product Research** 首先执行，基于用户需求进行市场调研和需求分析
2. **Feasibility Evaluation** 基于研究结果评估技术可行性和风险
3. **Result Aggregation** 汇总研究和评估结果，生成执行摘要
4. **Documentation Generation** 最后执行，基于所有前序结果生成完整的产品文档

---

## 📝 日志查看 | Log Viewing

日志文件保存在 `logs/` 目录：

```bash
# 查看今天的日志
cat logs/product_master_$(date +%Y%m%d).log

# 实时监控日志
tail -f logs/product_master_$(date +%Y%m%d).log

# 搜索特定内容
grep "NODE:" logs/product_master_*.log
```

详细日志说明请参考 `LOG_VIEWING_GUIDE.md`

---

## 📤 输出结果 | Output Results

执行结果保存在 `outputs/` 目录，格式为 JSON：

```json
{
  "timestamp": "2026-01-07T10:30:00",
  "execution_time": 120.5,
  "user_input": "...",
  "research_result": {...},
  "document_content": "...",
  "evaluation_result": {...},
  "final_summary": {...}
}
```

---

## 🔧 配置说明 | Configuration

### config.py

| 参数 | 说明 |
|------|------|
| `API_KEY` | LLM API 密钥 |
| `API_BASE_URL` | API 端点 |
| `MODEL_NAME` | 模型名称 |
| `LOG_LEVEL` | 日志级别 (INFO/DEBUG) |

---

## 📚 核心模块 | Core Modules

### langgraph_orchestrator.py

- `OrchestratorState` - 状态定义
- `LangGraphOrchestrator` - 编排器类
  - `_build_workflow()` - 构建 LangGraph 工作流
  - `researcher_node()` - 研究节点（第一步）
  - `evaluator_node()` - 评估节点（第二步，基于研究结果）
  - `aggregation_node()` - 汇总节点（第三步，汇总研究和评估结果）
  - `doc_assistant_node()` - 文档节点（第四步，基于所有前序结果）
  - `execute_workflow()` - 执行工作流
  - `stream_workflow()` - 流式执行

### agents.py

- `SimpleLLM` - LLM 客户端
- `ProductResearcher` - 产品研究员
- `DocAssistant` - 文档助手
- `FeasibilityEvaluator` - 可行性评估员

---

## 🌐 部署到EC2 | EC2 Deployment

### 快速部署

```bash
# 使用部署脚本
./deploy_to_ec2.sh

# 在EC2上设置环境
ssh -i "密钥路径" ubuntu@13.239.2.255
cd /home/ubuntu/ProductMaster
bash deploy_setup_ec2.sh
```

### Nginx配置（生产环境）

项目使用Nginx作为反向代理，配置文件位于：
- 配置文件模板: `nginx_product_master.conf`
- 详细文档: `NGINX_SETUP.md`

**快速修复样式加载问题**：
```bash
# 在EC2上运行
sudo bash fix_nginx.sh
```

详细修复指南请参考：`FIX_STYLE_AND_SSL.md`

### HTTPS配置（方案A - Let's Encrypt）

为域名 `productmaster.dpdns.org` 配置HTTPS：

```bash
# 1. 检查DNS解析
./check_dns.sh

# 2. 配置HTTPS（自动化）
./setup_https.sh
```

**详细文档**：
- 📘 `HTTPS_SETUP_GUIDE.md` - 完整HTTPS配置指南
- 🔐 `SECURITY_GROUP_HTTPS.md` - 安全组配置说明

**配置前准备**：
1. ✅ 确保DNS已配置（A记录指向 `13.239.2.255`）
2. ✅ 确保安全组已开放端口80和443
3. ✅ 确保Nginx已安装并运行

### 常见问题

#### 1. 样式文件无法加载
- 检查Nginx配置中的静态文件路径
- 确保文件权限正确（755目录，644文件）
- 参考 `FIX_STYLE_AND_SSL.md`

#### 2. 浏览器显示"不安全"
- HTTP协议会显示此警告
- **解决方案**: 运行 `./setup_https.sh` 配置HTTPS
- 详细步骤参考 `HTTPS_SETUP_GUIDE.md`

#### 3. 服务无法访问
- 检查安全组是否开放端口80（HTTP）或443（HTTPS）
- 参考 `SECURITY_GROUP_HTTPS.md` 配置安全组
- 检查Nginx和Gunicorn服务状态
- 查看日志：`sudo journalctl -u product-master -f`

---

## ⚠️ 注意事项 | Notes

1. 确保 API 配置正确
2. LLM 调用可能需要较长时间，请耐心等待
3. 日志文件会自动按日期分割
4. 结果文件会自动保存到 `outputs/` 目录
5. 生产环境建议使用Nginx + Gunicorn部署
6. 如需HTTPS，请配置SSL证书

---

## 📄 License

MIT License

---

## 🙏 致谢 | Acknowledgments

- LangChain / LangGraph Team
- SiliconFlow (硅基流动)
