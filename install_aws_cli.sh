#!/bin/bash

# AWS CLI 安装脚本

echo "🔧 AWS CLI 安装脚本"
echo "===================="
echo ""

# 检查是否已安装
if command -v aws &> /dev/null; then
    echo "✅ AWS CLI 已安装"
    aws --version
    exit 0
fi

echo "📦 正在下载 AWS CLI 安装包..."
cd /tmp

# 下载安装包
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"

if [ $? -ne 0 ]; then
    echo "❌ 下载失败，请检查网络连接"
    exit 1
fi

echo "✅ 下载完成"
echo ""
echo "🔐 需要管理员权限来安装..."
echo "   请在提示时输入您的密码"
echo ""

# 安装
sudo installer -pkg /tmp/AWSCLIV2.pkg -target /

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ AWS CLI 安装成功！"
    echo ""
    
    # 验证安装
    sleep 2
    if command -v aws &> /dev/null; then
        aws --version
        echo ""
        echo "📝 下一步：配置 AWS 凭证"
        echo "   运行: aws configure"
    else
        echo "⚠️  安装完成，但可能需要重新打开终端"
        echo "   或运行: source ~/.zshrc"
    fi
else
    echo ""
    echo "❌ 安装失败"
    exit 1
fi

# 清理
rm -f /tmp/AWSCLIV2.pkg
