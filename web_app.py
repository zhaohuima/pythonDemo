"""
Web应用主程序 | Web Application Main Program
提供Web界面来展示多智能体编排系统
Provides web interface to demonstrate multi-agent orchestration system
"""

import os

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
from orchestrator import ProductMaster
from datetime import datetime
import threading
import queue

app = Flask(__name__)
CORS(app)

# 存储执行状态和结果
execution_states = {}
execution_queue = queue.Queue()


class StreamingOrchestrator:
    """支持流式输出的编排器包装类"""
    
    def __init__(self, execution_id):
        self.execution_id = execution_id
        self.product_master = ProductMaster()
        self.states = {
            'status': 'idle',
            'current_step': None,
            'steps': [],
            'result': None,
            'error': None
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
        """执行编排流程，带状态更新"""
        try:
            self.update_state('running', 'initializing', 'Initializing system...')
            
            # Step 1: Product Researcher
            self.update_state('running', 'research', 'Executing product research...')
            research_result = self.product_master.researcher.research(user_input)
            self.update_state('running', 'research', 'Product research completed')
            
            # Step 2: Doc Assistant
            self.update_state('running', 'documentation', 'Generating product documentation...')
            doc_result = self.product_master.doc_assistant.generate_doc(
                user_input, 
                research_result["research_result"]
            )
            self.update_state('running', 'documentation', 'Documentation generation completed')
            
            # Step 3: Feasibility Evaluation
            self.update_state('running', 'evaluation', 'Conducting feasibility evaluation...')
            evaluation_result = self.product_master.evaluator.evaluate(
                user_input,
                research_result["research_result"],
                doc_result["document"]
            )
            self.update_state('running', 'evaluation', 'Evaluation completed')
            
            # Step 4: Summarization
            self.update_state('running', 'summarization', 'Aggregating results...')
            summary = self.product_master._summarize_results(
                user_input,
                research_result["research_result"],
                doc_result["document"],
                evaluation_result["evaluation_result"]
            )
            
            # 构建最终结果
            final_result = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "agents_outputs": {
                    "product_researcher": research_result,
                    "doc_assistant": doc_result,
                    "feasibility_evaluator": evaluation_result
                },
                "final_summary": summary,
                "status": "completed"
            }
            
            self.states['result'] = final_result
            self.update_state('completed', 'finished', 'All steps completed')
            
            # Save results to file
            output_dir = "outputs"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            filepath = os.path.join(output_dir, f"orchestration_result_{self.execution_id}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(final_result, f, indent=2, ensure_ascii=False, default=str)
            
            return final_result
            
        except Exception as e:
            self.states['error'] = str(e)
            self.update_state('error', None, f'Execution error: {str(e)}')
            raise


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


if __name__ == '__main__':
    print("\n" + "="*80)
    print("🌐 Starting Web Application Server")
    print("="*80)
    print("\nAccess URL: http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
