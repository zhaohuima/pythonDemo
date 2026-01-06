"""
LangGraph 演示脚本 | LangGraph Demo Script
展示如何使用LangGraph版本的多智能体编排系统
Demonstrates how to use the LangGraph version of multi-agent orchestration system
"""

import json
import os
from datetime import datetime
from agents import ProductResearcher, DocAssistant, FeasibilityEvaluator, init_llm
from langgraph_orchestrator import LangGraphOrchestrator


def main():
    """
    主函数 | Main Function
    演示LangGraph多智能体编排系统
    Demonstrates LangGraph multi-agent orchestration system
    """
    
    print("\n" + "="*80)
    print("🚀 LangGraph Multi-Agent Orchestration System Demo")
    print("🚀 LangGraph多智能体编排系统演示")
    print("="*80 + "\n")
    
    # 步骤1: 初始化LLM | Step 1: Initialize LLM
    print("⚙️  Step 1: Initializing Language Model")
    print("⚙️  第一步：初始化语言模型\n")
    
    # 调用init_llm函数创建LLM实例 | Call init_llm function to create LLM instance
    llm = init_llm()
    
    print("✓ Language Model initialized successfully")
    print("✓ 语言模型初始化成功\n")
    
    # 步骤2: 初始化三个Agent | Step 2: Initialize three agents
    print("⚙️  Step 2: Initializing Agents")
    print("⚙️  第二步：初始化Agent\n")
    
    # 创建产品研究员Agent | Create Product Researcher Agent
    researcher = ProductResearcher(llm)
    print(f"  ✓ {researcher.name} initialized")
    print(f"  ✓ {researcher.name}已初始化\n")
    
    # 创建文档助手Agent | Create Doc Assistant Agent
    doc_assistant = DocAssistant(llm)
    print(f"  ✓ {doc_assistant.name} initialized")
    print(f"  ✓ {doc_assistant.name}已初始化\n")
    
    # 创建可行性评估员Agent | Create Feasibility Evaluator Agent
    evaluator = FeasibilityEvaluator(llm)
    print(f"  ✓ {evaluator.name} initialized")
    print(f"  ✓ {evaluator.name}已初始化\n")
    
    # 步骤3: 创建LangGraph编排器 | Step 3: Create LangGraph Orchestrator
    print("⚙️  Step 3: Creating LangGraph Orchestrator")
    print("⚙️  第三步：创建LangGraph编排器\n")
    
    # 创建LangGraph编排器实例 | Create LangGraph Orchestrator instance
    orchestrator = LangGraphOrchestrator(researcher, doc_assistant, evaluator)
    
    print("✓ LangGraph Orchestrator created successfully")
    print("✓ LangGraph编排器创建成功\n")
    
    # 步骤4: 可视化工作流图 | Step 4: Visualize workflow graph
    print("⚙️  Step 4: Visualizing Workflow Graph")
    print("⚙️  第四步：可视化工作流图\n")
    
    # 调用可视化方法打印工作流结构 | Call visualization method to print workflow structure
    orchestrator.visualize_workflow_graph()
    
    # 步骤5: 准备用户输入 | Step 5: Prepare user input
    print("⚙️  Step 5: Preparing User Input")
    print("⚙️  第五步：准备用户输入\n")
    
    # 示例用户需求 | Example user requirement
    user_requirement = """
    我们需要开发一个AI驱动的客户服务平台。
    核心功能包括：
    1. 智能客服机器人
    2. 自动工单分类和路由
    3. 情感分析和质量监控
    4. 多渠道整合（邮件、聊天、电话）
    
    业务目标：
    - 提高客服效率50%
    - 降低客服成本30%
    - 提升客户满意度至95%
    - 支持日均10000次对话
    
    目标用户：SaaS企业和中型电商
    预算：500万
    上线时间：4个月
    
    English Translation:
    We need to develop an AI-driven customer service platform.
    Core features include:
    1. Intelligent customer service chatbot
    2. Automatic ticket classification and routing
    3. Sentiment analysis and quality monitoring
    4. Multi-channel integration (email, chat, phone)
    
    Business goals:
    - Increase customer service efficiency by 50%
    - Reduce customer service costs by 30%
    - Improve customer satisfaction to 95%
    - Support 10,000 conversations per day
    
    Target users: SaaS enterprises and mid-sized e-commerce
    Budget: 5 million yuan
    Launch time: 4 months
    """
    
    print("✓ User requirement prepared")
    print("✓ 用户需求已准备\n")
    
    # 步骤6: 执行工作流 | Step 6: Execute workflow
    print("⚙️  Step 6: Executing Orchestration Workflow")
    print("⚙️  第六步：执行编排工作流\n")
    
    # 调用execute_workflow方法执行完整的工作流 | Call execute_workflow to execute complete workflow
    final_state = orchestrator.execute_workflow(user_requirement)
    
    # 步骤7: 打印执行日志和结果 | Step 7: Print execution log and results
    print("⚙️  Step 7: Printing Execution Results")
    print("⚙️  第七步：打印执行结果\n")
    
    print_execution_results(final_state)
    
    # 步骤8: 保存结果 | Step 8: Save results
    print("⚙️  Step 8: Saving Results to File")
    print("⚙️  第八步：保存结果到文件\n")
    
    # 保存最终状态到JSON文件 | Save final state to JSON file
    save_results(final_state)
    
    print("\n" + "="*80)
    print("✨ LangGraph Orchestration Demo Complete")
    print("✨ LangGraph编排演示完成")
    print("="*80 + "\n")


