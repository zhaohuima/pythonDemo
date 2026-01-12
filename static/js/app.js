// 全局变量
let currentExecutionId = null;
let statusCheckInterval = null;
let eventSource = null;

// 打字机效果状态管理
const typewriterState = {};

// 进度映射
const AGENT_PROGRESS = {
    'initializing': { percent: 5, text: 'Initializing workflow...' },
    'research': { percent: 25, text: 'Product Researcher analyzing...' },
    'evaluation': { percent: 50, text: 'Feasibility Evaluator assessing...' },
    'summarization': { percent: 75, text: 'Aggregating results...' },
    'documentation': { percent: 90, text: 'Doc Assistant generating...' },
    'finished': { percent: 100, text: 'Completed!' }
};

// 开始编排流程
async function startOrchestration() {
    const userInput = document.getElementById('userInput').value.trim();
    
    if (!userInput) {
        alert('Please enter product requirements!');
        return;
    }
    
    // Disable submit button
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.querySelector('.btn-text').textContent = 'Processing...';
    
    // Show execution section and log section
    document.getElementById('executionSection').style.display = 'block';
    document.getElementById('logSection').style.display = 'block';

    // Show results section immediately with loading indicators
    document.getElementById('resultsSection').style.display = 'block';
    initializeLoadingStates();
    
    // Reset state
    resetExecutionState();
    
    // Show loading animation
    showLoading();
    
    try {
        // Send request
        const response = await fetch('/api/orchestrate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_input: userInput })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentExecutionId = data.execution_id;
            addLog('info', 'Orchestration started, Execution ID: ' + currentExecutionId);

            // Start SSE connection for streaming updates
            startSSEConnection();
        } else {
            throw new Error(data.error || 'Failed to start');
        }
    } catch (error) {
        addLog('error', 'Error: ' + error.message);
        hideLoading();
        submitBtn.disabled = false;
        submitBtn.querySelector('.btn-text').textContent = 'Start Design';
    }
}

// 开始SSE连接
function startSSEConnection() {
    if (eventSource) {
        eventSource.close();
    }

    eventSource = new EventSource(`/api/stream/${currentExecutionId}`);

    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.error) {
            addLog('error', 'Error: ' + data.error);
            eventSource.close();
            hideLoading();
            restoreSubmitButton();
            return;
        }

        if (data.done) {
            eventSource.close();
            hideLoading();
            restoreSubmitButton();
            return;
        }

        // 更新执行状态
        updateExecutionState(data);

        // 处理流式中间结果（打字机效果）
        if (data.partial_research) {
            streamTypewriter('researchResult', data.partial_research);
        }
        if (data.partial_evaluation) {
            streamTypewriter('evaluationResult', data.partial_evaluation);
        }
        if (data.partial_summary) {
            streamTypewriter('summaryResult', data.partial_summary);
            displaySummary(data.partial_summary);
        }
        if (data.partial_documentation) {
            streamTypewriter('documentationResult', data.partial_documentation);
        }

        if (data.final_result) {
            displayDetailedResults(data.final_result);
        }
    };

    eventSource.onerror = function(error) {
        console.error('SSE connection error:', error);
        eventSource.close();
        // 降级到轮询模式
        addLog('info', 'Falling back to polling mode...');
        startStatusPolling();
    };
}

// 恢复提交按钮
function restoreSubmitButton() {
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = false;
    submitBtn.querySelector('.btn-text').textContent = 'Start Design';
}

// 开始状态轮询
function startStatusPolling() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    
    statusCheckInterval = setInterval(async () => {
        if (!currentExecutionId) return;
        
        try {
            const response = await fetch(`/api/status/${currentExecutionId}`);
            const status = await response.json();
            
            updateExecutionState(status);
            
            // If completed or error, stop polling
            if (status.status === 'completed' || status.status === 'error') {
                clearInterval(statusCheckInterval);
                hideLoading();
                
                if (status.status === 'completed') {
                    await loadResults();
                } else {
                    addLog('error', 'Execution failed: ' + (status.error || 'Unknown error'));
                }
                
                // Restore submit button
                const submitBtn = document.getElementById('submitBtn');
                submitBtn.disabled = false;
                submitBtn.querySelector('.btn-text').textContent = 'Start Design';
            }
        } catch (error) {
            console.error('Status check failed:', error);
        }
    }, 1000); // Check every second
}

