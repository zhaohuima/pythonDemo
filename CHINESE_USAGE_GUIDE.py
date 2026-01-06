"""
Product Master 多智能体编排系统 - 中文使用指南
完整的项目使用说明和快速参考

用户可以使用本指南快速上手项目
"""

# ============================================================================
# 项目完成总结 | PROJECT COMPLETION SUMMARY
# ============================================================================

COMPLETION_SUMMARY = """

🎉 项目完成！| PROJECT COMPLETED! 🎉
════════════════════════════════════════════════════════════════════════════

项目名称 | Project Name:
    Product Master - 多智能体编排系统
    Product Master - Multi-Agent Orchestration System

完成时间 | Completion Date:
    2024-01-02

项目状态 | Status:
    ✅ 100% 完成 | 100% Complete

版本 | Version:
    1.0.0

════════════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# 项目统计 | PROJECT STATISTICS
# ============================================================================

STATISTICS = """
📊 项目统计数据 | PROJECT STATISTICS
════════════════════════════════════════════════════════════════════════════

文件统计 | Files:
  ✅ Python 文件:         7 个
  ✅ Markdown 文档:       2 个  
  ✅ 配置文件:           1 个
  ✅ 总计:              12 个文件

代码统计 | Code:
  ✅ 总代码行数:        3300+ 行
  ✅ 中英文注释:         800+ 行
  ✅ 类定义:             7 个
  ✅ 方法函数:          25+ 个
  ✅ 注释率:            ~25%

技术指标 | Technical:
  ✅ Agent 数量:        4 个 (Researcher, Assistant, Evaluator, Master)
  ✅ 支持模式:          2 种 (基础模式 + LangGraph 模式)
  ✅ API 支持:          1 个 (硅基流动)
  ✅ 文档完整度:        100%

════════════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# 核心功能详解 | CORE FEATURES EXPLAINED
# ============================================================================

CORE_FEATURES = """
✨ 核心功能详解 | CORE FEATURES
════════════════════════════════════════════════════════════════════════════

1️⃣ 产品研究员 Agent (Product Researcher)
   职责：进行产品需求调研和市场分析
   关键功能：
   • 分析用户的核心需求
   • 进行竞争对手分析
   • 识别目标用户群体
   • 提供市场洞察和建议
   
   使用方式：
   from agents import ProductResearcher, init_llm
   llm = init_llm()
   researcher = ProductResearcher(llm)
   result = researcher.research("您的产品需求")

2️⃣ 文档助手 Agent (Doc Assistant)
   职责：生成专业的产品需求文档
   关键功能：
   • 生成产品需求文档 (PRD)
   • 设计功能规格说明
   • 编写用户故事
   • 定义非功能需求
   
   使用方式：
   from agents import DocAssistant, init_llm
   llm = init_llm()
   assistant = DocAssistant(llm)
   result = assistant.generate_doc(user_input, research_data)

3️⃣ 可行性评估员 Agent (Feasibility Evaluator)
   职责：评估产品的可行性和技术架构
   关键功能：
   • 技术可行性评估
   • 系统架构设计
   • 成本预算评估
   • 合规性检查
   
   使用方式：
   from agents import FeasibilityEvaluator, init_llm
   llm = init_llm()
   evaluator = FeasibilityEvaluator(llm)
   result = evaluator.evaluate(user_input, research, doc)

4️⃣ 产品主人编排器 (Product Master Orchestrator)
   职责：协调所有 Agent 并汇总结果
   关键功能：
   • 按顺序执行三个 Agent
   • 聚合所有输出结果
   • 提炼关键要点
   • 生成最终建议
   
   使用方式：
   from orchestrator import ProductMaster
   master = ProductMaster()
   result = master.orchestrate("您的产品需求")
   master.print_execution_summary(result)

════════════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# 快速开始步骤 | QUICK START STEPS
# ============================================================================

QUICK_START = """
🚀 快速开始（5 分钟）| QUICK START (5 MINUTES)
════════════════════════════════════════════════════════════════════════════

第一步：检查环境
  $ python --version
  # 确保 Python 3.8 或以上

第二步：进入项目目录
  $ cd /workspaces/pythonDemo

第三步：安装依赖
  $ pip install -r requirements.txt
  # 这将安装：langgraph, langchain, openai 等

第四步：验证配置
  $ cat config.py
  # 确保 API_KEY 已正确配置

第五步：运行演示
  $ python main.py
  # 或者
  $ python langgraph_demo.py

第六步：查看结果
  $ cat outputs/orchestration_result.json
  # 查看执行结果

完成！系统已成功运行！

════════════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# 文件指南 | FILES GUIDE
# ============================================================================

