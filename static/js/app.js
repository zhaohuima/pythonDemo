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

// 字符计数器
function updateCharCount() {
    const textarea = document.getElementById('userInput');
    const counter = document.getElementById('charCounter');
    if (!textarea || !counter) return;

    const count = textarea.value.length;
    const max = textarea.maxLength || 5000;
    counter.textContent = `${count} / ${max}`;

    if (count > max * 0.9) {
        counter.classList.add('warning');
    } else {
        counter.classList.remove('warning');
    }
}

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
            // 特殊处理 evaluation，需要正确显示 citations
            const evalResult = data.partial_evaluation;
            if (typeof evalResult === 'object' && evalResult.citations && evalResult.citations.length > 0) {
                // 有 citations，使用专门的处理方式
                const evalEl = document.getElementById('evaluationResult');
                const citations = evalResult.citations;
                const evalWithoutCitations = { ...evalResult };
                delete evalWithoutCitations.citations;

                // 渲染评估结果（不含 citations）
                renderMarkdown(jsonToMarkdown(evalWithoutCitations), evalEl);

                // 追加格式化的 citations
                evalEl.innerHTML += formatCitations(citations);
            } else {
                // 没有 citations，使用普通的打字机效果
                streamTypewriter('evaluationResult', evalResult);
            }
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

/**
 * 格式化 Research 文本，将内联序号转换为 Markdown 列表
 * 支持的模式：(1), (2), (3) 以及 1., 2., 3. 等
 */
