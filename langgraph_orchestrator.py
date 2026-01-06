"""
LangGraph 版本的多智能体编排系统 | LangGraph Version of Multi-Agent Orchestration System
使用 LangGraph 的状态图来管理Agent的执行流程
Uses LangGraph's state graph to manage the execution flow of agents
"""

from typing import TypedDict, List, Any, Dict
from datetime import datetime
import json


class OrchestratorState(TypedDict):
    """
    编排器的状态定义 | State definition for the Orchestrator
    用于在各个Agent之间传递信息
    Used to pass information between agents
    """
    # 输入 | Inputs
    user_input: str  # 用户的初始输入 | User's initial input
    
    # 中间结果 | Intermediate results
    research_result: Dict[str, Any]  # 产品研究结果 | Product research result
    document_content: str  # 生成的文档 | Generated document
    evaluation_result: Dict[str, Any]  # 可行性评估结果 | Feasibility evaluation result
    
    # 最终结果 | Final results
    final_summary: Dict[str, Any]  # 最终汇总 | Final summary
    execution_log: List[str]  # 执行日志 | Execution log
    
    # 元数据 | Metadata
    timestamp: str  # 时间戳 | Timestamp
    execution_time: float  # 执行时间 | Execution time


class LangGraphOrchestrator:
    """
    基于 LangGraph 的编排器实现 | LangGraph-based Orchestrator Implementation
    
    主要特点：
    1. 使用状态图管理工作流 | Uses state graph to manage workflow
    2. 清晰的状态转移 | Clear state transitions
    3. 支持条件分支 | Supports conditional branching
    4. 便于扩展 | Easy to extend
    """
    
    def __init__(self, researcher, doc_assistant, evaluator):
        """
        初始化 LangGraph 编排器 | Initialize LangGraph Orchestrator
        
        Args:
            researcher: 产品研究员Agent | Product Researcher Agent
            doc_assistant: 文档助手Agent | Doc Assistant Agent
            evaluator: 可行性评估员Agent | Feasibility Evaluator Agent
        """
        # 存储三个Agent的实例 | Store instances of three agents
        self.researcher = researcher
        self.doc_assistant = doc_assistant
        self.evaluator = evaluator
        
        # 记录执行流程 | Record execution flow
        self.execution_flow = []
        
        # 编排器名称 | Orchestrator name
        self.name = "LangGraph Orchestrator"
    
    def create_initial_state(self, user_input: str) -> OrchestratorState:
        """
        创建初始状态 | Create initial state
        
        Args:
            user_input: 用户的产品需求输入 | User's product requirement input
            
        Returns:
            初始化的编排器状态 | Initialized orchestrator state
        """
        # 创建初始状态字典 | Create initial state dictionary
        initial_state: OrchestratorState = {
            "user_input": user_input,  # 用户输入 | User input
            "research_result": {},  # 初始化为空 | Initialize as empty
            "document_content": "",  # 初始化为空 | Initialize as empty
            "evaluation_result": {},  # 初始化为空 | Initialize as empty
            "final_summary": {},  # 初始化为空 | Initialize as empty
            "execution_log": [],  # 初始化为空日志列表 | Initialize as empty log list
            "timestamp": datetime.now().isoformat(),  # 记录时间戳 | Record timestamp
            "execution_time": 0.0  # 执行时间 | Execution time
        }
        
        return initial_state
    
    def researcher_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        研究员节点 | Researcher Node
        执行产品研究的图节点
        Graph node that executes product research
        
        Args:
            state: 当前编排器状态 | Current orchestrator state
            
        Returns:
            更新了research_result的状态 | State with updated research_result
        """
        # 记录节点执行 | Log node execution
        log_message = "📚 Researcher Node: Executing product research"
        state["execution_log"].append(log_message)
        print(f"→ {log_message}")
        print(f"→ 研究员节点：执行产品研究\n")
        
        # 调用研究员Agent | Call researcher agent
        research_result = self.researcher.research(state["user_input"])
        
        # 更新状态中的研究结果 | Update research result in state
        state["research_result"] = research_result["research_result"]
        
        # 记录完成 | Log completion
        completion_message = "✓ Researcher Node Completed"
        state["execution_log"].append(completion_message)
        print(f"✓ {completion_message}")
        print(f"✓ 研究员节点完成\n")
        
        return state
    
    def doc_assistant_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        文档助手节点 | Doc Assistant Node
        执行产品文档生成的图节点
        Graph node that executes product document generation
        
        Args:
            state: 当前编排器状态 | Current orchestrator state
            
        Returns:
            更新了document_content的状态 | State with updated document_content
        """
        # 记录节点执行 | Log node execution
        log_message = "📝 Doc Assistant Node: Generating product documentation"
        state["execution_log"].append(log_message)
        print(f"→ {log_message}")
        print(f"→ 文档助手节点：生成产品文档\n")
        
        # 调用文档助手Agent | Call doc assistant agent
        doc_result = self.doc_assistant.generate_doc(
            state["user_input"],
            state["research_result"]
        )
        
        # 更新状态中的文档内容 | Update document content in state
        state["document_content"] = doc_result["document"]
        
        # 记录完成 | Log completion
        completion_message = "✓ Doc Assistant Node Completed"
        state["execution_log"].append(completion_message)
        print(f"✓ {completion_message}")
        print(f"✓ 文档助手节点完成\n")
        
        return state
    
    def evaluator_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        可行性评估节点 | Feasibility Evaluator Node
        执行可行性评估的图节点
        Graph node that executes feasibility evaluation
        
        Args:
            state: 当前编排器状态 | Current orchestrator state
            
        Returns:
            更新了evaluation_result的状态 | State with updated evaluation_result
        """
        # 记录节点执行 | Log node execution
        log_message = "🔍 Evaluator Node: Conducting feasibility assessment"
        state["execution_log"].append(log_message)
        print(f"→ {log_message}")
        print(f"→ 评估员节点：执行可行性评估\n")
        
        # 调用可行性评估Agent | Call feasibility evaluator agent
        evaluation_result = self.evaluator.evaluate(
            state["user_input"],
            state["research_result"],
            state["document_content"]
        )
        
        # 更新状态中的评估结果 | Update evaluation result in state
        state["evaluation_result"] = evaluation_result["evaluation_result"]
        
        # 记录完成 | Log completion
        completion_message = "✓ Evaluator Node Completed"
        state["execution_log"].append(completion_message)
        print(f"✓ {completion_message}")
        print(f"✓ 评估员节点完成\n")
        
        return state
    
    def aggregation_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        聚合节点 | Aggregation Node
        汇总所有Agent的输出并提炼关键点
        Aggregate outputs from all agents and extract key points
        
        Args:
            state: 当前编排器状态 | Current orchestrator state
            
        Returns:
            更新了final_summary的状态 | State with updated final_summary
        """
        # 记录节点执行 | Log node execution
        log_message = "🎯 Aggregation Node: Summarizing and synthesizing results"
        state["execution_log"].append(log_message)
        print(f"→ {log_message}")
        print(f"→ 聚合节点：总结和综合结果\n")
        
        # 简单的汇总逻辑（在实际应用中，这里会调用LLM进行更复杂的处理）
        # Simple summarization logic (in real applications, this would call LLM for more complex processing)
        state["final_summary"] = {
            "research_conducted": bool(state["research_result"]),  # 是否完成了研究 | Whether research was conducted
            "document_generated": bool(state["document_content"]),  # 是否生成了文档 | Whether document was generated
            "evaluation_completed": bool(state["evaluation_result"]),  # 是否完成了评估 | Whether evaluation was completed
            "total_steps": len(state["execution_log"]),  # 执行步骤总数 | Total execution steps
            "status": "success" if all([
                state["research_result"],
                state["document_content"],
                state["evaluation_result"]
            ]) else "incomplete"  # 整体状态 | Overall status
        }
        
        # 记录完成 | Log completion
        completion_message = "✓ Aggregation Node Completed"
        state["execution_log"].append(completion_message)
        print(f"✓ {completion_message}")
        print(f"✓ 聚合节点完成\n")
        
        return state
    
    def execute_workflow(self, user_input: str) -> OrchestratorState:
        """
        执行完整的工作流 | Execute complete workflow
        按顺序执行所有节点，形成一个有向无环图 (DAG)
        Execute all nodes in sequence, forming a directed acyclic graph (DAG)
        
        Args:
            user_input: 用户的产品需求输入 | User's product requirement input
            
        Returns:
            最终的编排器状态 | Final orchestrator state
        """
        # 创建初始状态 | Create initial state
        state = self.create_initial_state(user_input)
        
        # 记录工作流开始 | Log workflow start
        start_time = datetime.now()
        
        print("\n" + "="*80)
        print("🌐 LangGraph Orchestration Workflow")
        print("🌐 LangGraph 编排工作流")
        print("="*80 + "\n")
        
        # 执行节点序列 | Execute node sequence
        # 节点1：产品研究员 | Node 1: Product Researcher
        state = self.researcher_node(state)
        
        # 节点2：文档助手 | Node 2: Doc Assistant
        state = self.doc_assistant_node(state)
        
        # 节点3：可行性评估员 | Node 3: Feasibility Evaluator
        state = self.evaluator_node(state)
        
        # 节点4：结果聚合 | Node 4: Result Aggregation
        state = self.aggregation_node(state)
        
        # 计算执行时间 | Calculate execution time
        end_time = datetime.now()
        state["execution_time"] = (end_time - start_time).total_seconds()
        
        return state
    
    def visualize_workflow_graph(self):
        """
        可视化工作流图 | Visualize workflow graph
        打印LangGraph的工作流结构
        Print the structure of the LangGraph workflow
        """
        print("\n" + "="*80)
        print("📊 LangGraph Workflow Structure - LangGraph工作流结构")
        print("="*80 + "\n")
        
        # 绘制工作流图 | Draw workflow graph
        graph_visualization = """
        ╔═════════════════════════════════════════════════════════════════════════╗
        ║                    LangGraph Orchestration Flow                         ║
        ║                    LangGraph 编排工作流                                 ║
        ╚═════════════════════════════════════════════════════════════════════════╝
        
                                    START
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │   INPUT STATE          │
                        │  (user_input)          │
                        └────────────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │  RESEARCHER_NODE       │
                        │  • Conduct Research    │
                        │  • Market Analysis     │
                        │  Output: research_     │
                        │           result       │
                        └────────────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │  DOC_ASSISTANT_NODE    │
                        │  • Generate Document   │
                        │  • PRD Creation        │
                        │  Output: document_     │
                        │          content       │
                        └────────────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │  EVALUATOR_NODE        │
                        │  • Feasibility Check   │
                        │  • Risk Assessment     │
                        │  Output: evaluation_   │
                        │          result        │
                        └────────────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │  AGGREGATION_NODE      │
                        │  • Summarize Results   │
                        │  • Synthesize Output   │
                        │  Output: final_        │
                        │          summary       │
                        └────────────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │   FINAL STATE          │
                        │  (all outputs)         │
                        └────────────────────────┘
                                     │
                                     ▼
                                    END
        
        
        State Flow Diagram - 状态流图：
        ════════════════════════════════
        
        user_input
             ↓
        research_result  ←── Researcher Node
             ↓
        document_content  ←── Doc Assistant Node (uses research_result)
             ↓
        evaluation_result  ←── Evaluator Node (uses research_result + document_content)
             ↓
        final_summary  ←── Aggregation Node (uses all previous outputs)
        
        
        Node Dependencies - 节点依赖关系：
        ════════════════════════════════
        
        Researcher Node:
          Inputs: user_input
          Outputs: research_result
        
        Doc Assistant Node:
          Inputs: user_input, research_result
          Outputs: document_content
        
        Evaluator Node:
          Inputs: user_input, research_result, document_content
          Outputs: evaluation_result
        
        Aggregation Node:
          Inputs: research_result, document_content, evaluation_result
          Outputs: final_summary
        """
        
        print(graph_visualization)
        print("="*80 + "\n")
