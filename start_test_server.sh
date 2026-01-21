#!/bin/bash

# 测试服务器启动脚本
# Test Server Startup Script

set -e

echo "=========================================="
echo "Starting Test Server"
echo "=========================================="

# 激活虚拟环境
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run ./setup_test_env.sh first"
    exit 1
fi

source venv/bin/activate

# 检查配置
if [ ! -f "config.py" ]; then
    echo "ERROR: config.py not found!"
    exit 1
fi

# 设置环境变量
export FLASK_APP=web_app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# 显示配置信息
echo ""
echo "Configuration:"
echo "  - Flask App: web_app.py"
echo "  - Environment: development"
echo "  - Debug Mode: enabled"
echo "  - Port: 5000"
echo ""

# 启动服务器
echo "Starting Flask server..."
echo "Access the application at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python web_app.py
