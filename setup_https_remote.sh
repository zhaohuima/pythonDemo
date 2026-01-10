#!/bin/bash

# HTTPS 配置脚本 - 在EC2服务器上直接运行
# 使用方法: 将此脚本上传到EC2，然后SSH连接后运行: sudo bash setup_https_remote.sh

set -e

DOMAIN="productmaster.dpdns.org"
EC2_IP="13.239.2.255"

echo "🔐 HTTPS 配置脚本 - 在EC2服务器上运行"
echo "========================================"
echo "域名: $DOMAIN"
echo "EC2 IP: $EC2_IP"
echo ""

# 检查是否为root或sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  此脚本需要sudo权限"
    echo "请使用: sudo bash setup_https_remote.sh"
    exit 1
fi

# 步骤1: 检查DNS解析
echo "📡 步骤1: 检查DNS解析..."
DNS_IP=$(dig +short $DOMAIN 2>/dev/null | tail -n1 || echo "")

if [ -z "$DNS_IP" ]; then
    echo "⚠️  警告: 无法解析域名 $DOMAIN"
    echo ""
    echo "请确保已在DNS服务商添加A记录:"
    echo "  主机记录: productmaster (或 @)"
    echo "  记录类型: A"
    echo "  记录值: $EC2_IP"
    echo "  TTL: 默认"
    echo ""
    # 非交互模式：如果DNS未配置，继续执行（certbot会处理）
    echo "继续执行配置（certbot会验证DNS）..."
else
    if [ "$DNS_IP" = "$EC2_IP" ]; then
        echo "✅ DNS解析正确: $DOMAIN -> $DNS_IP"
    else
        echo "⚠️  警告: DNS解析不匹配"
        echo "  期望: $EC2_IP"
        echo "  实际: $DNS_IP"
        echo ""
        read -p "是否继续? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

echo ""

# 步骤2: 检查Nginx是否安装
echo "📦 步骤2: 检查Nginx..."
if ! command -v nginx &> /dev/null; then
    echo "⚠️  Nginx未安装，正在安装..."
    apt update
    apt install -y nginx
    systemctl enable nginx
    systemctl start nginx
    echo "✅ Nginx已安装并启动"
else
    echo "✅ Nginx已安装"
fi

# 检查Nginx状态
if ! systemctl is-active --quiet nginx; then
    echo "⚠️  Nginx未运行，正在启动..."
    systemctl start nginx
fi

echo ""

# 步骤3: 更新Nginx配置使用域名
echo "📝 步骤3: 更新Nginx配置..."
NGINX_CONFIG="/etc/nginx/sites-available/product-master"

# 检查配置文件是否存在
if [ ! -f "$NGINX_CONFIG" ]; then
    echo "⚠️  Nginx配置文件不存在: $NGINX_CONFIG"
    echo "请先配置Nginx，或使用fix_nginx.sh脚本"
    echo "继续执行配置..."
else
    # 备份配置
    cp "$NGINX_CONFIG" "${NGINX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # 更新server_name
    sed -i "s/server_name.*;/server_name $DOMAIN;/g" "$NGINX_CONFIG"
    echo "✅ Nginx配置已更新为使用域名: $DOMAIN"
    
    # 测试配置
    if nginx -t; then
        systemctl reload nginx
        echo "✅ Nginx配置已重新加载"
    else
        echo "❌ Nginx配置测试失败"
        exit 1
    fi
fi

echo ""

# 步骤4: 检查并安装certbot
echo "📦 步骤4: 检查并安装certbot..."
if ! command -v certbot &> /dev/null; then
    echo "正在安装certbot..."
    apt update
    apt install -y certbot python3-certbot-nginx
    echo "✅ certbot已安装"
else
    echo "✅ certbot已安装"
fi

echo ""

# 步骤5: 检查安全组（提醒）
echo "🔐 步骤5: 安全组检查..."
echo ""
echo "⚠️  重要: 请确保EC2安全组已开放以下端口:"
echo "   - 端口 80 (HTTP) - 用于Let's Encrypt验证"
echo "   - 端口 443 (HTTPS) - 用于HTTPS访问"
echo ""
    echo ""
    echo "⚠️  请确保EC2安全组已开放端口80和443"
    echo "如果未配置，certbot验证可能会失败"
    echo ""

echo ""

# 步骤6: 配置SSL证书
echo "🔒 步骤6: 配置SSL证书..."
echo "正在运行certbot配置HTTPS..."
echo ""
echo "⚠️  注意: certbot需要邮箱地址用于证书到期提醒"
echo ""

# 使用默认邮箱（非交互模式）
USER_EMAIL="admin@${DOMAIN}"
echo "使用邮箱: $USER_EMAIL (用于证书到期提醒)"

echo ""
echo "正在配置SSL证书..."

# 运行certbot
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $USER_EMAIL --redirect || {
    echo ""
    echo "⚠️  自动配置失败，请手动运行:"
    echo "  certbot --nginx -d $DOMAIN"
    exit 1
}

echo ""

# 步骤7: 验证配置
echo "✅ 步骤7: 验证HTTPS配置..."
echo ""

# 测试Nginx配置
if nginx -t; then
    echo "✅ Nginx配置测试通过"
    systemctl restart nginx
else
    echo "❌ Nginx配置测试失败"
    exit 1
fi

# 检查服务状态
echo ""
echo "Nginx服务状态:"
systemctl status nginx --no-pager | head -n 5

# 检查证书
echo ""
echo "SSL证书信息:"
certbot certificates

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
echo "3. 测试自动续期:"
echo "   certbot renew --dry-run"
echo ""
echo "🎉 恭喜！您的网站现在已启用HTTPS！"
