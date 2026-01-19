"""
Web应用主程序 | Web Application Main Program
提供Web界面来展示多智能体编排系统
Provides web interface to demonstrate multi-agent orchestration system
"""

import os

# 设置 HuggingFace 离线模式 | Set HuggingFace offline mode
# 必须在导入 sentence_transformers 之前设置 | Must be set before importing sentence_transformers
# 这样可以避免每次查询时尝试连接 huggingface.co 导致的超时问题
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

# 修复 macOS SSL 证书权限问题 | Fix macOS SSL certificate permission issue
# 必须在导入其他模块之前设置 | Must be set before importing other modules
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
except ImportError:
    pass

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import json
import time
from langgraph_orchestrator import LangGraphOrchestrator
from agents import ProductResearcher, DocAssistant, FeasibilityEvaluator, init_llm
from datetime import datetime
import threading
import queue
from logger_config import logger

# Import RAG components
from config import RAG_ENABLED, RAG_DOCUMENTS_DIR, RAG_VECTOR_DB_DIR, RAG_COLLECTION_NAME, RAG_EMBEDDING_MODEL, RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP

# Initialize RAG retriever (global instance)
rag_retriever = None
if RAG_ENABLED:
    try:
        from rag import RAGRetriever
        rag_retriever = RAGRetriever(
            documents_dir=RAG_DOCUMENTS_DIR,
            persist_directory=RAG_VECTOR_DB_DIR,
            collection_name=RAG_COLLECTION_NAME,
            embedding_model=RAG_EMBEDDING_MODEL,
            chunk_size=RAG_CHUNK_SIZE,
            chunk_overlap=RAG_CHUNK_OVERLAP
        )
        logger.info("RAG Retriever initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize RAG Retriever: {e}")
        rag_retriever = None

app = Flask(__name__)
CORS(app)

# 存储执行状态和结果
execution_states = {}
execution_queue = queue.Queue()


