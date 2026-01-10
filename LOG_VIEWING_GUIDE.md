# 📋 日志查看指南 | Log Viewing Guide

## 📍 日志文件位置 | Log File Location

日志文件保存在项目根目录的 `logs/` 目录下：

```
/Users/mazhaohui/pythonDemo/logs/product_master_YYYYMMDD.log
```

例如：`logs/product_master_20260107.log`

---

## 🔍 查看日志的方法 | How to View Logs

### 方法 1: 实时查看控制台输出

运行程序时，日志会同时输出到控制台：

```bash
# 命令行模式
python3 main.py

# Web 应用模式
python3 web_app.py
```

### 方法 2: 查看日志文件

```bash
# 查看今天的日志
cat logs/product_master_$(date +%Y%m%d).log

# 实时监控日志
tail -f logs/product_master_$(date +%Y%m%d).log

# 查看最近 100 行
tail -n 100 logs/product_master_$(date +%Y%m%d).log

# 搜索特定内容
grep "NODE:" logs/product_master_*.log
grep "ERROR" logs/product_master_*.log
```

---

## 📊 日志格式 | Log Format

```
YYYY-MM-DD HH:MM:SS - LoggerName - LEVEL - [filename.py:line] - function() - message
```

示例：
```
2026-01-07 10:30:15 - ProductMaster - INFO - [langgraph_orchestrator.py:170] - researcher_node() - NODE: researcher_node - Starting execution
```

---

## 🎯 关键日志类型 | Key Log Types

### 1. LangGraph 工作流日志

```
INFO - Building LangGraph workflow...
INFO - ✓ Workflow graph compiled successfully
INFO - Graph nodes: ['__start__', 'researcher', 'doc_assistant', 'evaluator', 'aggregation', '__end__']
```

### 2. 节点执行日志

```
INFO - NODE: researcher_node - Starting execution
INFO - Calling ProductResearcher.research()...
INFO - ✓ ProductResearcher.research() completed
INFO - ✓ Researcher Node Completed
```

### 3. LLM API 调用日志

```
INFO - LLM API call attempt 1/3
INFO - ✓ LLM API call successful, response length: 2531
```

### 4. 错误日志

```
ERROR - LLM 调用失败（已重试3次）: Server disconnected
ERROR - ✗ LangGraph workflow execution failed: ...
```

---

## 🔧 日志级别 | Log Levels

| 级别 | 说明 |
|------|------|
| `DEBUG` | 详细调试信息 |
| `INFO` | 一般执行信息 |
| `WARNING` | 警告（重试等） |
| `ERROR` | 错误信息 |

---

## 🚀 快速命令 | Quick Commands

```bash
# 查看今天的日志
tail -n 50 logs/product_master_$(date +%Y%m%d).log

# 实时监控
tail -f logs/product_master_$(date +%Y%m%d).log

# 搜索错误
grep -i error logs/product_master_*.log

# 搜索节点执行
grep "NODE:" logs/product_master_*.log

# 统计日志条目
wc -l logs/product_master_*.log
```

---

## 💡 常见问题 | FAQ

**Q: 日志文件太大怎么办？**
A: 日志按天分割，可以定期清理旧日志：
```bash
find logs/ -name "*.log" -mtime +7 -delete
```

**Q: 如何修改日志级别？**
A: 编辑 `config.py` 中的 `LOG_LEVEL` 变量。
