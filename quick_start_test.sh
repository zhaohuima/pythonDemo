#!/bin/bash

# 一键启动测试环境
# One-Click Test Environment Launcher

echo "=========================================="
echo "Product Master - Test Environment"
echo "=========================================="
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "Setting up environment for the first time..."
    ./setup_test_env.sh
fi

# 激活虚拟环境
source venv/bin/activate

# 运行验证
echo "Verifying environment..."
./verify_test_env.sh

echo ""
echo "=========================================="
echo "Starting Web Application..."
echo "=========================================="
echo ""

# 启动服务器
./start_test_server.sh