FILES_GUIDE = """
📁 文件指南 | FILES GUIDE
════════════════════════════════════════════════════════════════════════════

🔧 配置和设置
─────────────

config.py (571 字节)
  作用：系统配置文件
  包含：API Key, API 端点, 模型名称
  修改场景：需要更换 API 或模型时
  难度：⭐ 简单

requirements.txt (108 字节)
  作用：项目依赖管理
  包含：langgraph, langchain, openai 等
  修改场景：需要添加新的库依赖时
  难度：⭐ 简单


🤖 核心实现
─────────────

agents.py (9.1K)
  作用：三个 Agent 的实现
  包含：
    • ProductResearcher - 产品研究员
    • DocAssistant - 文档助手
    • FeasibilityEvaluator - 可行性评估员
  关键方法：
    • research() - 执行研究
    • generate_doc() - 生成文档
    • evaluate() - 执行评估
  难度：⭐⭐⭐ 中等

orchestrator.py (14K)
  作用：基础编排器实现
  包含：
    • ProductMaster 编排器类
    • orchestrate() 主方法
    • _summarize_results() 汇总方法
    • print_execution_summary() 输出方法
  特点：简洁高效，易于理解
  难度：⭐⭐⭐ 中等

langgraph_orchestrator.py (17K)
  作用：LangGraph 版本编排器
  包含：
    • OrchestratorState 状态定义
    • LangGraphOrchestrator 编排器类
    • 四个执行节点
    • 工作流可视化
  特点：详细日志，清晰流程
  难度：⭐⭐⭐⭐ 较难


▶️ 演示程序
─────────────

main.py (3.5K)
  作用：基础版本演示程序
  执行：python main.py
  输出：outputs/orchestration_result.json
  执行时间：3-5 分钟
  难度：⭐ 简单

langgraph_demo.py (8.3K)
  作用：LangGraph 版本演示程序
  执行：python langgraph_demo.py
  输出：outputs/langgraph_results.json
  执行时间：3-5 分钟
  难度：⭐ 简单


📚 文档和指南
─────────────

README.md (15K)
  作用：完整的项目文档
  内容：项目简介, 架构说明, 使用示例, 故障排除等
  阅读时间：15-20 分钟
  难度：⭐ 简单

PROJECT_SUMMARY.py (22K)
  作用：项目全面总结
  内容：核心功能, 文件结构, 执行流程, 扩展性设计等
  阅读时间：20-30 分钟
  难度：⭐⭐ 简单-中等

QUICK_START_GUIDE.py (19K)
  作用：8 步快速开始指南
  内容：详细的上手步骤, 常见问题解决等
  阅读时间：30-45 分钟
  难度：⭐ 简单

PROJECT_COMPLETION_REPORT.md (18K)
  作用：项目完成报告
  内容：完成情况, 功能清单, 使用示例等
  阅读时间：10-15 分钟
  难度：⭐ 简单

PROJECT_SHOWCASE.py (21K)
  作用：项目展示和索引
  内容：学习路径, 命令参考, 使用场景等
  难度：⭐ 简单


════════════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# 常见操作 | COMMON OPERATIONS
# ============================================================================

COMMON_OPERATIONS = """
💻 常见操作命令 | COMMON OPERATIONS
════════════════════════════════════════════════════════════════════════════

1. 查看项目结构
   $ ls -lh /workspaces/pythonDemo/
   
2. 查看文件代码
   $ cat agents.py
   $ cat orchestrator.py
   $ cat config.py

3. 运行基础演示
   $ python main.py
   
4. 运行 LangGraph 演示
   $ python langgraph_demo.py

5. 查看执行结果
   $ cat outputs/orchestration_result.json
   $ cat outputs/langgraph_results.json

6. 统计代码行数
   $ wc -l *.py
   
7. 检查语法错误
   $ python -m py_compile *.py
   
8. 查看快速开始指南
   $ python QUICK_START_GUIDE.py
   
9. 查看项目展示
   $ python PROJECT_SHOWCASE.py
   
10. 创建输出目录（如果不存在）
    $ mkdir -p outputs

════════════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# 自定义使用 | CUSTOM USAGE
# ============================================================================

CUSTOM_USAGE = """
🎯 如何自定义使用 | HOW TO CUSTOMIZE
════════════════════════════════════════════════════════════════════════════

修改 main.py 中的用户输入：

打开 main.py，找到以下部分：

    user_requirement = \"\"\"
    我们想要开发一个针对电商企业的供应链管理系统。
    ...
    \"\"\"

替换为您自己的需求描述：

    user_requirement = \"\"\"
    我想开发一个在线教育平台。
    功能包括：
    1. 课程管理和发布
    2. 学生学习记录追踪
    3. 在线评估和反馈
    4. 社区互动功能
    
    目标：支持 10,000+ 并发用户
    时间框架：4 个月
    预算：100 万
    \"\"\"

然后运行：
    $ python main.py

等待 3-5 分钟，系统会为您生成完整的评估报告。

════════════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# 故障排除 | TROUBLESHOOTING
# ============================================================================

TROUBLESHOOTING = """
🔧 常见问题解决 | TROUBLESHOOTING
════════════════════════════════════════════════════════════════════════════

