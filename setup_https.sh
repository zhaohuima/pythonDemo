#!/bin/bash

# HTTPS 自动配置脚本 - 方案A
# 使用 Let's Encrypt 为 EC2 上的 Nginx 配置 HTTPS

set -e

# 配置信息
DOMAIN="productmaster.dpdns.org"
EC2_IP="13.239.2.255"
EC2_USER="ubuntu"
KEY_FILE="/Users/mazhaohui/AWS 实例密钥/My Ubuntu Key -EC2_t3.micro_product master.pem"
PROJECT_DIR="/home/ubuntu/ProductMaster"  # 如果实际路径不同，请修改

echo "🔐 HTTPS 自动配置脚本 - 方案A"
echo "=============================="
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

# 步骤1: 检查DNS解析（在EC2服务器上执行）
echo "📡 步骤1: 检查DNS解析..."
echo "正在在EC2服务器上检查域名 $DOMAIN 是否指向 $EC2_IP ..."

# 测试EC2连接
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_IP" "echo '✅ EC2连接成功!'" > /dev/null 2>&1 || {
    echo "❌ 无法连接到EC2服务器"
    echo "请检查："
    echo "  1. EC2实例是否运行中"
    echo "  2. 安全组是否允许SSH (端口22)"
    echo "  3. 密钥文件路径是否正确"
    exit 1
}

# 在EC2上检查DNS
DNS_CHECK=$(ssh -i "$KEY_FILE" "$EC2_USER@$EC2_IP" "dig +short $DOMAIN 2>/dev/null | tail -n1 || echo 'FAILED'")

if [ "$DNS_CHECK" = "FAILED" ] || [ -z "$DNS_CHECK" ]; then
    echo "⚠️  警告: 无法在EC2上解析域名 $DOMAIN"
    echo ""
    echo "请确保已在DNS服务商添加A记录:"
    echo "  主机记录: productmaster (或 @)"
    echo "  记录类型: A"
    echo "  记录值: $EC2_IP"
    echo "  TTL: 默认"
    echo ""
    echo "DNS配置后可能需要5-10分钟生效"
    read -p "DNS已配置完成? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "请先配置DNS，然后重新运行此脚本"
        exit 1
    fi
else
    if [ "$DNS_CHECK" = "$EC2_IP" ]; then
        echo "✅ DNS解析正确: $DOMAIN -> $DNS_CHECK"
    else
        echo "⚠️  警告: DNS解析不匹配"
        echo "  期望: $EC2_IP"
        echo "  实际: $DNS_CHECK"
        echo ""
        echo "请检查DNS配置，确保域名指向正确的IP地址"
        read -p "是否继续? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

echo ""

# 步骤2: 测试EC2连接
echo "📡 步骤2: 测试EC2连接..."
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_IP" "echo '✅ EC2连接成功!'" || {
    echo "❌ EC2连接失败"
    exit 1
}
echo ""

# 步骤3: 更新Nginx配置使用域名
echo "📝 步骤3: 更新Nginx配置..."
echo "正在更新Nginx配置以使用域名 $DOMAIN ..."

# 创建临时配置文件
cat > /tmp/nginx_update.sh << 'NGINX_UPDATE_EOF'
#!/bin/bash
set -e

DOMAIN="productmaster.dpdns.org"
NGINX_CONFIG="/etc/nginx/sites-available/product-master"

# 备份现有配置
if [ -f "$NGINX_CONFIG" ]; then
    cp "$NGINX_CONFIG" "${NGINX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 更新server_name（如果存在）
if [ -f "$NGINX_CONFIG" ]; then
    sed -i "s/server_name.*;/server_name $DOMAIN;/g" "$NGINX_CONFIG"
    echo "✅ Nginx配置已更新"
else
    echo "⚠️  Nginx配置文件不存在，将在certbot配置时自动创建"
fi
NGINX_UPDATE_EOF

chmod +x /tmp/nginx_update.sh
scp -i "$KEY_FILE" /tmp/nginx_update.sh "$EC2_USER@$EC2_IP:/tmp/"
ssh -i "$KEY_FILE" "$EC2_USER@$EC2_IP" "sudo bash /tmp/nginx_update.sh"
rm /tmp/nginx_update.sh