function formatResearchText(text) {
    if (!text || typeof text !== 'string') return text;

    let formatted = text;

    // ===== 处理 (1), (2), (3) 格式 =====
    // 先处理分号、逗号后的序号
    formatted = formatted.replace(/([;,])\s*\((\d+)\)\s*/g, '$1\n• ');

    // 处理冒号后的序号（特殊处理，保留冒号）
    formatted = formatted.replace(/:\s*\(1\)\s*/g, ':\n• ');

    // 处理句号后的序号
    formatted = formatted.replace(/\.\s*\((\d+)\)\s*/g, '.\n• ');

    // 处理剩余的括号序号（如 (2), (3) 等）
    formatted = formatted.replace(/\s*\((\d+)\)\s*/g, '\n• ');

    // ===== 处理 1., 2., 3. 格式（如 Market Analysis 中的竞品列表）=====
    // 匹配句号后跟空格再跟数字序号的模式，如 ". 1. " 或 ", 1. "
    formatted = formatted.replace(/([.,;])\s+(\d+)\.\s+/g, '$1\n• ');

    // 匹配文本开头或换行后的数字序号
    formatted = formatted.replace(/^(\d+)\.\s+/gm, '• ');

    // 清理多余的换行（超过2个连续换行变为2个）
    formatted = formatted.replace(/\n{3,}/g, '\n\n');

    // 确保 bullet point 格式一致
    formatted = formatted.replace(/\n•\s*/g, '\n• ');

    return formatted;
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
                // 对长文本进行格式化，将序号转换为列表
                const formattedValue = formatResearchText(cleanedValue);
                // 如果值很长或包含换行，单独一行显示
                if (formattedValue.length > 100 || formattedValue.includes('\n')) {
                    markdown += `**${formattedKey}**:\n\n${formattedValue}\n\n`;
                } else {
                    markdown += `**${formattedKey}**: ${formattedValue}\n\n`;
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

    // 如果有评估结果，显示到 evaluation tab（包含引用处理）
    if (partialResults.evaluation) {
        const evalEl = document.getElementById('evaluationResult');
        const evalResult = partialResults.evaluation;

        if (typeof evalResult === 'object') {
            // 提取引用信息
            const citations = evalResult.citations || [];

            // 创建不包含citations的评估结果副本
            const evalWithoutCitations = { ...evalResult };
            delete evalWithoutCitations.citations;

            // 渲染评估结果
            renderMarkdown(jsonToMarkdown(evalWithoutCitations), evalEl);

            // 如果有引用，追加引用部分
            if (citations.length > 0) {
                evalEl.innerHTML += formatCitations(citations);
            }
        } else {
            renderMarkdown(jsonToMarkdown(evalResult), evalEl);
        }
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

    // 评估结果 - 以Markdown形式显示，包含引用
    if (result.agents_outputs && result.agents_outputs.feasibility_evaluator) {
        const evalResult = result.agents_outputs.feasibility_evaluator.evaluation_result;
        const evalEl = document.getElementById('evaluationResult');

        let evalContent = '';
        if (typeof evalResult === 'object') {
            // 提取引用信息
            const citations = evalResult.citations || [];

            // 创建不包含citations的评估结果副本
            const evalWithoutCitations = { ...evalResult };
            delete evalWithoutCitations.citations;

            // 将JSON对象转换为Markdown格式
            evalContent = jsonToMarkdown(evalWithoutCitations);

            // 添加引用部分
            if (citations.length > 0) {
                evalContent += '\n\n' + formatCitations(citations);
            }
        } else {
            evalContent = evalResult;
        }

        // 渲染评估结果
        if (typeof evalResult === 'object') {
            const evalWithoutCitations = { ...evalResult };
            delete evalWithoutCitations.citations;
            renderMarkdown(jsonToMarkdown(evalWithoutCitations), evalEl);

            // 如果有引用，追加引用部分
            const citations = evalResult.citations || [];
            if (citations.length > 0) {
                evalEl.innerHTML += formatCitations(citations);
            }
        } else {
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

    // Initialize RAG/Knowledge Base status
    loadRAGStatus();

    // Setup file upload handler
    const pdfUpload = document.getElementById('pdfUpload');
    if (pdfUpload) {
        pdfUpload.addEventListener('change', handleFileUpload);
    }
});

// ============================================================================
// RAG / Knowledge Base Management Functions
// ============================================================================

// Load RAG status and document list
async function loadRAGStatus() {
    const statusEl = document.getElementById('ragStatus');
    const chunksEl = document.getElementById('ragChunks');
    const docsListEl = document.getElementById('documentsList');

    if (!statusEl) return;

    statusEl.textContent = 'Checking...';
    statusEl.className = 'kb-status-value loading';

    try {
        const response = await fetch('/api/rag/status');
        const data = await response.json();

        if (data.enabled) {
            statusEl.textContent = 'Enabled';
            statusEl.className = 'kb-status-value enabled';
            chunksEl.textContent = `${data.chunks_in_vector_store} chunks indexed`;

            // Display document list
            displayDocumentList(data.documents || []);
        } else {
            statusEl.textContent = 'Disabled';
            statusEl.className = 'kb-status-value disabled';
            chunksEl.textContent = '';
            docsListEl.innerHTML = '<div class="kb-empty">RAG is not enabled</div>';
        }
    } catch (error) {
        console.error('Failed to load RAG status:', error);
        statusEl.textContent = 'Error';
        statusEl.className = 'kb-status-value disabled';
    }
}

// Display document list
function displayDocumentList(documents) {
    const docsListEl = document.getElementById('documentsList');
    if (!docsListEl) return;

    if (documents.length === 0) {
        docsListEl.innerHTML = '<div class="kb-empty">No documents uploaded. Upload PDF files to enable RAG.</div>';
        return;
    }

    let html = '';
    documents.forEach(doc => {
        html += `
            <div class="kb-document-item">
                <div class="kb-document-info">
                    <span class="kb-document-icon">📄</span>
                    <span class="kb-document-name">${doc.filename}</span>
                    <span class="kb-document-size">${doc.size_mb} MB</span>
                </div>
                <button class="kb-document-delete" onclick="deleteDocument('${doc.filename}')">🗑️ Delete</button>
            </div>
        `;
    });

    docsListEl.innerHTML = html;
}

// Handle file upload
async function handleFileUpload(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    const statusEl = document.getElementById('ragStatus');
    statusEl.textContent = 'Uploading...';
    statusEl.className = 'kb-status-value loading';

    try {
        const response = await fetch('/api/documents/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.uploaded && data.uploaded.length > 0) {
            alert(`Uploaded ${data.uploaded.length} file(s) successfully!\n\nClick "Reindex" to index the new documents.`);
        }

        if (data.errors && data.errors.length > 0) {
            alert('Some files failed to upload:\n' + data.errors.join('\n'));
        }

        // Refresh status
        loadRAGStatus();

    } catch (error) {
        console.error('Upload failed:', error);
        alert('Upload failed: ' + error.message);
        loadRAGStatus();
    }

    // Clear file input
    event.target.value = '';
}

// Delete a document
async function deleteDocument(filename) {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/documents/${encodeURIComponent(filename)}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message || 'Document deleted successfully');
            loadRAGStatus();
        } else {
            alert('Failed to delete: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Delete failed:', error);
        alert('Delete failed: ' + error.message);
    }
}

// Reindex all documents
async function reindexDocuments() {
    const reindexBtn = document.querySelector('.reindex-btn');
    if (reindexBtn) {
        reindexBtn.disabled = true;
        reindexBtn.textContent = '🔄 Indexing...';
    }

    const statusEl = document.getElementById('ragStatus');
    statusEl.textContent = 'Indexing...';
    statusEl.className = 'kb-status-value loading';

    try {
        const response = await fetch('/api/documents/reindex', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.status === 'success') {
            alert(`Indexing completed!\n\nDocuments: ${data.documents_processed}\nChunks created: ${data.chunks_created}`);
        } else if (data.status === 'warning') {
            alert(data.message || 'No documents to index');
        } else {
            alert('Indexing failed: ' + (data.message || 'Unknown error'));
        }

        loadRAGStatus();

    } catch (error) {
        console.error('Reindex failed:', error);
        alert('Reindex failed: ' + error.message);
        loadRAGStatus();
    } finally {
        if (reindexBtn) {
            reindexBtn.disabled = false;
            reindexBtn.textContent = '🔄 Reindex';
        }
    }
}

// Format citations for display
function formatCitations(citations) {
    if (!citations || citations.length === 0) return '';

    let html = '<div class="citations-section"><h4>📚 References</h4>';

    citations.forEach(citation => {
        html += `
            <div class="citation-item">
                <span class="citation-number">${citation.id}</span>
                <div class="citation-details">
                    <div class="citation-document">${citation.document}</div>
                    <div class="citation-section">${citation.section}</div>
                    <div class="citation-page">Page ${citation.page}</div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    return html;
}