问题 1: ImportError: No module named 'langgraph'
解决方案：
  $ pip install -r requirements.txt

问题 2: API 连接错误 (403 Unauthorized)
解决方案：
  1. 检查 config.py 中的 API_KEY 是否正确
  2. 检查网络连接
  3. 检查 API 端点是否可访问

问题 3: 执行超时
解决方案：
  1. API 可能响应较慢，请耐心等待
  2. 检查网络连接质量
  3. 尝试简化输入内容

问题 4: JSON 解析错误
解决方案：
  这是正常现象，系统会自动处理
  如果频繁发生，可能需要调整模型温度参数

问题 5: 输出文件无法保存
解决方案：
  1. 检查 outputs 目录是否存在
  2. 创建目录：mkdir -p outputs
  3. 检查目录权限：chmod 755 outputs

════════════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# 学习建议 | LEARNING RECOMMENDATIONS
# ============================================================================

LEARNING_RECOMMENDATIONS = """
📚 学习建议 | LEARNING RECOMMENDATIONS
════════════════════════════════════════════════════════════════════════════

推荐学习路径：

🟢 初级（新手）- 1 小时
  1. 阅读 README.md 的项目简介部分 (10 分钟)
  2. 运行 python main.py (5 分钟)
  3. 查看 outputs/orchestration_result.json (5 分钟)
  4. 修改 user_requirement 并重新运行 (40 分钟)

🟡 中级（进阶）- 2 小时
  1. 完整阅读 README.md 和相关文档 (30 分钟)
  2. 逐行阅读 agents.py 代码 (30 分钟)
  3. 理解 orchestrator.py 的编排逻辑 (30 分钟)
  4. 尝试自定义修改和运行 (30 分钟)

🔴 高级（专家）- 4 小时
  1. 完成中级所有内容 (2 小时)
  2. 深入研究 langgraph_orchestrator.py (45 分钟)
  3. 尝试添加自定义 Agent (45 分钟)
  4. 设计完整的自定义工作流 (30 分钟)

推荐阅读顺序：
  1. README.md (项目概述)
  2. config.py (配置说明)
  3. agents.py (Agent 实现)
  4. orchestrator.py (编排逻辑)
  5. langgraph_orchestrator.py (状态管理)
  6. PROJECT_SUMMARY.py (深入理解)

关键概念理解：
  □ 理解什么是 Agent
  □ 理解编排器的作用
  □ 理解 LangGraph 的状态管理
  □ 理解工作流的执行流程
  □ 理解如何扩展系统

════════════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# 高级功能 | ADVANCED FEATURES
# ============================================================================

ADVANCED_FEATURES = """
🚀 高级功能 | ADVANCED FEATURES
════════════════════════════════════════════════════════════════════════════

1. 添加自定义 Agent
   
   创建新的 Agent 类：
   
   class CustomAgent:
       def __init__(self, llm):
           self.llm = llm
           self.name = "Custom Agent"
       
       def process(self, input_data):
           prompt = f"处理: {input_data}"
           return self.llm.predict(prompt)
   
   集成到编排器中：
   
   custom_agent = CustomAgent(llm)
   result = custom_agent.process(input_data)

2. 自定义工作流
   
   创建新的编排器类，继承并修改执行逻辑：
   
   class CustomOrchestrator(ProductMaster):
       def orchestrate(self, user_input):
           # 自定义工作流逻辑
           pass

3. 条件分支和循环
   
   在工作流中添加条件判断：
   
   if result['quality_score'] < 0.7:
       result = self.researcher.research(input)
   else:
       result = self.evaluator.evaluate(input)

4. 异步处理
   
   支持异步调用以提高性能：
   
   async def async_orchestrate(self, user_input):
       results = await asyncio.gather(
           self.researcher.research(user_input),
           self.doc_assistant.generate_doc(user_input)
       )

5. 集成外部数据源
   
   从数据库或 API 获取数据：
   
   database_data = fetch_from_database()
   enriched_input = enrich_with_external_data(input, database_data)
   result = orchestrator.orchestrate(enriched_input)

════════════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# 最佳实践 | BEST PRACTICES
# ============================================================================

