# 🔧 macOS SSL 权限问题修复指南 | macOS SSL Permission Fix Guide

## 问题描述 | Problem

在 macOS 上运行程序时，可能会出现以下错误：

```
PermissionError: [Errno 1] Operation not permitted
```

这是由于 macOS 的系统级安全限制，阻止程序访问 SSL 证书文件。

## 解决方案 | Solutions

### 方案 1: 使用环境变量（推荐）

在运行程序前设置环境变量：

```bash
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE
python3 web_app.py
```

或使用一行命令：

```bash
SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())") REQUESTS_CA_BUNDLE=$SSL_CERT_FILE python3 web_app.py
```

### 方案 2: 在 shell 配置文件中永久设置

编辑 `~/.zshrc`（如果使用 zsh）或 `~/.bash_profile`（如果使用 bash）：

```bash
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE
```

然后重新加载配置：

```bash
source ~/.zshrc  # 或 source ~/.bash_profile
```

### 方案 3: 使用 conda 环境（如果有 conda）

```bash
conda create -n product_master python=3.9
conda activate product_master
pip install -r requirements.txt
```

### 方案 4: 临时禁用 SSL 验证（仅开发环境）

⚠️ **警告：仅用于开发环境，不推荐用于生产环境**

在代码中已经设置了 `verify=False` 用于 `SimpleLLM`，但 `langchain-openai` 仍然会尝试访问系统证书。

可以尝试在导入前设置：

```python
import os
os.environ['PYTHONHTTPSVERIFY'] = '0'
```

### 方案 5: 修复系统权限（需要管理员权限）

如果上述方法都不行，可以尝试修复证书权限：

```bash
# 修复证书权限
sudo chmod 644 /etc/ssl/cert.pem
sudo chown root:wheel /etc/ssl/cert.pem
```

## 当前状态 | Current Status

即使遇到 SSL 权限问题，程序仍然可以正常运行：

- ✅ **回退模式可用** - 使用 `SimpleLLM` 直接调用 API
- ✅ **所有功能正常** - DocAssistant 和 FeasibilityEvaluator 正常工作
- ✅ **ProductResearcher 可用** - 使用回退模式（直接 LLM 调用）
- ⚠️ **ReAct Agent 不可用** - 需要解决 SSL 权限问题才能使用工具

## 推荐方案 | Recommended Solution

**使用方案 1**（环境变量），这是最简单且安全的方法。

创建一个启动脚本 `start_web.sh`：

```bash
#!/bin/bash
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE
python3 web_app.py
```

然后运行：

```bash
chmod +x start_web.sh
./start_web.sh
```

## 验证修复 | Verify Fix

修复后，运行以下命令验证：

```bash
python3 -c "
import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

from langchain_openai import ChatOpenAI
print('✅ LangChain OpenAI SSL fixed!')
"
```

如果成功，应该看到 `✅ LangChain OpenAI SSL fixed!`

## 注意事项 | Notes

1. **安全性**：方案 4（禁用 SSL 验证）不安全，仅在开发环境使用
2. **权限**：方案 5 需要管理员权限，请谨慎操作
3. **环境变量**：方案 1 和 2 是推荐的方法，不影响系统安全