echo ""

# 步骤4: 检查并安装certbot
echo "📦 步骤4: 检查并安装certbot..."
ssh -i "$KEY_FILE" "$EC2_USER@$EC2_IP" << 'CERTBOT_INSTALL'
    if ! command -v certbot &> /dev/null; then
        echo "正在安装certbot..."
        sudo apt update
        sudo apt install -y certbot python3-certbot-nginx
        echo "✅ certbot已安装"
    else
        echo "✅ certbot已安装"
    fi
CERTBOT_INSTALL

echo ""

# 步骤5: 检查安全组（提醒用户）
echo "🔐 步骤5: 检查安全组配置..."
echo ""
echo "⚠️  重要: 请确保EC2安全组已开放以下端口:"
echo "   - 端口 80 (HTTP) - 用于Let's Encrypt验证"
echo "   - 端口 443 (HTTPS) - 用于HTTPS访问"
echo ""
read -p "安全组已配置完成? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "请在AWS控制台配置安全组:"
    echo "1. 进入EC2控制台 -> 实例 -> 安全组"
    echo "2. 添加入站规则:"
    echo "   - HTTP (端口80), 来源: 0.0.0.0/0"
    echo "   - HTTPS (端口443), 来源: 0.0.0.0/0"
    echo ""
    read -p "配置完成后按回车继续..."
fi

echo ""

# 步骤6: 配置SSL证书
echo "🔒 步骤6: 配置SSL证书..."
echo "正在运行certbot配置HTTPS..."
echo ""
echo "⚠️  注意: certbot需要邮箱地址用于证书到期提醒"
echo ""

# 询问用户邮箱
read -p "请输入您的邮箱地址（用于证书到期提醒）: " USER_EMAIL
if [ -z "$USER_EMAIL" ]; then
    USER_EMAIL="admin@$DOMAIN"
    echo "使用默认邮箱: $USER_EMAIL"
fi

echo ""
echo "正在配置SSL证书..."

# 使用非交互式模式运行certbot
ssh -i "$KEY_FILE" -t "$EC2_USER@$EC2_IP" "sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $USER_EMAIL --redirect" || {
    echo ""
    echo "⚠️  自动配置可能失败，请手动运行以下命令:"
    echo "  ssh -i \"$KEY_FILE\" $EC2_USER@$EC2_IP"
    echo "  sudo certbot --nginx -d $DOMAIN"
    echo ""
    read -p "是否现在手动配置? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在打开SSH连接..."
        ssh -i "$KEY_FILE" -t "$EC2_USER@$EC2_IP" "sudo certbot --nginx -d $DOMAIN"
    else
        echo "请稍后手动运行: sudo certbot --nginx -d $DOMAIN"
        exit 1
    fi
}

echo ""

# 步骤7: 验证配置
echo "✅ 步骤7: 验证HTTPS配置..."
echo ""

# 测试Nginx配置
ssh -i "$KEY_FILE" "$EC2_USER@$EC2_IP" "sudo nginx -t" || {
    echo "❌ Nginx配置测试失败"
    exit 1
}

# 重启Nginx
ssh -i "$KEY_FILE" "$EC2_USER@$EC2_IP" "sudo systemctl restart nginx"

# 检查服务状态
ssh -i "$KEY_FILE" "$EC2_USER@$EC2_IP" "sudo systemctl status nginx --no-pager | head -n 5"

echo ""
echo "=================================="
echo "✅ HTTPS配置完成！"
echo ""
echo "📋 验证步骤:"
echo "1. 访问 https://$DOMAIN"
echo "   应该看到安全锁图标 ✅"
echo ""
echo "2. 访问 http://$DOMAIN"
echo "   应该自动重定向到 https://$DOMAIN"
echo ""
echo "3. 检查证书有效期:"
echo "   sudo certbot certificates"
echo ""
echo "4. 测试自动续期:"
echo "   sudo certbot renew --dry-run"
echo ""
echo "🎉 恭喜！您的网站现在已启用HTTPS！"
