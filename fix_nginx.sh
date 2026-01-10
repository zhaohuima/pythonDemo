#!/bin/bash

# Nginx配置修复脚本
# 用于修复静态文件加载和配置HTTPS

set -e

PROJECT_DIR="/home/ubuntu/ProductMaster"
NGINX_CONFIG="/etc/nginx/sites-available/product-master"
NGINX_ENABLED="/etc/nginx/sites-enabled/product-master"

echo "🔧 修复Nginx配置 - Product Master"
echo "=================================="
echo ""

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  此脚本需要sudo权限"
    echo "请使用: sudo bash fix_nginx.sh"
    exit 1
fi

# 检查Nginx是否安装
if ! command -v nginx &> /dev/null; then
    echo "📦 安装Nginx..."
    apt update
    apt install -y nginx
    echo "✅ Nginx已安装"
else
    echo "✅ Nginx已安装"
fi

# 备份现有配置
if [ -f "$NGINX_CONFIG" ]; then
    BACKUP_FILE="${NGINX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "💾 备份现有配置到: $BACKUP_FILE"
    cp "$NGINX_CONFIG" "$BACKUP_FILE"
fi

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo "⚠️  警告: 项目目录不存在: $PROJECT_DIR"
    echo "请确认项目路径是否正确"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查静态文件目录
if [ ! -d "$PROJECT_DIR/static" ]; then
    echo "⚠️  警告: 静态文件目录不存在: $PROJECT_DIR/static"
    echo "请确认项目已正确部署"
fi

# 创建Nginx配置
echo ""
echo "📝 创建Nginx配置文件..."

cat > "$NGINX_CONFIG" << 'NGINX_EOF'
# Nginx 配置文件 - Product Master
# 自动生成于: $(date)

# 限流配置（需要在 http 块中定义，如果还没有的话）
# limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
# limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

server {
    listen 80;
    server_name 13.239.2.255 _;
    
    # 日志配置
    access_log /var/log/nginx/product-master-access.log;
    error_log /var/log/nginx/product-master-error.log;
    
    # 客户端最大上传大小
    client_max_body_size 10M;
    
    # 静态文件配置 - 直接由 Nginx 提供
    location /static/ {
        alias /home/ubuntu/ProductMaster/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options "nosniff" always;
        access_log off;
        
        # 确保文件可访问
        try_files $uri =404;
    }
    
    # 主应用代理配置
    location / {
        # 代理到 Gunicorn 或 Flask 开发服务器
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 安全头
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
    
    # API 端点配置
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # API 超时设置更长
        proxy_connect_timeout 60s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        
        # CORS 头
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
    }
    
    # 健康检查端点
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
NGINX_EOF

echo "✅ Nginx配置文件已创建"

# 修复文件权限
echo ""
echo "🔐 修复文件权限..."
if [ -d "$PROJECT_DIR" ]; then
    chown -R ubuntu:www-data "$PROJECT_DIR" 2>/dev/null || chown -R ubuntu:ubuntu "$PROJECT_DIR"
    find "$PROJECT_DIR" -type d -exec chmod 755 {} \;
    find "$PROJECT_DIR" -type f -exec chmod 644 {} \;
    find "$PROJECT_DIR/static" -type f -exec chmod 644 {} \; 2>/dev/null || true
    echo "✅ 文件权限已修复"
else
    echo "⚠️  跳过权限修复（项目目录不存在）"
fi

# 启用配置
echo ""
echo "🔗 启用Nginx配置..."
ln -sf "$NGINX_CONFIG" "$NGINX_ENABLED"
echo "✅ 配置已启用"

# 检查Nginx主配置中的限流设置
echo ""
echo "🔍 检查Nginx主配置..."
if ! grep -q "limit_req_zone.*api_limit" /etc/nginx/nginx.conf 2>/dev/null; then
    echo "⚠️  注意: 需要在 /etc/nginx/nginx.conf 的 http 块中添加限流配置"
    echo "   添加以下内容到 http { ... } 块中:"
    echo "   limit_req_zone \$binary_remote_addr zone=api_limit:10m rate=10r/s;"
    echo "   limit_conn_zone \$binary_remote_addr zone=conn_limit:10m;"
fi

# 测试配置
echo ""
echo "🧪 测试Nginx配置..."
if nginx -t; then
    echo "✅ Nginx配置测试通过"
else
    echo "❌ Nginx配置测试失败，请检查错误信息"
    exit 1
fi

# 重启Nginx
echo ""
echo "🔄 重启Nginx服务..."
systemctl restart nginx
systemctl enable nginx

# 检查状态
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx服务运行正常"
else
    echo "❌ Nginx服务启动失败"
    systemctl status nginx
    exit 1
fi

# 完成
echo ""
echo "=================================="
echo "✅ 修复完成！"
echo ""
echo "📋 验证步骤："
echo "1. 访问 http://13.239.2.255/static/css/style.css"
echo "   应该能看到CSS文件内容"
echo ""
echo "2. 访问 http://13.239.2.255"
echo "   页面应该正常显示样式"
echo ""
echo "3. 检查Nginx日志："
echo "   sudo tail -f /var/log/nginx/product-master-access.log"
echo ""
echo "📚 如需配置HTTPS，请参考 FIX_STYLE_AND_SSL.md"