// 更新执行状态
function updateExecutionState(status) {
    const currentStep = status.current_step;

    // 更新进度条
    if (currentStep) {
        updateProgress(currentStep);
    }

    // 更新节点状态
    const stepMap = {
        'initializing': null,
        'research': 'research',
        'documentation': 'documentation',
        'evaluation': 'evaluation',
        'summarization': 'summarization',
        'finished': 'finished'
    };
    
    // 重置所有节点
    document.querySelectorAll('.graph-node').forEach(node => {
        node.classList.remove('active', 'completed', 'error');
    });
    
    // 更新当前步骤
    if (currentStep && stepMap[currentStep]) {
        const nodeId = `node-${stepMap[currentStep]}`;
        const node = document.getElementById(nodeId);
        if (node) {
            node.classList.add('active');
            const statusEl = node.querySelector('.node-status');
            if (statusEl) {
                statusEl.textContent = 'Running...';
            }
        }
    }
    
    // Mark completed steps
    const steps = status.steps || [];
    steps.forEach(step => {
        const stepName = step.step;
        if (stepMap[stepName]) {
            const nodeId = `node-${stepMap[stepName]}`;
            const node = document.getElementById(nodeId);
            if (node) {
                node.classList.remove('active');
                node.classList.add('completed');
                const statusEl = node.querySelector('.node-status');
                if (statusEl) {
                    statusEl.textContent = 'Completed';
                }
            }
        }
    });
    
    // 更新日志
    if (steps.length > 0) {
        const lastStep = steps[steps.length - 1];
        addLog('info', `[${lastStep.step}] ${lastStep.message}`);
    }

    // 显示中间结果（如果有）
    if (status.partial_results) {
        displayPartialResults(status.partial_results);
    }

    // 如果完成，标记所有节点
    if (status.status === 'completed') {
        document.querySelectorAll('.graph-node').forEach(node => {
            if (!node.classList.contains('start-node') && !node.classList.contains('end-node')) {
                node.classList.add('completed');
            }
        });
        document.getElementById('node-finished').classList.add('completed');
    }
}

// 加载结果
async function loadResults() {
    if (!currentExecutionId) return;
    
    try {
        const response = await fetch(`/api/result/${currentExecutionId}`);
        if (response.status === 202) {
            // Still executing
            return;
        }
        
        const result = await response.json();
        
        // Show results section
        document.getElementById('resultsSection').style.display = 'block';
        
        // Display summary information
        displaySummary(result.final_summary);
        
        // Display detailed results
        displayDetailedResults(result);
        
    } catch (error) {
        console.error('Failed to load results:', error);
        addLog('error', 'Failed to load results: ' + error.message);
    }
}

