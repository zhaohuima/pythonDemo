"""
LangGraph 版本的多智能体编排系统 | LangGraph Version of Multi-Agent Orchestration System
使用 LangGraph 的状态图来管理Agent的执行流程
Uses LangGraph's state graph to manage the execution flow of agents
"""

from typing import TypedDict, List, Any, Dict
from datetime import datetime
import json
from langgraph.graph import StateGraph, END
from logger_config import logger, log_function_call


class OrchestratorState(TypedDict):
    """
    编排器的状态定义 | State definition for the Orchestrator
    用于在各个Agent之间传递信息
    Used to pass information between agents
    
    This TypedDict defines the state schema that flows through the LangGraph workflow.
    Each node can read from and write to this shared state.
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
    1. 使用 LangGraph StateGraph 管理工作流 | Uses LangGraph StateGraph to manage workflow
    2. 清晰的状态转移和边定义 | Clear state transitions and edge definitions
    3. 支持条件分支（可扩展）| Supports conditional branching (extensible)
    4. 便于扩展和维护 | Easy to extend and maintain
    
    重构说明 | Refactoring Notes:
    ====================
    当前实现 vs LangGraph 实现：
    
    当前实现（手动顺序调用）：
    - 手动按顺序调用节点函数
    - 状态通过函数参数传递
    - 没有图结构，无法可视化
    - 难以添加条件分支或循环
    
    LangGraph 实现（真正的图结构）：
    - 使用 StateGraph 创建有向无环图（DAG）
    - 状态自动在节点间传递
    - 可以可视化整个工作流图
    - 支持条件边、循环、并行执行
    - 更好的错误处理和检查点功能
    """
    
    def __init__(self, researcher, doc_assistant, evaluator, llm=None):
        """
        初始化 LangGraph 编排器 | Initialize LangGraph Orchestrator
        
        Args:
            researcher: 产品研究员Agent | Product Researcher Agent
            doc_assistant: 文档助手Agent | Doc Assistant Agent
            evaluator: 可行性评估员Agent | Feasibility Evaluator Agent
            llm: 语言模型实例（用于汇总）| Language model instance (for summarization)
        """
        # 存储三个Agent的实例 | Store instances of three agents
        self.researcher = researcher
        self.doc_assistant = doc_assistant
        self.evaluator = evaluator
        
        # 存储 LLM 实例用于汇总 | Store LLM instance for summarization
        if llm is None:
            from agents import init_llm
            self.llm = init_llm()
        else:
            self.llm = llm
        
        # 记录执行流程 | Record execution flow
        self.execution_flow = []
        
        # 编排器名称 | Orchestrator name
        self.name = "LangGraph Orchestrator"
        
        # 构建 LangGraph 工作流 | Build LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        构建 LangGraph 工作流图 | Build LangGraph workflow graph
        
        Returns:
            编译后的 LangGraph 应用 | Compiled LangGraph application
        """
        logger.info("Building LangGraph workflow...")
        
        # 创建状态图 | Create state graph
        workflow = StateGraph(OrchestratorState)
        logger.debug("Created StateGraph with OrchestratorState")
        
        # 添加节点到图中 | Add nodes to the graph
        # 每个节点是一个函数，接收 state 并返回更新后的 state
        logger.debug("Adding nodes to workflow...")
        workflow.add_node("researcher", self.researcher_node)
        logger.debug("  ✓ Added node: researcher")
        workflow.add_node("doc_assistant", self.doc_assistant_node)
        logger.debug("  ✓ Added node: doc_assistant")
        workflow.add_node("evaluator", self.evaluator_node)
        logger.debug("  ✓ Added node: evaluator")
        workflow.add_node("aggregation", self.aggregation_node)
        logger.debug("  ✓ Added node: aggregation")
        
        # 定义图的入口点 | Define entry point of the graph
        workflow.set_entry_point("researcher")
        logger.debug("Set entry point: researcher")
        
        # 添加边（定义节点间的连接）| Add edges (define connections between nodes)
        # 这些边定义了工作流的执行顺序
        # 新顺序: researcher -> evaluator -> aggregation -> doc_assistant
        logger.debug("Adding edges to workflow...")
        workflow.add_edge("researcher", "evaluator")
        logger.debug("  ✓ Edge: researcher -> evaluator")
        workflow.add_edge("evaluator", "aggregation")
        logger.debug("  ✓ Edge: evaluator -> aggregation")
        workflow.add_edge("aggregation", "doc_assistant")
        logger.debug("  ✓ Edge: aggregation -> doc_assistant")
        workflow.add_edge("doc_assistant", END)  # END 是 LangGraph 的特殊节点，表示工作流结束
        logger.debug("  ✓ Edge: doc_assistant -> END")
        
        # 编译图 | Compile the graph
        # 编译后会进行验证，确保图的完整性
        logger.info("Compiling workflow graph...")
        app = workflow.compile()
        logger.info("✓ Workflow graph compiled successfully")
        
        # 记录图结构 | Log graph structure
        try:
            graph = app.get_graph()
            logger.info(f"Graph nodes: {list(graph.nodes.keys())}")
            logger.info(f"Graph edges: {list(graph.edges)}")
        except Exception as e:
            logger.debug(f"Could not get graph structure: {e}")
        
        return app
    
    @log_function_call
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
        logger.info("=" * 60)
        logger.info("NODE: researcher_node - Starting execution")
        logger.debug(f"State keys: {list(state.keys())}")
        logger.debug(f"User input length: {len(state.get('user_input', ''))}")
        
        # 记录节点执行 | Log node execution
        log_message = "📚 Researcher Node: Executing product research"
        state["execution_log"].append(log_message)
        print(f"→ {log_message}")
        logger.info(log_message)
        
        # 调用研究员Agent | Call researcher agent
        logger.info("Calling ProductResearcher.research()...")
        research_result = self.researcher.research(state["user_input"])
        logger.info("✓ ProductResearcher.research() completed")
        logger.debug(f"Research result keys: {list(research_result.get('research_result', {}).keys())}")
        
        # 更新状态中的研究结果 | Update research result in state
        state["research_result"] = research_result["research_result"]
        logger.debug("Updated state['research_result']")
        
        # 记录完成 | Log completion
        completion_message = "✓ Researcher Node Completed"
        state["execution_log"].append(completion_message)
        print(f"✓ {completion_message}\n")
        logger.info(completion_message)
        logger.info("=" * 60)
        
        return state
    
    @log_function_call
    def doc_assistant_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        文档助手节点 | Doc Assistant Node
        执行产品文档生成的图节点（基于研究、评估和汇总结果）
        Graph node that executes product document generation (based on research, evaluation, and summary)
        
        Args:
            state: 当前编排器状态 | Current orchestrator state
            
        Returns:
            更新了document_content的状态 | State with updated document_content
        """
        logger.info("=" * 60)
        logger.info("NODE: doc_assistant_node - Starting execution")
        
        # 记录节点执行 | Log node execution
        log_message = "📝 Doc Assistant Node: Generating product documentation based on all results"
        state["execution_log"].append(log_message)
        print(f"→ {log_message}")
        logger.info(log_message)
        
        # 调用文档助手Agent | Call doc assistant agent
        # 注意：现在使用 research_result、evaluation_result 和 final_summary
        logger.info("Calling DocAssistant.generate_doc_with_summary()...")
        
        # 构建包含所有信息的研究结果 | Build research result with all information
        enriched_research = {
            **state["research_result"],
            "evaluation_result": state["evaluation_result"],
            "final_summary": state["final_summary"]
        }
        
        doc_result = self.doc_assistant.generate_doc(
            state["user_input"],
            enriched_research
        )
        logger.info("✓ DocAssistant.generate_doc() completed")
        
        # 更新状态中的文档内容 | Update document content in state
        state["document_content"] = doc_result["document"]
        logger.debug(f"Document length: {len(doc_result['document'])}")
        
        # 记录完成 | Log completion
        completion_message = "✓ Doc Assistant Node Completed"
        state["execution_log"].append(completion_message)
        print(f"✓ {completion_message}\n")
        logger.info(completion_message)
        logger.info("=" * 60)
        
        return state
    
    @log_function_call
    def evaluator_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        可行性评估节点 | Feasibility Evaluator Node
        执行可行性评估的图节点（基于研究结果）
        Graph node that executes feasibility evaluation (based on research results)
        
        Args:
            state: 当前编排器状态 | Current orchestrator state
            
        Returns:
            更新了evaluation_result的状态 | State with updated evaluation_result
        """
        logger.info("=" * 60)
        logger.info("NODE: evaluator_node - Starting execution")
        
        # 记录节点执行 | Log node execution
        log_message = "🔍 Evaluator Node: Conducting feasibility assessment based on research"
        state["execution_log"].append(log_message)
        print(f"→ {log_message}")
        logger.info(log_message)
        
        # 调用可行性评估Agent | Call feasibility evaluator agent
        # 注意：现在只使用 research_result，不再依赖 document_content
        logger.info("Calling FeasibilityEvaluator.evaluate()...")
        evaluation_result = self.evaluator.evaluate(
            state["user_input"],
            state["research_result"],
            ""  # 不再使用 document_content
        )
        logger.info("✓ FeasibilityEvaluator.evaluate() completed")
        
        # 更新状态中的评估结果 | Update evaluation result in state
        state["evaluation_result"] = evaluation_result["evaluation_result"]
        logger.debug(f"Evaluation keys: {list(evaluation_result['evaluation_result'].keys())}")
        
        # 记录完成 | Log completion
        completion_message = "✓ Evaluator Node Completed"
        state["execution_log"].append(completion_message)
        print(f"✓ {completion_message}\n")
        logger.info(completion_message)
        logger.info("=" * 60)
        
        return state
    
    @log_function_call
    def aggregation_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        聚合节点 | Aggregation Node
        汇总研究结果和评估结果并提炼关键点
        Aggregate research and evaluation results and extract key points
        
        Args:
            state: 当前编排器状态 | Current orchestrator state
            
        Returns:
            更新了final_summary的状态 | State with updated final_summary
        """
        logger.info("=" * 60)
        logger.info("NODE: aggregation_node - Starting execution")
        
        # 记录节点执行 | Log node execution
        log_message = "🎯 Aggregation Node: Summarizing research and evaluation results"
        state["execution_log"].append(log_message)
        print(f"→ {log_message}")
        logger.info(log_message)
        
        # 使用 LLM 进行汇总 | Use LLM for summarization
        from agents import parse_json_response
        
        # 构建汇总提示词（不再使用 document_content）| Build summarization prompt (no longer uses document_content)
        prompt = f"""
Based on the following outputs from research and evaluation, please extract key points and action recommendations:

User Requirement:
{state["user_input"]}

Product Researcher's Results:
{json.dumps(state["research_result"], ensure_ascii=False)}

Feasibility Evaluation Results:
{json.dumps(state["evaluation_result"], ensure_ascii=False)}

Please generate a high-level executive summary that includes:
1. Project Feasibility Score (1-10)
2. Core Value Propositions
3. Key Success Factors
4. Key Risks and Mitigation Strategies
5. Recommended Next Steps

Please return in JSON format with the following fields (all content must be in English):
- feasibility_score: Feasibility score (numeric value 1-10)
- value_propositions: Core value propositions (list of strings in English)
- success_factors: Key success factors (list of strings in English)
- risks_and_mitigations: Risks and mitigation strategies (list of strings in English)
- next_steps: Recommended next steps (list of strings in English)

IMPORTANT: All text content in the JSON response must be in English only.
"""
        
        # 调用 LLM 进行汇总 | Call LLM for summarization
        summary_response = self.llm.invoke(prompt)
        
        # 解析 JSON 响应 | Parse JSON response
        summary = parse_json_response(summary_response, [
            "feasibility_score", "value_propositions", "success_factors",
            "risks_and_mitigations", "next_steps"
        ])
        
        # 更新状态中的最终汇总 | Update final summary in state
        state["final_summary"] = summary
        logger.debug(f"Summary keys: {list(summary.keys())}")
        
        # 记录完成 | Log completion
        completion_message = "✓ Aggregation Node Completed"
        state["execution_log"].append(completion_message)
        print(f"✓ {completion_message}\n")
        logger.info(completion_message)
        logger.info("=" * 60)
        
        return state
    
    @log_function_call
    def execute_workflow(self, user_input: str) -> OrchestratorState:
        """
        执行完整的工作流 | Execute complete workflow
        使用 LangGraph 的 invoke 方法执行编译后的图
        Execute the compiled graph using LangGraph's invoke method
        
        Args:
            user_input: 用户的产品需求输入 | User's product requirement input
            
        Returns:
            最终的编排器状态 | Final orchestrator state
        """
        logger.info("=" * 80)
        logger.info("EXECUTING LANGGRAPH WORKFLOW")
        logger.info("=" * 80)
        
        # 创建初始状态 | Create initial state
        logger.info("Creating initial state...")
        initial_state = self.create_initial_state(user_input)
        logger.debug(f"Initial state keys: {list(initial_state.keys())}")
        
        # 记录工作流开始 | Log workflow start
        start_time = datetime.now()
        logger.info(f"Workflow started at: {start_time.isoformat()}")
        
        print("\n" + "="*80)
        print("🌐 LangGraph Orchestration Workflow")
        print("🌐 LangGraph 编排工作流")
        print("="*80 + "\n")
        
        # 使用 LangGraph 的 invoke 方法执行工作流
        # LangGraph 会自动：
        # 1. 按照定义的边顺序执行节点
        # 2. 在节点间传递状态
        # 3. 处理错误和异常
        # 4. 支持流式输出（如果使用 stream 方法）
        logger.info("Invoking LangGraph workflow...")
        logger.info("Workflow execution flow:")
        logger.info("  START -> researcher -> evaluator -> aggregation -> doc_assistant -> END")
        
        try:
            final_state = self.workflow.invoke(initial_state)
            logger.info("✓ LangGraph workflow execution completed successfully")
        except Exception as e:
            logger.error(f"✗ LangGraph workflow execution failed: {str(e)}", exc_info=True)
            raise
        
        # 计算执行时间 | Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        final_state["execution_time"] = execution_time
        logger.info(f"Workflow execution time: {execution_time:.2f} seconds")
        logger.info(f"Workflow completed at: {end_time.isoformat()}")
        logger.info("=" * 80)
        
        return final_state
    
    def stream_workflow(self, user_input: str):
        """
        流式执行工作流 | Stream workflow execution
        使用 LangGraph 的 stream 方法，可以实时看到每个节点的执行
        
        Args:
            user_input: 用户的产品需求输入 | User's product requirement input
            
        Yields:
            每个节点执行后的状态 | State after each node execution
        """
        # 创建初始状态 | Create initial state
        initial_state = self.create_initial_state(user_input)
        
        # 使用 stream 方法流式执行
        # 这会返回一个生成器，每次 yield 一个节点的执行结果
        for state in self.workflow.stream(initial_state):
            yield state
    
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
    
    def visualize_workflow_graph(self):
        """
        可视化工作流图 | Visualize workflow graph
        使用 LangGraph 的内置可视化功能
        Use LangGraph's built-in visualization capabilities
        """
        print("\n" + "="*80)
        print("📊 LangGraph Workflow Structure")
        print("📊 LangGraph 工作流结构")
        print("="*80 + "\n")
        
        # LangGraph 提供了 get_graph() 方法来获取图的表示
        # 可以用于可视化或调试
        try:
            graph = self.workflow.get_graph()
            print("Graph Nodes:", list(graph.nodes.keys()))
            print("Graph Edges:", list(graph.edges))
            print("\n")
        except:
            pass
        
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
                        │  DOC_ASSISTANT_NODE    │
                        │  • Generate Document   │
                        │  • PRD Creation        │
                        │  Output: document_     │
                        │          content       │
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
        evaluation_result  ←── Evaluator Node (uses research_result)
             ↓
        final_summary  ←── Aggregation Node (uses research_result + evaluation_result)
             ↓
        document_content  ←── Doc Assistant Node (uses all previous outputs)
        
        
        Node Dependencies - 节点依赖关系：
        ════════════════════════════════
        
        Researcher Node:
          Inputs: user_input
          Outputs: research_result
        
        Evaluator Node:
          Inputs: user_input, research_result
          Outputs: evaluation_result
        
        Aggregation Node:
          Inputs: research_result, evaluation_result
          Outputs: final_summary
        
        Doc Assistant Node:
          Inputs: user_input, research_result, evaluation_result, final_summary
          Outputs: document_content
        
        
        LangGraph Features Used - 使用的 LangGraph 特性：
        ════════════════════════════════════════════════
        
        ✅ StateGraph: 创建状态图
        ✅ add_node(): 添加节点到图
        ✅ add_edge(): 定义节点间的边
        ✅ set_entry_point(): 设置入口点
        ✅ compile(): 编译图
        ✅ invoke(): 执行工作流
        ✅ stream(): 流式执行（可选）
        """
        
        print(graph_visualization)
        print("="*80 + "\n")