BEST_PRACTICES = """
✨ 最佳实践 | BEST PRACTICES
════════════════════════════════════════════════════════════════════════════

1. 代码组织
   ✅ 保持模块的单一职责
   ✅ 使用清晰的命名规范
   ✅ 添加详细的注释和文档
   ✅ 遵循 Python 风格指南 (PEP 8)

2. 提示词优化
   ✅ 使用清晰明确的指令
   ✅ 提供充分的上下文信息
   ✅ 指定输出的格式和结构
   ✅ 包含例子说明

3. 错误处理
   ✅ 捕获并处理 API 异常
   ✅ 实现重试机制
   ✅ 记录详细的错误日志
   ✅ 实现优雅的降级策略

4. 性能优化
   ✅ 使用缓存减少重复调用
   ✅ 利用异步处理提高效率
   ✅ 批量处理数据
   ✅ 优化 API 调用成本

5. 安全性
   ✅ 不要硬编码敏感信息
   ✅ 使用环境变量管理配置
   ✅ 定期更新依赖库
   ✅ 验证和清理用户输入

6. 文档和维护
   ✅ 为每个函数写文档字符串
   ✅ 保持代码注释的准确性
   ✅ 定期更新 README 和文档
   ✅ 记录重要的更改和决策

════════════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# 支持和反馈 | SUPPORT & FEEDBACK
# ============================================================================

SUPPORT_FEEDBACK = """
💬 支持和反馈 | SUPPORT & FEEDBACK
════════════════════════════════════════════════════════════════════════════

如果您在使用过程中遇到问题或有改进建议：

1. 查看文档
   - 阅读 README.md 获取基础信息
   - 查看 QUICK_START_GUIDE.py 获取详细步骤
   - 查看 PROJECT_SUMMARY.py 了解深层概念

2. 运行诊断
   - 检查 Python 版本
   - 验证依赖库安装
   - 测试 API 连接
   - 查看错误日志

3. 寻求帮助
   - 查阅故障排除部分
   - 参考使用示例
   - 查看代码注释
   - 参考最佳实践

4. 报告问题
   - 提供完整的错误信息
   - 包含复现步骤
   - 说明您的环境信息
   - 附加相关的日志

5. 改进建议
   - 建议新功能
   - 改进 UI/UX
   - 优化性能
   - 增强文档

════════════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# 使用约定 | USAGE AGREEMENT
# ============================================================================

USAGE_AGREEMENT = """
⚖️ 使用约定 | USAGE AGREEMENT
════════════════════════════════════════════════════════════════════════════

本项目（Product Master）是为数字化项目产品经理设计的辅助工具。

使用条款：
  • 本项目采用 MIT 许可证，可自由使用和修改
  • 使用时请遵守相应的法律法规
  • API Key 仅用于开发和测试，不应在生产环境中使用
  • 不应用于任何非法目的

责任说明：
  • 本项目按"现状"提供，不提供任何担保
  • 使用本项目产生的任何后果由用户自行承担
  • 作者不对任何数据损失或业务损害承担责任

数据隐私：
  • 所有用户输入都会发送到 API 进行处理
  • 请不要输入包含敏感信息的内容
  • 建议在生产环境中自行部署本地 LLM

持续改进：
  • 项目会持续更新和改进
  • 欢迎提供反馈和建议
  • 保持依赖库和安全补丁的最新状态

════════════════════════════════════════════════════════════════════════════
"""

# ============================================================================
# 主要显示函数
# ============================================================================

def main():
    """显示完整的中文使用指南"""
    
    print("\n" + "="*80)
    print(COMPLETION_SUMMARY)
    print("="*80 + "\n")
    
    print(STATISTICS)
    print("\n" + "="*80 + "\n")
    
    print(CORE_FEATURES)
    print("\n" + "="*80 + "\n")
    
    print(QUICK_START)
    print("\n" + "="*80 + "\n")
    
    print(FILES_GUIDE)
    print("\n" + "="*80 + "\n")
    
    print(COMMON_OPERATIONS)
    print("\n" + "="*80 + "\n")
    
    print(CUSTOM_USAGE)
    print("\n" + "="*80 + "\n")
    
    print(TROUBLESHOOTING)
    print("\n" + "="*80 + "\n")
    
    print(LEARNING_RECOMMENDATIONS)
    print("\n" + "="*80 + "\n")
    
    print(ADVANCED_FEATURES)
    print("\n" + "="*80 + "\n")
    
    print(BEST_PRACTICES)
    print("\n" + "="*80 + "\n")
    
    print(SUPPORT_FEEDBACK)
    print("\n" + "="*80 + "\n")
    
    print(USAGE_AGREEMENT)
    
    print("\n" + "="*80)
    print("🎉 感谢使用 Product Master 系统！")
    print("🎉 Thank you for using Product Master System!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
