"""
产品主人智能体 - 编排器 | Product Master Agent - Orchestrator
负责协调其他三个Agent的工作流程，并汇总输出
Responsible for orchestrating workflow of three agents and aggregating outputs
"""

import json
from typing import Any, Dict, Optional
from datetime import datetime
from agents import ProductResearcher, DocAssistant, FeasibilityEvaluator, init_llm


class ProductMaster:
    """
    产品主人编排器 | Product Master Orchestrator
    主要职责：
    1. 接收用户输入 | Receive user input
    2. 协调三个Agent的执行 | Coordinate execution of three agents
    3. 汇总所有结果 | Aggregate all results
    4. 提炼要点并输出 | Extract key points and output
    """
    
    def __init__(self):
        """
        初始化Product Master编排器 | Initialize Product Master Orchestrator
        """
        # 初始化LLM模型 | Initialize LLM model
        self.llm = init_llm()
        
        # 初始化三个Agent | Initialize three agents
        self.researcher = ProductResearcher(self.llm)
        self.doc_assistant = DocAssistant(self.llm)
        self.evaluator = FeasibilityEvaluator(self.llm)
        
        # 存储执行历史 | Store execution history
        self.execution_history = []
        
        # Agent名称 | Agent name
        self.name = "Product Master"
    
    def orchestrate(self, user_input: str) -> Dict[str, Any]:
        """
        编排整个工作流程 | Orchestrate the entire workflow
        
        Args:
            user_input: 用户的产品需求输入 | User's product requirement input
            
        Returns:
            包含最终汇总结果的字典 | Dictionary containing final aggregated results
        """
        # 记录开始时间 | Record start time
        start_time = datetime.now()
        
        print("\n" + "="*80)
        print("🚀 Product Master - Multi-Agent Orchestration System")
        print("产品主人 - 多智能体编排系统")
        print("="*80 + "\n")
        
        # 第一步：执行Product Researcher | Step 1: Execute Product Researcher
        print("📚 Step 1: Product Researcher - Conducting Market Research")
        print("第一步：产品研究员 - 进行市场调研...\n")
        
        research_result = self.researcher.research(user_input)
        print(f"✓ Product Researcher completed")
        print(f"✓ 产品研究员完成\n")
        
        # 第二步：执行Doc Assistant | Step 2: Execute Doc Assistant
        print("📝 Step 2: Doc Assistant - Generating PRD")
        print("第二步：文档助手 - 生成产品需求文档...\n")
        
        doc_result = self.doc_assistant.generate_doc(
            user_input, 
            research_result["research_result"]
        )
        print(f"✓ Doc Assistant completed")
        print(f"✓ 文档助手完成\n")
        
        # 第三步：执行Feasibility Evaluator | Step 3: Execute Feasibility Evaluator
        print("🔍 Step 3: Feasibility Evaluator - Conducting Assessment")
        print("第三步：可行性评估员 - 进行评估...\n")
        
        evaluation_result = self.evaluator.evaluate(
            user_input,
            research_result["research_result"],
            doc_result["document"]
        )
        print(f"✓ Feasibility Evaluator completed")
        print(f"✓ 可行性评估员完成\n")
        
        # 第四步：汇总和提炼 | Step 4: Aggregation and Summary
        print("🎯 Step 4: Product Master - Aggregating and Summarizing Results")
        print("第四步：产品主人 - 汇总和提炼结果...\n")
        
        summary = self._summarize_results(
            user_input,
            research_result["research_result"],
            doc_result["document"],
            evaluation_result["evaluation_result"]
        )
        
        # 记录结束时间 | Record end time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # 构建最终结果 | Build final result
        final_result = {
            "timestamp": start_time.isoformat(),
            "execution_time_seconds": round(execution_time, 2),
            "user_input": user_input,
            "agents_outputs": {
                "product_researcher": research_result,
                "doc_assistant": doc_result,
                "feasibility_evaluator": evaluation_result
            },
            "final_summary": summary,
            "status": "completed"
        }
        
        # 保存到执行历史 | Save to execution history
        self.execution_history.append(final_result)
        
        return final_result
    
    def _summarize_results(self, user_input: str, research: Dict, doc: str, evaluation: Dict) -> Dict[str, Any]:
        """
        汇总各Agent的输出，提炼关键要点 | Aggregate outputs from all agents and extract key points
        
        Args:
            user_input: 用户输入 | User input
            research: 研究结果 | Research results
            doc: 生成的文档 | Generated document
            evaluation: 评估结果 | Evaluation results
            
        Returns:
            包含关键要点的汇总 | Dictionary containing key points summary
        """
        # 构建提示词进行汇总 | Build prompt for summarization
        prompt = f"""
基于以下来自三个不同Agent的输出，请提炼核心要点和行动建议：

用户需求 | User Requirement:
{user_input}

产品研究员的调研结果 | Product Researcher's Results:
{json.dumps(research, ensure_ascii=False)}

产品文档摘要 | Document Summary:
{doc[:500]}...

可行性评估结果 | Feasibility Evaluation:
{json.dumps(evaluation, ensure_ascii=False)}

请生成一份高层次的执行摘要，包含：
1. 项目可行性评分 (1-10分) | Project Feasibility Score (1-10)
2. 核心价值主张 | Core Value Propositions
3. 关键成功因素 | Key Success Factors
4. 主要风险与缓解策略 | Key Risks and Mitigation Strategies
5. 推荐的后续步骤 | Recommended Next Steps

请以JSON格式返回，字段如下：
- feasibility_score: 可行性评分
- value_propositions: 核心价值主张（列表）
- success_factors: 关键成功因素（列表）
- risks_and_mitigations: 风险和缓解策略（列表）
- next_steps: 推荐的后续步骤（列表）

Return in JSON format as specified above.
"""
        
        # 调用LLM进行汇总 | Call LLM for summarization
        summary_response = self.llm.predict(prompt)
        
        # 尝试解析JSON | Try to parse JSON
        try:
            summary = json.loads(summary_response)
        except:
            # 如果解析失败，返回原始文本 | If parsing fails, return raw text
            summary = {
                "raw_summary": summary_response,
                "feasibility_score": "待评估 | To be evaluated",
                "value_propositions": [],
                "success_factors": [],
                "risks_and_mitigations": [],
                "next_steps": []
            }
        
        return summary
    
    def print_execution_summary(self, result: Dict[str, Any]):
        """
        打印执行的图表和汇总信息 | Print execution graph and summary information
        
        Args:
            result: 执行结果 | Execution result
        """
        print("\n" + "="*80)
        print("📊 EXECUTION GRAPH - 执行图")
        print("="*80 + "\n")
        
        # 绘制执行流程图 | Draw execution flow graph
        graph = """
        ┌─────────────────────────────────────────────────────────────┐
        │              🎯 Product Master Orchestrator                 │
        │              产品主人编排器                                 │
        └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────────────────┐
        │  User Input: Product Requirements                           │
        │  用户输入：产品需求                                         │
        └─────────────────────────────────────────────────────────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  ▼                 ▼                 ▼
        ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
        │ Product          │ │ Doc              │ │ Feasibility      │
        │ Researcher       │ │ Assistant        │ │ Evaluator        │
        │                  │ │                  │ │                  │
        │ • User Research  │ │ • PRD Document   │ │ • Tech Feasible  │
        │ • Market Analysis│ │ • Spec Design    │ │ • Architecture   │
        │ • Target Users   │ │ • Requirements   │ │ • Cost Estimate  │
        │                  │ │                  │ │ • Compliance     │
        └──────────────────┘ └──────────────────┘ └──────────────────┘
                  │                 │                 │
                  └─────────────────┼─────────────────┘
                                    ▼
        ┌─────────────────────────────────────────────────────────────┐
        │         🎯 Product Master - Aggregation & Summary           │
        │         产品主人 - 聚合与汇总                               │
        │                                                             │
        │  ✓ Feasibility Score      - 可行性评分                     │
        │  ✓ Value Propositions     - 核心价值主张                   │
        │  ✓ Success Factors        - 成功因素                       │
        │  ✓ Risk Mitigation        - 风险缓解                       │
        │  ✓ Next Steps             - 后续步骤                       │
        └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────────────────┐
        │           📤 Output to User - 输出给用户                    │
        │                                                             │
        │  Comprehensive Product Strategy Document                   │
        │  完整的产品战略文档                                         │
        └─────────────────────────────────────────────────────────────┘
        """
        
        print(graph)
        
        # 打印执行统计 | Print execution statistics
        print("\n" + "="*80)
        print("📈 EXECUTION STATISTICS - 执行统计")
        print("="*80 + "\n")
        
        print(f"⏱️  Execution Time: {result['execution_time_seconds']}s")
        print(f"⏱️  执行时间：{result['execution_time_seconds']}秒\n")
        
        print(f"✅ Status: {result['status']}")
        print(f"✅ 状态：{result['status']}\n")
        
        # 打印最终汇总 | Print final summary
        print("="*80)
        print("🎯 FINAL SUMMARY - 最终汇总")
        print("="*80 + "\n")
        
        summary = result.get('final_summary', {})
        
        if isinstance(summary, dict):
            if 'feasibility_score' in summary:
                print(f"项目可行性评分 | Feasibility Score: {summary['feasibility_score']}")
            
            if 'value_propositions' in summary:
                print(f"\n核心价值主张 | Core Value Propositions:")
                for prop in summary.get('value_propositions', []):
                    print(f"  • {prop}")
            
            if 'success_factors' in summary:
                print(f"\n关键成功因素 | Key Success Factors:")
                for factor in summary.get('success_factors', []):
                    print(f"  • {factor}")
            
            if 'risks_and_mitigations' in summary:
                print(f"\n风险与缓解策略 | Risks & Mitigation Strategies:")
                for risk in summary.get('risks_and_mitigations', []):
                    print(f"  • {risk}")
            
            if 'next_steps' in summary:
                print(f"\n推荐后续步骤 | Recommended Next Steps:")
                for step in summary.get('next_steps', []):
                    print(f"  • {step}")
        
        print("\n" + "="*80)
        print("✨ Orchestration Complete - 编排完成")
        print("="*80 + "\n")
