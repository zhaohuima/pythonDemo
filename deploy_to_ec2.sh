#!/bin/bash

# AWS EC2 部署脚本
# 用于将 Product Master 项目部署到 EC2 实例

set -e

# 配置信息
EC2_IP="13.239.2.255"
EC2_USER="ubuntu"
KEY_FILE="/Users/mazhaohui/AWS 实例密钥/My Ubuntu Key -EC2_t3.micro_product master.pem"
PROJECT_NAME="ProductMaster"
REMOTE_DIR="/home/ubuntu/$PROJECT_NAME"

echo "🚀 开始部署 Product Master 到 AWS EC2..."
echo "=========================================="
echo "EC2 IP: $EC2_IP"
echo "用户: $EC2_USER"
echo "密钥文件: $KEY_FILE"
echo ""

# 检查密钥文件是否存在
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ 错误: 密钥文件不存在: $KEY_FILE"
    exit 1
fi

# 设置密钥文件权限
chmod 400 "$KEY_FILE"
echo "✅ 密钥文件权限已设置"

# 测试连接
echo ""
echo "📡 测试 EC2 连接..."
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_IP" "echo '✅ 连接成功!'" || {
    echo "❌ 连接失败，请检查："
    echo "   1. EC2 实例是否运行中"
    echo "   2. 安全组是否允许 SSH (端口 22)"
    echo "   3. 密钥文件路径是否正确"
    exit 1
}

# 在 EC2 上创建项目目录
echo ""
echo "📁 在 EC2 上创建项目目录..."
ssh -i "$KEY_FILE" "$EC2_USER@$EC2_IP" "mkdir -p $REMOTE_DIR"

# 同步项目文件（排除不需要的文件）
echo ""
echo "📤 同步项目文件到 EC2..."
rsync -avz --progress \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude 'logs/*' \
    --exclude 'outputs/*' \
    --exclude '.DS_Store' \
    --exclude 'venv' \
    --exclude 'env' \
    -e "ssh -i \"$KEY_FILE\" -o StrictHostKeyChecking=no" \
    ./ "$EC2_USER@$EC2_IP:$REMOTE_DIR/"

echo ""
echo "✅ 文件同步完成！"
echo ""
echo "📋 下一步操作："
echo "   1. SSH 连接到 EC2:"
echo "      ssh -i \"$KEY_FILE\" $EC2_USER@$EC2_IP"
echo ""
echo "   2. 进入项目目录:"
echo "      cd $REMOTE_DIR"
echo ""
echo "   3. 安装依赖:"
echo "      sudo apt update"
echo "      sudo apt install -y python3-pip python3-venv"
echo "      python3 -m venv venv"
echo "      source venv/bin/activate"
echo "      pip install -r requirements.txt"
echo ""
echo "   4. 配置 API 密钥（编辑 config.py）"
echo ""
echo "   5. 运行 Web 应用:"
echo "      python3 web_app.py"
echo ""
echo "   6. 或使用 systemd 服务（见 deploy_setup_ec2.sh）"
