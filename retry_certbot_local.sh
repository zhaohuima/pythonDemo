#!/bin/bash

# Certbot 重试配置脚本 - 从本地执行
# 自动SSH到EC2并运行certbot配置

set -e

DOMAIN="productmaster.dpdns.org"
EC2_IP="13.239.2.255"
EC2_USER="ubuntu"
KEY_FILE="/Users/mazhaohui/AWS 实例密钥/My Ubuntu Key -EC2_t3.micro_product master.pem"

echo "🔄 Certbot 重试配置脚本（本地执行）"
echo "===================================="
echo "域名: $DOMAIN"
echo "EC2 IP: $EC2_IP"
echo ""

# 检查密钥文件
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ 错误: 密钥文件不存在: $KEY_FILE"
    exit 1
fi

chmod 400 "$KEY_FILE"
echo "✅ 密钥文件权限已设置"
echo ""

# 步骤1: 上传retry_certbot.sh到EC2
echo "📤 步骤1: 上传脚本到EC2..."
scp -i "$KEY_FILE" \
    -o StrictHostKeyChecking=no \
    retry_certbot.sh \
    "$EC2_USER@$EC2_IP:/home/ubuntu/" || {
    echo "❌ 上传脚本失败"
    exit 1
}
echo "✅ 脚本已上传"
echo ""

# 步骤2: 在EC2上运行脚本
echo "🚀 步骤2: 在EC2上运行certbot配置..."
echo ""

ssh -i "$KEY_FILE" \
    -o StrictHostKeyChecking=no \
    "$EC2_USER@$EC2_IP" \
    "chmod +x ~/retry_certbot.sh && sudo bash ~/retry_certbot.sh" || {
    echo ""
    echo "❌ 配置失败"
    echo ""
    echo "请检查:"
    echo "1. DNS是否已配置并生效"
    echo "2. 安全组是否开放端口80和443"
    echo "3. Nginx服务是否正常运行"
    echo ""
    echo "手动SSH到EC2查看详细错误:"
    echo "  ssh -i \"$KEY_FILE\" $EC2_USER@$EC2_IP"
    echo "  sudo bash ~/retry_certbot.sh"
    exit 1
}

echo ""
echo "✅ 配置完成！"
echo ""
echo "📋 验证步骤:"
echo "1. 访问 https://$DOMAIN"
echo "2. 访问 http://$DOMAIN (应该重定向到HTTPS)"
