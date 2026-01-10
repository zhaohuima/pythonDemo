"""
主程序 | Main Program
使用 LangGraph 多智能体编排系统
Multi-Agent Orchestration System using LangGraph
"""

import json
import os
from langgraph_orchestrator import LangGraphOrchestrator
from agents import ProductResearcher, DocAssistant, FeasibilityEvaluator, init_llm
from logger_config import logger


def main():
    """
    主函数 | Main Function
    使用 LangGraph 编排器运行多智能体系统
    Run multi-agent system using LangGraph orchestrator
    """
    
    print("\n" + "=" * 80)
    print("🚀 Product Master - LangGraph Multi-Agent Orchestration System")
    print("🚀 产品主人 - LangGraph 多智能体编排系统")
    print("=" * 80 + "\n")
    
    # 初始化 LLM | Initialize LLM
    print("⚙️  Step 1: Initializing Language Model...")
    logger.info("Initializing LLM...")
    llm = init_llm()
    print("✓ Language Model initialized\n")
    logger.info("✓ LLM initialized")
    
    # 初始化三个 Agent | Initialize three agents
    print("⚙️  Step 2: Initializing Agents...")
    logger.info("Initializing Agents...")
    
    researcher = ProductResearcher(llm)
    print(f"  ✓ {researcher.name} initialized")
    
    doc_assistant = DocAssistant(llm)
    print(f"  ✓ {doc_assistant.name} initialized")
    
    evaluator = FeasibilityEvaluator(llm)
    print(f"  ✓ {evaluator.name} initialized\n")
    logger.info("✓ All agents initialized")
    
    # 创建 LangGraph 编排器 | Create LangGraph Orchestrator
    print("⚙️  Step 3: Creating LangGraph Orchestrator...")
    logger.info("Creating LangGraph Orchestrator...")
    orchestrator = LangGraphOrchestrator(researcher, doc_assistant, evaluator, llm)
    print("✓ LangGraph Orchestrator created\n")
    logger.info("✓ LangGraph Orchestrator created")
    
    # 可视化工作流图 | Visualize workflow graph
    print("⚙️  Step 4: Workflow Graph Structure...")
    orchestrator.visualize_workflow_graph()
    
    # 示例用户输入：产品需求 | Example user input: product requirement
    user_requirement = """   
    We want to develop a supply chain management system for e-commerce enterprises.
    Functional requirements include:
    1. Real-time inventory tracking and management
    2. Supplier collaboration platform
    3. Order forecasting and optimization
    4. Cost analysis and reporting
    
    Our goals are:
    - Improve supply chain efficiency by 30%
    - Reduce inventory costs by 20%
    - Shorten delivery time
    - Improve supplier relationships
    
    Target market: Mid-sized e-commerce enterprises (annual sales 50-200 million yuan)
    Timeline: MVP launch within 6 months
    """
    
    # 执行工作流 | Execute workflow
    print("\n⚙️  Step 5: Executing LangGraph Workflow...")
    print("=" * 80 + "\n")
    logger.info("Starting workflow execution...")
    
    result = orchestrator.execute_workflow(user_requirement)
    
    # 打印执行结果 | Print execution results
    print("\n" + "=" * 80)
    print("📋 EXECUTION RESULTS")
    print("=" * 80 + "\n")
    
    # 打印执行日志 | Print execution log
    print("Execution Log:")
    print("-" * 40)
    for i, log_entry in enumerate(result.get("execution_log", []), 1):
        print(f"  {i}. {log_entry}")
    print()
    
    # 打印执行时间 | Print execution time
    print(f"⏱️  Total Execution Time: {result.get('execution_time', 0):.2f} seconds\n")
    
    # 打印最终汇总 | Print final summary
    print("Final Summary:")
    print("-" * 40)
    summary = result.get("final_summary", {})
    if summary:
        print(f"  Feasibility Score: {summary.get('feasibility_score', 'N/A')}")
        print(f"  Value Propositions: {len(summary.get('value_propositions', []))} items")
        print(f"  Success Factors: {len(summary.get('success_factors', []))} items")
        print(f"  Risks & Mitigations: {len(summary.get('risks_and_mitigations', []))} items")
        print(f"  Next Steps: {len(summary.get('next_steps', []))} items")
    print()
    
    # 保存结果到文件 | Save results to file
    save_results_to_file(result)
    
    print("=" * 80)
    print("✨ LangGraph Orchestration Complete!")
    print("✨ LangGraph 编排完成！")
    print("=" * 80 + "\n")


def save_results_to_file(result: dict, filename: str = "orchestration_result.json"):
    """
    将执行结果保存到JSON文件 | Save execution results to JSON file
    
    Args:
        result: 执行结果字典 | Execution result dictionary
        filename: 文件名 | Filename (default: orchestration_result.json)
    """
    # 创建输出目录 | Create output directory if it doesn't exist
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 构建完整的文件路径 | Build full file path
    filepath = os.path.join(output_dir, filename)
    
    # 将结果保存到JSON文件 | Save results to JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        # 使用 indent 和 ensure_ascii 参数使输出更易读 | Use indent and ensure_ascii for better readability
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ Results saved to: {filepath}")
    logger.info(f"Results saved to: {filepath}")


if __name__ == "__main__":
    """
    程序入口点 | Program entry point
    """
    main()
