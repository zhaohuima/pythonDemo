#!/bin/bash

# 测试环境设置脚本
# Test Environment Setup Script

set -e

echo "=========================================="
echo "Setting up Test Environment"
echo "=========================================="

# 1. 激活虚拟环境
echo "Step 1: Activating virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# 2. 升级pip
echo "Step 2: Upgrading pip..."
pip install --upgrade pip

# 3. 安装主要依赖
echo "Step 3: Installing main dependencies..."
pip install -r requirements.txt

# 4. 安装测试依赖
echo "Step 4: Installing test dependencies..."
pip install -r requirements-test.txt

# 5. 安装额外的开发工具
echo "Step 5: Installing additional development tools..."
pip install pytest pytest-cov ipython

# 6. 检查配置文件
echo "Step 6: Checking configuration..."
if [ ! -f "config.py" ]; then
    echo "ERROR: config.py not found!"
    exit 1
fi

# 7. 创建必要的目录
echo "Step 7: Creating necessary directories..."
mkdir -p logs
mkdir -p outputs
mkdir -p test_results
mkdir -p knowledge_base/documents
mkdir -p vector_db/chroma_db

# 8. 显示已安装的包
echo "Step 8: Installed packages:"
pip list | grep -E "(langgraph|langchain|flask|openai|requests)"

echo ""
echo "=========================================="
echo "Test Environment Setup Complete!"
echo "=========================================="
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the web application, run:"
echo "  ./start_test_server.sh"
echo ""
echo "To run tests, run:"
echo "  pytest"
echo ""