// 显示汇总信息
function displaySummary(summary) {
    const summaryEl = document.getElementById('finalSummary');
    
    if (summary && typeof summary === 'object') {
        let html = '';
        
        if (summary.feasibility_score) {
            html += `
                <div class="summary-item">
                    <span class="summary-label">Feasibility Score:</span>
                    <span class="summary-value">${summary.feasibility_score}/10</span>
                </div>
            `;
        }
        
        if (summary.value_propositions && summary.value_propositions.length > 0) {
            html += `
                <div class="summary-item" style="grid-column: 1 / -1;">
                    <span class="summary-label">Core Value Propositions:</span>
                    <ul style="margin-top: 10px; padding-left: 20px;">
                        ${summary.value_propositions.map(vp => `<li>${vp}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        if (summary.success_factors && summary.success_factors.length > 0) {
            html += `
                <div class="summary-item" style="grid-column: 1 / -1;">
                    <span class="summary-label">Key Success Factors:</span>
                    <ul style="margin-top: 10px; padding-left: 20px;">
                        ${summary.success_factors.map(sf => `<li>${sf}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        summaryEl.innerHTML = html;
    } else if (summary && summary.raw_summary) {
        summaryEl.innerHTML = `
            <div class="summary-item" style="grid-column: 1 / -1;">
                <pre style="white-space: pre-wrap; font-family: inherit;">${summary.raw_summary}</pre>
            </div>
        `;
    }
}

// 清理Markdown代码块标记
function cleanMarkdown(text) {
    if (!text) return '';
    let cleaned = String(text);
    
    // 移除开头的代码块标记（支持多行）
    cleaned = cleaned.replace(/^```(?:markdown|json|text|md)?\s*\n?/i, '');
    cleaned = cleaned.replace(/^```\s*\n?/i, '');
    
    // 移除结尾的代码块标记（支持多行和换行）
    cleaned = cleaned.replace(/\n?```\s*$/i, '');
    cleaned = cleaned.replace(/\n?```$/i, '');
    
    // 移除首尾空白，但保留内部格式
    return cleaned.trim();
}

// 格式化键名（将下划线转换为空格，首字母大写）
function formatKeyName(key) {
    return key
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ')
        .trim();
}

// 清理字符串中的 JSON/Markdown 代码块标记
function cleanJsonString(str) {
    if (typeof str !== 'string') return str;
    let cleaned = str.trim();
    // 移除开头的代码块标记
    cleaned = cleaned.replace(/^```(?:json|markdown|text|md)?\s*\n?/gi, '');
    // 移除结尾的代码块标记
    cleaned = cleaned.replace(/\n?```\s*$/gi, '');
    return cleaned.trim();
}

// 将JSON对象转换为Markdown格式
function jsonToMarkdown(obj, level = 0, parentKey = '') {
    if (obj === null || obj === undefined) return '';
    
    // 如果是字符串，检查是否是 JSON 字符串
    if (typeof obj === 'string') {
        let cleaned = cleanJsonString(obj);
        // 尝试解析为 JSON
        try {
            const parsed = JSON.parse(cleaned);
            if (typeof parsed === 'object') {
                return jsonToMarkdown(parsed, level, parentKey);
            }
        } catch (e) {
            // 不是 JSON，直接返回清理后的文本
            return cleaned + '\n\n';
        }
        return cleaned + '\n\n';
    }
    
    let markdown = '';
    
    // 根据层级选择标题级别
    const getHeading = (lvl) => {
        const headings = ['#', '##', '###', '####', '#####'];
        return headings[Math.min(lvl, headings.length - 1)];
    };
    
    if (Array.isArray(obj)) {
        obj.forEach((item, index) => {
            if (typeof item === 'object' && item !== null) {
                // 如果数组项是对象，递归处理
                const itemContent = jsonToMarkdown(item, level + 1);
                markdown += `${index + 1}. ${itemContent}\n`;
            } else {
                // 简单值直接作为列表项
                markdown += `- ${cleanJsonString(String(item))}\n`;
            }
        });
        markdown += '\n';
    } else if (typeof obj === 'object') {
        Object.keys(obj).forEach(key => {
            const value = obj[key];
            const formattedKey = formatKeyName(key);
            
            if (value === null || value === undefined) {
                return; // 跳过空值
            }
            
            if (Array.isArray(value)) {
                // 数组：作为列表显示
                markdown += `${getHeading(level + 1)} ${formattedKey}\n\n`;
                value.forEach(item => {
                    if (typeof item === 'object' && item !== null) {
                        markdown += jsonToMarkdown(item, level + 2);
                    } else {
                        markdown += `- ${cleanJsonString(String(item))}\n`;
                    }
                });
                markdown += '\n';
            } else if (typeof value === 'object') {
                // 嵌套对象：作为子章节
                markdown += `${getHeading(level + 1)} ${formattedKey}\n\n`;
                markdown += jsonToMarkdown(value, level + 1, key);
            } else {
                // 简单值：作为键值对
                const cleanedValue = cleanJsonString(String(value));
                // 如果值很长，单独一行显示
                if (cleanedValue.length > 100 || cleanedValue.includes('\n')) {
                    markdown += `**${formattedKey}**:\n\n${cleanedValue}\n\n`;
                } else {
                    markdown += `**${formattedKey}**: ${cleanedValue}\n\n`;
                }
            }
        });
    } else {
        // 基本类型
        markdown += `${obj}\n\n`;
    }
    
    return markdown;
}

// Render Markdown content
function renderMarkdown(markdownText, element) {
    if (!markdownText) {
        element.innerHTML = '<p style="color: #999;">No content available</p>';
        return;
    }
    
    // 确保是字符串类型
    let text = String(markdownText);
    
    // 清理代码块标记
    let cleaned = cleanMarkdown(text);
    
    // 使用marked.js渲染Markdown
    if (typeof marked !== 'undefined') {
        try {
            // 配置marked选项
            marked.setOptions({
                breaks: true,  // 支持换行
                gfm: true,     // GitHub风格Markdown
                sanitize: false // 允许HTML（因为我们信任内容）
            });
            element.innerHTML = marked.parse(cleaned);
        } catch (error) {
            console.error('Markdown渲染错误:', error);
            // 如果渲染失败，显示原始文本
            element.innerHTML = '<pre>' + cleaned + '</pre>';
        }
    } else {
        // 如果没有marked.js，使用简单的文本显示，但保留换行
        element.innerHTML = '<pre style="white-space: pre-wrap; font-family: inherit;">' + cleaned + '</pre>';
    }
}

// 初始化加载状态
function initializeLoadingStates() {
    document.getElementById('researchResult').innerHTML = '<p class="loading-indicator">⏳ 正在生成产品研究报告...</p>';
    document.getElementById('evaluationResult').innerHTML = '<p class="loading-indicator">⏳ 正在进行可行性评估...</p>';
    document.getElementById('summaryResult').innerHTML = '<p class="loading-indicator">⏳ 正在生成最终总结...</p>';
    document.getElementById('documentationResult').innerHTML = '<p class="loading-indicator">⏳ 正在生成产品文档...</p>';
}

// 显示中间结果（流式输出）
function displayPartialResults(partialResults) {
    if (!partialResults) return;

    // 显示 Results Section（如果还未显示）
    if (Object.keys(partialResults).some(key => partialResults[key])) {
        document.getElementById('resultsSection').style.display = 'block';
    }

    // 如果有研究结果，显示到 research tab
    if (partialResults.research) {
        const researchEl = document.getElementById('researchResult');
        renderMarkdown(jsonToMarkdown(partialResults.research), researchEl);
    }

    // 如果有评估结果，显示到 evaluation tab
    if (partialResults.evaluation) {
        const evalEl = document.getElementById('evaluationResult');
        renderMarkdown(jsonToMarkdown(partialResults.evaluation), evalEl);
    }

    // 如果有汇总结果，显示到 summary tab 和 summary card
    if (partialResults.summary) {
        displaySummary(partialResults.summary);
        const summaryEl = document.getElementById('summaryResult');
        renderMarkdown(jsonToMarkdown(partialResults.summary), summaryEl);
    }

    // 如果有文档结果，显示到 documentation tab
    if (partialResults.documentation) {
        const docEl = document.getElementById('documentationResult');
        renderMarkdown(partialResults.documentation, docEl);
    }

    // 自动切换到最新可用的 tab
    if (partialResults.documentation) {
        showTab('documentation');
    } else if (partialResults.summary) {
        showTab('summary');
    } else if (partialResults.evaluation) {
        showTab('evaluation');
    } else if (partialResults.research) {
        showTab('research');
    }
}

// 显示详细结果
function displayDetailedResults(result) {
    // 产品研究结果
    if (result.agents_outputs && result.agents_outputs.product_researcher) {
        const research = result.agents_outputs.product_researcher.research_result;
        const researchEl = document.getElementById('researchResult');
        if (typeof research === 'object') {
            // 将JSON转换为Markdown格式显示
            const markdown = jsonToMarkdown(research);
            renderMarkdown(markdown, researchEl);
        } else {
            renderMarkdown(research, researchEl);
        }
    }
    
    // 文档结果 - 确保完整显示
    if (result.agents_outputs && result.agents_outputs.doc_assistant) {
        const doc = result.agents_outputs.doc_assistant.document;
        const docEl = document.getElementById('documentationResult');
        // 清理并渲染Markdown，确保完整显示
        renderMarkdown(doc, docEl);
    }
    
    // 评估结果 - 以Markdown形式显示
    if (result.agents_outputs && result.agents_outputs.feasibility_evaluator) {
        const evalResult = result.agents_outputs.feasibility_evaluator.evaluation_result;
        const evalEl = document.getElementById('evaluationResult');
        if (typeof evalResult === 'object') {
            // 将JSON对象转换为Markdown格式
            const markdown = jsonToMarkdown(evalResult);
            renderMarkdown(markdown, evalEl);
        } else {
            // 如果已经是文本，直接渲染
            renderMarkdown(evalResult, evalEl);
        }
    }
    
    // 最终汇总 - 以Markdown形式显示
    if (result.final_summary) {
        const summaryEl = document.getElementById('summaryResult');
        if (typeof result.final_summary === 'object') {
            // 将JSON对象转换为Markdown格式
            const markdown = jsonToMarkdown(result.final_summary);
            renderMarkdown(markdown, summaryEl);
        } else {
            // 如果已经是文本，直接渲染
            renderMarkdown(result.final_summary, summaryEl);
        }
    }
}

// 显示标签页
function showTab(tabName, event) {
    // 隐藏所有标签页
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // 移除所有按钮的active类
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // 显示选中的标签页
    const targetPane = document.getElementById(`tab-${tabName}`);
    if (targetPane) {
        targetPane.classList.add('active');
    }
    
    // 激活对应的按钮
    if (event && event.target) {
        event.target.classList.add('active');
    } else {
        // 如果没有event参数，通过索引找到对应的按钮（新顺序）
        const tabNames = ['research', 'evaluation', 'summary', 'documentation'];
        const index = tabNames.indexOf(tabName);
        const buttons = document.querySelectorAll('.tab-btn');
        if (buttons[index]) {
            buttons[index].classList.add('active');
        }
    }
}

// 重置执行状态
function resetExecutionState() {
    document.querySelectorAll('.graph-node').forEach(node => {
        node.classList.remove('active', 'completed', 'error');
    });

    document.getElementById('executionLog').innerHTML = '';

    // Reset status text (new order: research -> evaluation -> summarization -> documentation)
    ['research', 'evaluation', 'summarization', 'documentation'].forEach(step => {
        const statusEl = document.getElementById(`status-${step}`);
        if (statusEl) {
            statusEl.textContent = 'Waiting';
        }
    });

    // 重置打字机状态
    Object.keys(typewriterState).forEach(key => {
        typewriterState[key] = { displayedLength: 0, fullContent: '', isTyping: false };
    });

    // 清空结果区域
    ['researchResult', 'evaluationResult', 'summaryResult', 'documentationResult'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = '';
    });
}

// 添加日志
function addLog(type, message) {
    const logContainer = document.getElementById('executionLog');
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// 显示/隐藏加载动画
function showLoading() {
    showProgress();
    // 不再显示全屏遮罩
    // document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    hideProgress();
    // document.getElementById('loadingOverlay').style.display = 'none';
}

// #region agent log - Hypothesis A: Both progressBar and floatingStatus are displayed together
// 进度条控制 - 只显示右侧底部状态条
function showProgress() {
    const progressBar = document.getElementById('progressBar');
    const floatingStatus = document.getElementById('floatingStatus');
    console.log('[DEBUG] showProgress called:', { progressBar: progressBar, floatingStatus: floatingStatus });
    fetch('http://127.0.0.1:7242/ingest/0e3ade31-f317-42f9-b791-2c3a162c0607',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:675',message:'showProgress function called',data:{progressBarExists:!!progressBar,floatingStatusExists:!!floatingStatus},timestamp:Date.now(),sessionId:'debug-session',runId:'pre-fix',hypothesisId:'A'})}).catch(()=>{});
    // 只显示右侧底部的状态条，隐藏顶部进度条
    // if (progressBar) progressBar.style.display = 'block';
    if (floatingStatus) floatingStatus.style.display = 'flex';
    fetch('http://127.0.0.1:7242/ingest/0e3ade31-f317-42f9-b791-2c3a162c0607',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:678',message:'Post-fix: Only floatingStatus displayed above results',data:{progressBarHidden:true,floatingStatusVisible:true,positionChanged:true},timestamp:Date.now(),sessionId:'debug-session',runId:'post-fix',hypothesisId:'A'})}).catch(()=>{});
    updateProgress('initializing');
}
// #endregion

// #region agent log - Hypothesis B: hideProgress hides both elements
function hideProgress() {
    console.log('[DEBUG] hideProgress called');
    fetch('http://127.0.0.1:7242/ingest/0e3ade31-f317-42f9-b791-2c3a162c0607',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:690',message:'hideProgress function called',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'pre-fix',hypothesisId:'B'})}).catch(()=>{});
    updateProgress('finished');
    setTimeout(() => {
        const progressBar = document.getElementById('progressBar');
        const floatingStatus = document.getElementById('floatingStatus');
        // 只隐藏右侧底部的状态条，保持顶部进度条隐藏
        // if (progressBar) progressBar.style.display = 'none';
        if (floatingStatus) floatingStatus.style.display = 'none';
        const progressFill = document.querySelector('.progress-bar-fill');
        if (progressFill) progressFill.style.width = '0%';
    }, 1000);
}
// #endregion

// #region agent log - Hypothesis C: progress-bar-text element also shows status
function updateProgress(step) {
    const progress = AGENT_PROGRESS[step] || AGENT_PROGRESS['initializing'];
    const progressFill = document.querySelector('.progress-bar-fill');
    const progressPercent = document.getElementById('progressPercent');
    const progressAgent = document.getElementById('progressAgent');
    const statusText = document.getElementById('statusText');

    console.log('[DEBUG] updateProgress called:', step, progress);
    fetch('http://127.0.0.1:7242/ingest/0e3ade31-f317-42f9-b791-2c3a162c0607',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:707',message:'updateProgress called',data:{step:step,progress:progress},timestamp:Date.now(),sessionId:'debug-session',runId:'pre-fix',hypothesisId:'C'})}).catch(()=>{});

    if (progressFill) progressFill.style.width = progress.percent + '%';
    if (progressPercent) progressPercent.textContent = progress.percent + '%';
    if (progressAgent) progressAgent.textContent = progress.text;
    if (statusText) statusText.textContent = progress.text;
}
// #endregion

// 打字机效果
function streamTypewriter(elementId, content) {
    const element = document.getElementById(elementId);
    if (!element) return;

    // 显示结果区域
    document.getElementById('resultsSection').style.display = 'block';

    // 初始化或获取状态
    if (!typewriterState[elementId]) {
        typewriterState[elementId] = {
            displayedLength: 0,
            fullContent: '',
            isTyping: false
        };
    }

    const state = typewriterState[elementId];

    // 处理内容：如果是对象，转换为Markdown
    let textContent;
    if (typeof content === 'object') {
        textContent = jsonToMarkdown(content);
    } else {
        textContent = String(content);
    }

    // 更新完整内容
    state.fullContent = textContent;

    // 如果已经在打字，让现有动画继续
    if (state.isTyping) return;

    // 开始打字机效果
    state.isTyping = true;
    typeNextChunk(elementId, element, state);
}

function typeNextChunk(elementId, element, state) {
    const chunkSize = 10; // 每次显示10个字符
    const delay = 20;     // 20ms间隔

    if (state.displayedLength < state.fullContent.length) {
        // 计算下一个chunk
        const nextLength = Math.min(
            state.displayedLength + chunkSize,
            state.fullContent.length
        );

        const displayText = state.fullContent.substring(0, nextLength);
        state.displayedLength = nextLength;

        // 渲染Markdown（带光标效果）
        renderMarkdownWithCursor(displayText, element, state.displayedLength < state.fullContent.length);

        // 继续下一个chunk
        setTimeout(() => typeNextChunk(elementId, element, state), delay);
    } else {
        // 打字完成
        state.isTyping = false;
        // 最终渲染（无光标）
        renderMarkdown(state.fullContent, element);
    }
}

function renderMarkdownWithCursor(text, element, showCursor) {
    // 清理并渲染Markdown
    let cleaned = cleanMarkdown(text);

    if (typeof marked !== 'undefined') {
        try {
            let html = marked.parse(cleaned);
            // 添加闪烁光标
            if (showCursor) {
                html += '<span class="typing-cursor">|</span>';
            }
            element.innerHTML = html;
        } catch (error) {
            element.innerHTML = '<pre>' + cleaned + '</pre>';
        }
    } else {
        element.innerHTML = '<pre>' + cleaned + (showCursor ? '<span class="typing-cursor">|</span>' : '') + '</pre>';
    }

    // 自动滚动到底部
    element.scrollTop = element.scrollHeight;
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 可以在这里添加初始化代码
    console.log('Product Master Web Interface Loaded');
});
