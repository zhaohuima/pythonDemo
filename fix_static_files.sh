#!/bin/bash

# 修复静态文件访问问题的脚本
# 在EC2服务器上运行

set -e

echo "🔧 修复静态文件访问问题"
echo "========================"

# 检查是否为root或sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  此脚本需要sudo权限"
    echo "请使用: sudo bash fix_static_files.sh"
    exit 1
fi

NGINX_CONFIG="/etc/nginx/sites-available/product-master"
STATIC_DIR="/home/ubuntu/ProductMaster/static"

echo ""
echo "📝 步骤1: 备份Nginx配置..."
cp "$NGINX_CONFIG" "${NGINX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
echo "✅ 配置已备份"

echo ""
echo "📝 步骤2: 更新静态文件配置..."

# 创建临时配置文件
cat > /tmp/static_location.conf << 'EOF'
    location /static/ {
        alias /home/ubuntu/ProductMaster/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options "nosniff" always;
        access_log off;
        try_files $uri =404;
    }
EOF

# 使用Python更新配置
python3 << PYTHON_EOF
import re

config_file = "$NGINX_CONFIG"
static_config = """    location /static/ {
        alias /home/ubuntu/ProductMaster/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options "nosniff" always;
        access_log off;
        try_files \$uri =404;
    }"""

with open(config_file, 'r') as f:
    content = f.read()

# 替换静态文件配置
pattern = r'location /static/ \{[^}]*\}'
if re.search(pattern, content):
    content = re.sub(pattern, static_config, content)
    with open(config_file, 'w') as f:
        f.write(content)
    print("✅ 静态文件配置已更新")
else:
    # 如果没有找到，在server块中添加
    content = content.replace(
        '    # 静态文件缓存',
        '    # 静态文件缓存\n' + static_config
    )
    with open(config_file, 'w') as f:
        f.write(content)
    print("✅ 静态文件配置已添加")
PYTHON_EOF

echo ""
echo "🔐 步骤3: 修复文件权限..."
chmod -R 755 /home/ubuntu
chmod -R 755 /home/ubuntu/ProductMaster
chmod -R 755 "$STATIC_DIR"
chown -R ubuntu:www-data "$STATIC_DIR"
echo "✅ 文件权限已修复"

echo ""
echo "🧪 步骤4: 测试Nginx配置..."
if nginx -t; then
    echo "✅ Nginx配置测试通过"
    systemctl reload nginx
    echo "✅ Nginx已重新加载"
else
    echo "❌ Nginx配置测试失败"
    exit 1
fi

echo ""
echo "✅ 修复完成！"
echo ""
echo "📋 验证步骤:"
echo "1. 访问 https://productmaster.dpdns.org/static/css/style.css"
echo "   应该能看到CSS文件内容"
echo ""
echo "2. 访问 https://productmaster.dpdns.org"
echo "   页面样式应该正常显示"
