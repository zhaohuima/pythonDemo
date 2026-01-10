#!/bin/bash

# Certbot 重试配置脚本
# 用于在DNS配置完成后重新运行certbot配置HTTPS

set -e

DOMAIN="productmaster.dpdns.org"
EC2_IP="13.239.2.255"

echo "🔄 Certbot 重试配置脚本"
echo "========================"
echo "域名: $DOMAIN"
echo "EC2 IP: $EC2_IP"
echo ""

# 检查是否为root或sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  此脚本需要sudo权限"
    echo "请使用: sudo bash retry_certbot.sh"
    exit 1
fi

# 步骤1: 检查DNS解析
echo "📡 步骤1: 检查DNS解析..."
DNS_IP=$(dig +short $DOMAIN 2>/dev/null | tail -n1 || echo "")

if [ -z "$DNS_IP" ]; then
    echo "❌ DNS解析失败: 无法解析域名 $DOMAIN"
    echo ""
    echo "请确保:"
    echo "1. 已在DNS服务商添加A记录:"
    echo "   主机记录: productmaster (或 @)"
    echo "   记录类型: A"
    echo "   记录值: $EC2_IP"
    echo ""
    echo "2. 已等待5-10分钟让DNS生效"
    echo ""
    echo "3. 验证DNS解析:"
    echo "   dig +short $DOMAIN"
    echo ""
    exit 1
fi

if [ "$DNS_IP" = "$EC2_IP" ]; then
    echo "✅ DNS解析正确: $DOMAIN -> $DNS_IP"
else
    echo "⚠️  DNS解析不匹配:"
    echo "   期望: $EC2_IP"
    echo "   实际: $DNS_IP"
    echo ""
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""

# 步骤2: 检查Nginx配置
echo "📝 步骤2: 检查Nginx配置..."
if ! nginx -t > /dev/null 2>&1; then
    echo "❌ Nginx配置错误"
    echo "运行 'sudo nginx -t' 查看详细错误"
    exit 1
fi

# 检查server_name是否使用域名
if ! grep -q "server_name $DOMAIN" /etc/nginx/sites-available/product-master 2>/dev/null; then
    echo "⚠️  Nginx配置中server_name未使用域名"
    echo "正在更新配置..."
    
    # 备份配置
    cp /etc/nginx/sites-available/product-master \
       /etc/nginx/sites-available/product-master.backup.$(date +%Y%m%d_%H%M%S)
    
    # 更新server_name
    sed -i "s/server_name.*;/server_name $DOMAIN;/g" /etc/nginx/sites-available/product-master
    
    # 测试并重载
    if nginx -t; then
        systemctl reload nginx
        echo "✅ Nginx配置已更新"
    else
        echo "❌ Nginx配置更新失败"
        exit 1
    fi
else
    echo "✅ Nginx配置正确"
fi

echo ""

# 步骤3: 检查端口80和443是否开放
echo "🔐 步骤3: 检查端口监听..."
if ! netstat -tlnp 2>/dev/null | grep -q ":80 "; then
    echo "⚠️  警告: 端口80未监听"
    echo "请检查Nginx是否运行: sudo systemctl status nginx"
fi

if ! netstat -tlnp 2>/dev/null | grep -q ":443 "; then
    echo "ℹ️  端口443未监听（正常，证书配置后会监听）"
fi

echo ""

# 步骤4: 检查certbot是否安装
echo "📦 步骤4: 检查certbot..."
if ! command -v certbot &> /dev/null; then
    echo "⚠️  certbot未安装，正在安装..."
    apt update
    apt install -y certbot python3-certbot-nginx
    echo "✅ certbot已安装"
else
    echo "✅ certbot已安装"
fi

echo ""

# 步骤5: 检查现有证书
echo "📜 步骤5: 检查现有证书..."
EXISTING_CERT=$(sudo certbot certificates 2>/dev/null | grep -A 2 "$DOMAIN" || echo "")

if [ -n "$EXISTING_CERT" ]; then
    echo "⚠️  发现现有证书:"
    sudo certbot certificates | grep -A 5 "$DOMAIN"
    echo ""
    read -p "是否删除现有证书并重新获取? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在删除现有证书..."
        sudo certbot delete --cert-name $DOMAIN --non-interactive || true
        echo "✅ 现有证书已删除"
    fi
fi

echo ""

# 步骤6: 运行certbot配置
echo "🔒 步骤6: 运行certbot配置SSL证书..."
echo ""
echo "使用邮箱: admin@$DOMAIN (用于证书到期提醒)"
echo ""

# 运行certbot
if certbot --nginx -d $DOMAIN \
    --non-interactive \
    --agree-tos \
    --email "admin@$DOMAIN" \
    --redirect; then
    
    echo ""
    echo "=================================="
    echo "✅ HTTPS配置成功！"
    echo ""
    
    # 验证配置
    echo "📋 验证配置..."
    if nginx -t; then
        systemctl reload nginx
        echo "✅ Nginx配置已重新加载"
    fi
    
    echo ""
    echo "📜 证书信息:"
    certbot certificates | grep -A 10 "$DOMAIN"
    
    echo ""
    echo "🎉 恭喜！您的网站现在已启用HTTPS！"
    echo ""
    echo "📋 访问测试:"
    echo "1. HTTPS: https://$DOMAIN"
    echo "   应该看到安全锁图标 ✅"
    echo ""
    echo "2. HTTP: http://$DOMAIN"
    echo "   应该自动重定向到 HTTPS ✅"
    echo ""
    echo "3. 测试自动续期:"
    echo "   sudo certbot renew --dry-run"
    
else
    echo ""
    echo "❌ Certbot配置失败"
    echo ""
    echo "可能的原因:"
    echo "1. DNS解析未生效（等待更长时间）"
    echo "2. 安全组未开放端口80"
    echo "3. Nginx配置错误"
    echo ""
    echo "查看详细日志:"
    echo "   sudo tail -f /var/log/letsencrypt/letsencrypt.log"
    echo ""
    echo "手动运行certbot:"
    echo "   sudo certbot --nginx -d $DOMAIN"
    exit 1
fi
