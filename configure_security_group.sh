#!/bin/bash

# AWS EC2 安全组自动配置脚本
# 用于自动配置端口 5000 的入站规则

set -e

EC2_IP="13.239.2.255"

echo "🔐 AWS EC2 安全组配置脚本"
echo "=========================="
echo ""

# 检查 AWS CLI 是否安装
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI 未安装"
    echo ""
    echo "请先安装 AWS CLI:"
    echo "  macOS: brew install awscli"
    echo "  或访问: https://aws.amazon.com/cli/"
    echo ""
    exit 1
fi

echo "✅ AWS CLI 已安装"
echo ""

# 检查 AWS 凭证
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS 凭证未配置"
    echo ""
    echo "请先配置 AWS 凭证:"
    echo "  aws configure"
    echo ""
    echo "需要输入:"
    echo "  - AWS Access Key ID"
    echo "  - AWS Secret Access Key"
    echo "  - Default region (例如: ap-southeast-1)"
    echo "  - Default output format (json)"
    echo ""
    exit 1
fi

echo "✅ AWS 凭证已配置"
echo ""

# 获取实例信息
echo "📡 正在查找 EC2 实例..."
INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=ip-address,Values=$EC2_IP" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text 2>/dev/null)

if [ "$INSTANCE_ID" == "None" ] || [ -z "$INSTANCE_ID" ]; then
    echo "❌ 无法找到 IP 为 $EC2_IP 的实例"
    echo ""
    echo "请手动查找实例 ID，然后运行:"
    echo "  aws ec2 describe-instances --instance-ids <INSTANCE_ID>"
    exit 1
fi

echo "✅ 找到实例: $INSTANCE_ID"
echo ""

# 获取安全组 ID
echo "🔍 正在获取安全组信息..."
SECURITY_GROUP_ID=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' \
    --output text)

echo "✅ 安全组 ID: $SECURITY_GROUP_ID"
echo ""

# 检查是否已有端口 5000 的规则
echo "🔍 检查现有规则..."
EXISTING_RULE=$(aws ec2 describe-security-groups \
    --group-ids "$SECURITY_GROUP_ID" \
    --query "SecurityGroups[0].IpPermissions[?FromPort==\`5000\` && ToPort==\`5000\`]" \
    --output json)

if [ "$EXISTING_RULE" != "[]" ] && [ -n "$EXISTING_RULE" ]; then
    echo "⚠️  端口 5000 的规则已存在:"
    echo "$EXISTING_RULE" | jq '.' 2>/dev/null || echo "$EXISTING_RULE"
    echo ""
    read -p "是否要添加新规则？(y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 0
    fi
fi

# 获取用户 IP（可选）
echo ""
read -p "是否只允许您的 IP 访问？(y/n，选 n 则允许所有 IP): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📡 正在获取您的 IP 地址..."
    USER_IP=$(curl -s https://api.ipify.org 2>/dev/null || curl -s https://checkip.amazonaws.com 2>/dev/null || echo "")
    
    if [ -z "$USER_IP" ]; then
        echo "⚠️  无法自动获取 IP，请输入您的 IP 地址:"
        read -p "IP 地址: " USER_IP
    else
        echo "✅ 检测到您的 IP: $USER_IP"
    fi
    
    CIDR="${USER_IP}/32"
    DESCRIPTION="Product Master Web App - User IP"
else
    CIDR="0.0.0.0/0"
    DESCRIPTION="Product Master Web App - All IPs"
    echo "⚠️  警告: 将允许所有 IP 访问（仅用于测试）"
fi

echo ""
echo "📝 准备添加规则:"
echo "   类型: 自定义 TCP"
echo "   端口: 5000"
echo "   来源: $CIDR"
echo ""

read -p "确认添加？(y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

# 添加安全组规则
echo ""
echo "🔧 正在添加安全组规则..."
aws ec2 authorize-security-group-ingress \
    --group-id "$SECURITY_GROUP_ID" \
    --protocol tcp \
    --port 5000 \
    --cidr "$CIDR" \
    --description "$DESCRIPTION" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 安全组规则添加成功！"
    echo ""
    echo "🌐 现在可以访问: http://$EC2_IP:5000"
    echo ""
    echo "等待几秒钟让规则生效，然后刷新浏览器..."
else
    echo ""
    echo "❌ 添加规则失败"
    echo "可能是规则已存在，或权限不足"
    exit 1
fi
