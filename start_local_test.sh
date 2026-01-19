#!/bin/bash

# 本地测试环境启动脚本
# Local Test Environment Startup Script

set -e

echo "🚀 启动 Product Master 本地测试环境"
echo "===================================="
echo ""

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 错误: 虚拟环境不存在"
    echo ""
    echo "请先运行设置脚本："
    echo "   ./setup_local_test.sh"
    exit 1
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate
echo "✅ 虚拟环境已激活"
echo ""

# 设置SSL证书路径（修复macOS SSL问题）
echo "🔧 配置SSL证书..."
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())" 2>/dev/null || echo "")
export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE
if [ -n "$SSL_CERT_FILE" ]; then
    echo "✅ SSL证书已配置: $SSL_CERT_FILE"
else
    echo "⚠️  警告: 无法设置SSL证书路径（可能不影响功能）"
fi
echo ""

# 检查依赖是否安装
echo "🔍 检查依赖..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ 错误: Flask未安装"
    echo ""
    echo "请先运行设置脚本："
    echo "   ./setup_local_test.sh"
    exit 1
fi
echo "✅ 依赖检查通过"
echo ""

# 显示配置信息
echo "📋 配置信息："
echo "   - Python版本: $(python3 --version)"
echo "   - Flask版本: $(python3 -c 'import flask; print(flask.__version__)' 2>/dev/null || echo '未知')"
echo "   - 工作目录: $(pwd)"
echo ""

# 启动Web服务器
echo "🌐 启动Web服务器..."
echo ""
echo "=========================================="
echo "  访问地址: http://localhost:5000"
echo "  按 Ctrl+C 停止服务器"
echo "=========================================="
echo ""

python3 web_app.py
