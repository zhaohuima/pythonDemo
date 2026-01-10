# 🔧 安装 LangGraph ReAct Agent 依赖 | Install LangGraph ReAct Agent Dependencies

## 问题 | Problem

如果看到以下日志：
```
LangChain OpenAI not available: No module named 'langchain_openai'
LangGraph ReAct Agent not available, using fallback mode
```

这表示缺少 `langchain-openai` 依赖包。

## 解决方案 | Solution

### 方法 1: 使用 pip 安装（推荐）

```bash
pip3 install langchain-openai
```

或使用 requirements.txt：

```bash
pip3 install -r requirements.txt
```

### 方法 2: 如果遇到 SSL 权限问题

如果遇到 `Operation not permitted` SSL 错误（macOS 常见问题），尝试以下方法：

#### 选项 A: 使用 --trusted-host（临时解决）

```bash
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org langchain-openai
```

#### 选项 B: 配置 pip 使用系统证书

```bash
pip3 install --cert /etc/ssl/cert.pem langchain-openai
```

#### 选项 C: 使用 conda（如果有）

```bash
conda install -c conda-forge langchain-openai
```

#### 选项 D: 使用 pip 的 --user 标志

```bash
pip3 install --user langchain-openai
```

### 方法 3: 验证安装

安装后，运行以下命令验证：

```python
python3 -c "from langchain_openai import ChatOpenAI; print('✅ LangChain OpenAI installed successfully')"
```

## 当前状态 | Current Status

即使没有安装 `langchain-openai`，程序仍然可以正常运行：

- ✅ **回退模式可用** - 使用 `SimpleLLM` 直接调用 API
- ✅ **所有功能正常** - DocAssistant 和 FeasibilityEvaluator 正常工作
- ⚠️ **ReAct Agent 不可用** - ProductResearcher 使用回退模式（直接 LLM 调用）

## 功能对比 | Feature Comparison

| 功能 | ReAct Agent 模式 | 回退模式 |
|------|----------------|---------|
| **Product Researcher** | ✅ 使用工具和自主决策 | ✅ 直接 LLM 调用 |
| **Doc Assistant** | ✅ 正常工作 | ✅ 正常工作 |
| **Feasibility Evaluator** | ✅ 正常工作 | ✅ 正常工作 |
| **工具调用** | ✅ 支持 | ❌ 不支持 |
| **执行时间** | 可能较长（多轮交互） | 较快（单次调用） |

## 建议 | Recommendation

1. **如果需要 ReAct Agent 功能**：安装 `langchain-openai`
2. **如果只需要基本功能**：可以继续使用回退模式
3. **生产环境**：建议安装所有依赖以获得完整功能

## 安装后重启

安装完成后，**重启 Web 应用**才能使用 ReAct Agent：

```bash
# 停止当前运行的 web_app.py
# 然后重新启动
python3 web_app.py
```

---

如有问题，请查看日志文件：`logs/product_master_YYYYMMDD.log`
