"""
主程序 | Main Program
演示多智能体编排系统的使用
Demonstrates the usage of the multi-agent orchestration system
"""

import json
import os
from orchestrator import ProductMaster


def main():
    """
    主函数 | Main Function
    初始化系统并运行一个示例流程
    Initialize system and run an example workflow
    """
    
    # 创建 Product Master 编排器实例 | Create Product Master Orchestrator instance
    product_master = ProductMaster()
    
    # 示例用户输入：产品需求 | Example user input: product requirement
    user_requirement = """
    我们想要开发一个针对电商企业的供应链管理系统。
    功能需求包括：
    1. 实时库存追踪和管理
    2. 供应商协作平台
    3. 订单预测和优化
    4. 成本分析和报告
    
    我们的目标是：
    - 提高供应链效率30%
    - 降低库存成本20%
    - 缩短交付周期
    - 改善供应商关系
    
    目标市场：中型电商企业（年销售额5000万-2亿）
    时间框架：6个月内上线MVP
    
    English Translation:
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
    
    # 执行编排流程 | Execute orchestration workflow
    print("\n🚀 Starting Multi-Agent Orchestration System")
    print("🚀 启动多智能体编排系统\n")
    
    # 调用 orchestrate 方法执行整个流程 | Call orchestrate method to execute entire workflow
    result = product_master.orchestrate(user_requirement)
    
    # 打印执行图和汇总信息 | Print execution graph and summary information
    product_master.print_execution_summary(result)
    
    # 保存结果到文件 | Save results to file
    save_results_to_file(result)


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
    print(f"✅ 结果已保存到：{filepath}\n")


if __name__ == "__main__":
    """
    程序入口点 | Program entry point
    当此文件被直接运行时执行主函数
    Execute main function when this file is run directly
    """
    main()