class StreamingOrchestrator:
    """支持流式输出的编排器包装类 - 使用 LangGraph"""
    
    # LangGraph 节点名称到前端步骤的映射（按新顺序）
    # New order: researcher -> evaluator -> aggregation -> doc_assistant
    NODE_MAPPING = {
        'researcher': {
            'step': 'research',
            'display_name': 'Product Research',
            'icon': '📚',
            'order': 1
        },
        'evaluator': {
            'step': 'evaluation',
            'display_name': 'Feasibility Evaluation',
            'icon': '🔍',
            'order': 2
        },
        'aggregation': {
            'step': 'summarization',
            'display_name': 'Result Aggregation',
            'icon': '🎯',
            'order': 3
        },
        'doc_assistant': {
            'step': 'documentation',
            'display_name': 'Documentation Generation',
            'icon': '📝',
            'order': 4
        }
    }
    
    def __init__(self, execution_id):
        self.execution_id = execution_id

        # 初始化 LLM
        logger.info(f"[{execution_id}] Initializing LLM...")
        self.llm = init_llm()

        # 初始化三个 Agent（FeasibilityEvaluator 使用 RAG）
        logger.info(f"[{execution_id}] Initializing Agents...")
        self.researcher = ProductResearcher(self.llm)
        self.doc_assistant = DocAssistant(self.llm)
        # Pass RAG retriever to FeasibilityEvaluator
        self.evaluator = FeasibilityEvaluator(self.llm, rag_retriever)

        if rag_retriever:
            logger.info(f"[{execution_id}] FeasibilityEvaluator initialized with RAG support")
        else:
            logger.info(f"[{execution_id}] FeasibilityEvaluator initialized without RAG support")

        # 创建 LangGraph 编排器
        logger.info(f"[{execution_id}] Creating LangGraph Orchestrator...")
        self.langgraph_orchestrator = LangGraphOrchestrator(
            self.researcher,
            self.doc_assistant,
            self.evaluator,
            self.llm
        )
        logger.info(f"[{execution_id}] LangGraph Orchestrator created successfully")
        
        self.states = {
            'status': 'idle',
            'current_step': None,
            'steps': [],
            'result': None,
            'error': None,
            'partial_results': {
                'research': None,
                'evaluation': None,
                'summary': None,
                'documentation': None
            }
        }
    
    def update_state(self, status, step=None, message=None):
        """更新执行状态"""
        if step:
            self.states['current_step'] = step
            if message:
                self.states['steps'].append({
                    'step': step,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                })
        self.states['status'] = status
        execution_states[self.execution_id] = self.states.copy()
    
    def orchestrate(self, user_input):
        """执行编排流程，使用 LangGraph 流式执行"""
        try:
            logger.info(f"[{self.execution_id}] Starting LangGraph orchestration")
            self.update_state('running', 'initializing', 'Initializing LangGraph workflow...')
            
            # 使用 LangGraph 流式执行工作流
            logger.info(f"[{self.execution_id}] Starting stream workflow execution")
            
            # 流式执行，实时更新状态
            final_state = None
            completed_nodes = set()
            
            # 使用 stream_workflow 执行工作流（只执行一次）
            for state_update in self.langgraph_orchestrator.stream_workflow(user_input):
                # LangGraph stream 返回格式: {'node_name': state_dict}
                if isinstance(state_update, dict):
                    for key, value in state_update.items():
                        # 检查是否是已知节点
                        if key in self.NODE_MAPPING:
                            node_info = self.NODE_MAPPING[key]
                            step_name = node_info['step']
                            display_name = node_info['display_name']

                            # 标记节点完成
                            completed_nodes.add(key)

                            # 捕获中间结果并保存到 partial_results
                            if key == 'researcher' and isinstance(value, dict):
                                self.states['partial_results']['research'] = value.get('research_result')
                            elif key == 'evaluator' and isinstance(value, dict):
                                self.states['partial_results']['evaluation'] = value.get('evaluation_result')
                            elif key == 'aggregation' and isinstance(value, dict):
                                self.states['partial_results']['summary'] = value.get('final_summary')
                            elif key == 'doc_assistant' and isinstance(value, dict):
                                self.states['partial_results']['documentation'] = value.get('document_content')

                            # 更新状态 - 节点完成
                            self.update_state(
                                'running',
                                step_name,
                                f'{display_name} completed'
                            )
                            logger.info(f"[{self.execution_id}] Node {key} ({step_name}) completed")

                            # 保存状态（每次更新都保存，最后一次就是最终状态）
                            if isinstance(value, dict):
                                final_state = value

                        # 检查是否是完整状态对象
                        elif isinstance(value, dict) and 'execution_log' in value:
                            final_state = value
            
            # 检查是否成功获取最终状态
            if final_state is None:
                raise Exception("Workflow execution failed: no final state returned")
            
            logger.info(f"[{self.execution_id}] Stream workflow completed, completed nodes: {completed_nodes}")
            
            # 从 final_state 中提取结果并构建最终结果
            logger.info(f"[{self.execution_id}] Building final result from state")
            final_result = self._build_final_result(user_input, final_state)
            
            self.states['result'] = final_result
            self.update_state('completed', 'finished', 'LangGraph workflow completed successfully')
            
            # 保存结果到文件
            self._save_results(final_result)
            
            logger.info(f"[{self.execution_id}] Orchestration completed successfully")
            return final_result
            
        except Exception as e:
            logger.error(f"[{self.execution_id}] Orchestration failed: {str(e)}", exc_info=True)
            self.states['error'] = str(e)
            self.update_state('error', None, f'LangGraph execution error: {str(e)}')
            raise
    
    def _build_final_result(self, user_input, final_state):
        """从 LangGraph 的 final_state 构建前端期望的结果格式"""
        return {
            "timestamp": final_state.get("timestamp", datetime.now().isoformat()),
            "execution_time_seconds": final_state.get("execution_time", 0),
            "user_input": user_input,
            "agents_outputs": {
                "product_researcher": {
                    "agent": "Product Researcher",
                    "research_result": final_state.get("research_result", {}),
                    "status": "completed"
                },
                "doc_assistant": {
                    "agent": "Doc Assistant",
                    "document": final_state.get("document_content", ""),
                    "status": "completed"
                },
                "feasibility_evaluator": {
                    "agent": "Feasibility Evaluator",
                    "evaluation_result": final_state.get("evaluation_result", {}),
                    "status": "completed"
                }
            },
            "final_summary": final_state.get("final_summary", {}),
            "status": "completed"
        }
    
    def _save_results(self, final_result):
        """保存结果到文件"""
        output_dir = "outputs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        filepath = os.path.join(output_dir, f"orchestration_result_{self.execution_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"[{self.execution_id}] Results saved to: {filepath}")


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/orchestrate', methods=['POST'])
def orchestrate():
    """执行编排流程的API端点"""
    try:
        data = request.json
        user_input = data.get('user_input', '')
        
        if not user_input:
            return jsonify({'error': 'User input cannot be empty'}), 400
        
        # 生成执行ID
        execution_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        
        # 创建编排器并执行
        orchestrator = StreamingOrchestrator(execution_id)
        execution_states[execution_id] = orchestrator.states
        
        # 在后台线程中执行
        def run_orchestration():
            try:
                orchestrator.orchestrate(user_input)
            except Exception as e:
                orchestrator.update_state('error', None, f'Execution failed: {str(e)}')
        
        thread = threading.Thread(target=run_orchestration)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'execution_id': execution_id,
            'status': 'started',
            'message': 'Orchestration started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<execution_id>')
