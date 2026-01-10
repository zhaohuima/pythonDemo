// 全局变量
let currentExecutionId = null;
let statusCheckInterval = null;

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
    
    // Show execution section
    document.getElementById('executionSection').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    
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
            
            // Start status polling
            startStatusPolling();
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
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 可以在这里添加初始化代码
    console.log('Product Master Web Interface Loaded');
});