def print_execution_results(state):
    """
    打印执行结果 | Print execution results
    
    Args:
        state: 最终的编排器状态 | Final orchestrator state
    """
    print("="*80)
    print("📋 EXECUTION RESULTS - 执行结果")
    print("="*80 + "\n")
    
    # 打印执行日志 | Print execution log
    print("执行日志 | Execution Log:")
    print("-" * 80)
    for i, log_entry in enumerate(state.get("execution_log", []), 1):
        print(f"{i}. {log_entry}")
    print("-" * 80 + "\n")
    
    # 打印执行时间 | Print execution time
    print(f"⏱️  总执行时间 | Total Execution Time: {state.get('execution_time', 0):.2f} seconds")
    print(f"⏱️  总执行时间 | 总执行时间：{state.get('execution_time', 0):.2f}秒\n")
    
    # 打印最终汇总 | Print final summary
    print("="*80)
    print("📊 FINAL SUMMARY - 最终汇总")
    print("="*80 + "\n")
    
    summary = state.get("final_summary", {})
    
    print(f"✓ 研究完成 | Research Conducted: {summary.get('research_conducted', False)}")
    print(f"✓ 文档生成 | Document Generated: {summary.get('document_generated', False)}")
    print(f"✓ 评估完成 | Evaluation Completed: {summary.get('evaluation_completed', False)}")
    print(f"✓ 总步骤数 | Total Steps: {summary.get('total_steps', 0)}")
    print(f"✓ 状态 | Status: {summary.get('status', 'unknown').upper()}\n")


def save_results(state, filename="langgraph_results.json"):
    """
    将结果保存到JSON文件 | Save results to JSON file
    
    Args:
        state: 要保存的编排器状态 | Orchestrator state to save
        filename: 文件名 | Filename
    """
    # 创建输出目录 | Create output directory if it doesn't exist
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 构建完整的文件路径 | Build full file path
    filepath = os.path.join(output_dir, filename)
    
    # 将状态转换为可序列化的格式 | Convert state to serializable format
    serializable_state = {
        "timestamp": state.get("timestamp"),
        "execution_time": state.get("execution_time"),
        "user_input": state.get("user_input"),
        "execution_log": state.get("execution_log", []),
        "final_summary": state.get("final_summary", {}),
        # 添加其他字段的摘要 | Add summary of other fields
        "research_result_keys": list(state.get("research_result", {}).keys()),
        "document_content_length": len(state.get("document_content", "")),
        "evaluation_result_keys": list(state.get("evaluation_result", {}).keys()),
    }
    
    # 保存到JSON文件 | Save to JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(serializable_state, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ Results saved to: {filepath}")
    print(f"✅ 结果已保存到：{filepath}\n")


if __name__ == "__main__":
    """
    程序入口点 | Program entry point
    当此文件被直接运行时执行主函数
    Execute main function when this file is run directly
    """
    main()
