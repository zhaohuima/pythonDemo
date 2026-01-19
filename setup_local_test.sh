#!/bin/bash

# 本地测试环境设置脚本
# Local Test Environment Setup Script

set -e

echo "🧪 Product Master 本地测试环境设置"
echo "===================================="
echo ""

# 检查Python版本
echo "📋 检查Python版本..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python版本: $PYTHON_VERSION"
echo ""

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
else
    echo "✅ 虚拟环境已存在"
fi
echo ""

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate
echo "✅ 虚拟环境已激活"
echo ""

# 升级pip
echo "⬆️  升级pip..."
pip install --upgrade pip --quiet
echo "✅ pip已升级"
echo ""

# 安装依赖
echo "📚 安装项目依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ 依赖安装完成"
else
    echo "⚠️  警告: requirements.txt 文件不存在"
fi
echo ""

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs outputs knowledge_base/documents vector_db/chroma_db
echo "✅ 目录创建完成"
echo ""

# 检查配置文件
echo "🔍 检查配置文件..."
if [ -f "config.py" ]; then
    echo "✅ config.py 存在"
    # 检查API密钥是否配置
    if grep -q "API_KEY = \"your-api-key\"" config.py 2>/dev/null; then
        echo "⚠️  警告: 请确保在 config.py 中配置了正确的 API_KEY"
    else
        echo "✅ API密钥已配置"
    fi
else
    echo "❌ 错误: config.py 文件不存在"
    exit 1
fi
echo ""

echo "🎉 本地测试环境设置完成！"
echo ""
echo "📋 下一步操作："
echo ""
echo "1. 启动Web服务器："
echo "   source venv/bin/activate"
echo "   python3 web_app.py"
echo ""
echo "   或者使用启动脚本："
echo "   ./start_local_test.sh"
echo ""
echo "2. 在浏览器中访问："
echo "   http://localhost:5000"
echo ""
echo "3. 测试功能："
echo "   - 输入产品需求"
echo "   - 点击 'Start Design' 按钮"
echo "   - 查看执行过程和结果"
echo ""