def get_status(execution_id):
    """Get execution status API endpoint"""
    if execution_id not in execution_states:
        return jsonify({'error': 'Execution ID not found'}), 404
    
    state = execution_states[execution_id]
    return jsonify(state)


@app.route('/api/result/<execution_id>')
def get_result(execution_id):
    """获取执行结果的API端点"""
    if execution_id not in execution_states:
        return jsonify({'error': 'Execution ID not found'}), 404

    state = execution_states[execution_id]
    if state['status'] == 'completed' and state.get('result'):
        return jsonify(state['result'])
    elif state['status'] == 'error':
        return jsonify({'error': state.get('error', 'Unknown error')}), 500
    else:
        return jsonify({'message': 'Execution not completed yet'}), 202


@app.route('/api/stream/<execution_id>')
def stream_status(execution_id):
    """SSE流式状态推送端点"""
    def generate():
        last_partial_results = {}

        while True:
            if execution_id not in execution_states:
                yield f"data: {json.dumps({'error': 'Execution ID not found'})}\n\n"
                break

            state = execution_states[execution_id]
            current_partial = state.get('partial_results', {})

            # 构建更新数据
            update = {
                'status': state['status'],
                'current_step': state.get('current_step'),
                'steps': state.get('steps', [])
            }

            # 检查每个agent的结果是否有更新
            for key in ['research', 'evaluation', 'summary', 'documentation']:
                if current_partial.get(key) and current_partial.get(key) != last_partial_results.get(key):
                    update[f'partial_{key}'] = current_partial[key]
                    last_partial_results[key] = current_partial[key]

            yield f"data: {json.dumps(update, ensure_ascii=False, default=str)}\n\n"

            # 完成或出错时结束
            if state['status'] in ['completed', 'error']:
                if state['status'] == 'completed' and state.get('result'):
                    yield f"data: {json.dumps({'final_result': state['result']}, ensure_ascii=False, default=str)}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
                break

            time.sleep(0.5)  # 500ms检查间隔

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


# ============================================================================
# RAG Document Management API Endpoints
# ============================================================================

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all documents in the knowledge base"""
    if not rag_retriever:
        return jsonify({
            'error': 'RAG is not enabled',
            'documents': []
        }), 200

    try:
        status = rag_retriever.get_status()
        return jsonify({
            'enabled': True,
            'documents': status.get('documents', []),
            'chunks_in_vector_store': status.get('chunks_in_vector_store', 0)
        })
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """Upload PDF documents to the knowledge base"""
    if not rag_retriever:
        return jsonify({'error': 'RAG is not enabled'}), 400

    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files selected'}), 400

    uploaded = []
    errors = []

    for file in files:
        if file.filename == '':
            continue

        if not file.filename.lower().endswith('.pdf'):
            errors.append(f"{file.filename}: Not a PDF file")
            continue

        try:
            # Save file to knowledge base directory
            filepath = os.path.join(RAG_DOCUMENTS_DIR, file.filename)
            os.makedirs(RAG_DOCUMENTS_DIR, exist_ok=True)
            file.save(filepath)
            uploaded.append(file.filename)
            logger.info(f"Uploaded document: {file.filename}")
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
            logger.error(f"Error uploading {file.filename}: {e}")

    return jsonify({
        'uploaded': uploaded,
        'errors': errors,
        'message': f"Uploaded {len(uploaded)} file(s). Use /api/documents/reindex to index them."
    })


@app.route('/api/documents/<filename>', methods=['DELETE'])
def delete_document(filename):
    """Delete a document from the knowledge base"""
    if not rag_retriever:
        return jsonify({'error': 'RAG is not enabled'}), 400

    try:
        filepath = os.path.join(RAG_DOCUMENTS_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Deleted document: {filename}")
            return jsonify({
                'message': f"Deleted {filename}. Use /api/documents/reindex to update the index."
            })
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting {filename}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/documents/reindex', methods=['POST'])
def reindex_documents():
    """Rebuild the vector index from all documents"""
    if not rag_retriever:
        return jsonify({'error': 'RAG is not enabled'}), 400

    try:
        logger.info("Starting document reindexing...")
        result = rag_retriever.rebuild_index()
        logger.info(f"Reindexing completed: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error reindexing documents: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rag/status', methods=['GET'])
def rag_status():
    """Get RAG system status"""
    if not rag_retriever:
        return jsonify({
            'enabled': False,
            'message': 'RAG is not enabled'
        })

    try:
        status = rag_retriever.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting RAG status: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*80)
    print("🌐 Starting Web Application Server")
    print("="*80)
    print("\nAccess URL: http://localhost:5001")
    print("Press Ctrl+C to stop the server\n")
    app.run(debug=True, host='0.0.0.0', port=5001)
