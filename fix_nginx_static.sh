#!/bin/bash

# 修复 Nginx 静态文件配置脚本
# 用于解决样式和 JavaScript 文件无法加载的问题

echo "=========================================="
echo "🔧 Nginx 静态文件配置修复工具"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否在 EC2 上运行
if [ ! -f "/etc/nginx/sites-available/product-master" ]; then
    echo -e "${RED}❌ 错误: 未找到 Nginx 配置文件${NC}"
    echo "请在 EC2 实例上运行此脚本"
    exit 1
fi

# 检测项目路径
echo "📂 检测项目路径..."
PROJECT_PATHS=(
    "/home/ubuntu/pythonDemo"
    "/home/ubuntu/ProductMaster"
    "/home/ubuntu/product-master"
)

PROJECT_PATH=""
for path in "${PROJECT_PATHS[@]}"; do
    if [ -d "$path" ] && [ -d "$path/static" ]; then
        PROJECT_PATH="$path"
        echo -e "${GREEN}✅ 找到项目路径: $PROJECT_PATH${NC}"
        break
    fi
done

if [ -z "$PROJECT_PATH" ]; then
    echo -e "${YELLOW}⚠️  未找到项目路径，请手动输入:${NC}"
    read -p "项目路径: " PROJECT_PATH
    if [ ! -d "$PROJECT_PATH" ] || [ ! -d "$PROJECT_PATH/static" ]; then
        echo -e "${RED}❌ 路径无效或不存在 static 目录${NC}"
        exit 1
    fi
fi

# 检查静态文件目录
echo ""
echo "📁 检查静态文件目录..."
if [ -d "$PROJECT_PATH/static/css" ]; then
    echo -e "${GREEN}✅ CSS 目录存在${NC}"
    ls -lh "$PROJECT_PATH/static/css/" | head -5
else
    echo -e "${RED}❌ CSS 目录不存在${NC}"
fi

if [ -d "$PROJECT_PATH/static/js" ]; then
    echo -e "${GREEN}✅ JavaScript 目录存在${NC}"
    ls -lh "$PROJECT_PATH/static/js/" | head -5
else
    echo -e "${RED}❌ JavaScript 目录不存在${NC}"
fi

# 备份原配置
echo ""
echo "💾 备份原配置文件..."
sudo cp /etc/nginx/sites-available/product-master /etc/nginx/sites-available/product-master.backup.$(date +%Y%m%d_%H%M%S)
echo -e "${GREEN}✅ 备份完成${NC}"

# 更新 Nginx 配置
echo ""
echo "🔧 更新 Nginx 配置..."
sudo sed -i "s|alias /home/ubuntu/ProductMaster/static/;|alias $PROJECT_PATH/static/;|g" /etc/nginx/sites-available/product-master

# 验证配置
echo ""
echo "✅ 验证 Nginx 配置..."
if sudo nginx -t; then
    echo -e "${GREEN}✅ Nginx 配置验证通过${NC}"
else
    echo -e "${RED}❌ Nginx 配置验证失败${NC}"
    echo "正在恢复备份..."
    sudo cp /etc/nginx/sites-available/product-master.backup.* /etc/nginx/sites-available/product-master
    exit 1
fi

# 检查文件权限
echo ""
echo "🔐 检查文件权限..."
sudo chown -R ubuntu:www-data "$PROJECT_PATH/static"
sudo chmod -R 755 "$PROJECT_PATH/static"
echo -e "${GREEN}✅ 权限已设置${NC}"

# 重启 Nginx
echo ""
echo "🔄 重启 Nginx..."
sudo systemctl restart nginx

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Nginx 重启成功${NC}"
else
    echo -e "${RED}❌ Nginx 重启失败${NC}"
    echo "查看日志: sudo tail -f /var/log/nginx/error.log"
    exit 1
fi

# 显示配置摘要
echo ""
echo "=========================================="
echo "📋 配置摘要"
echo "=========================================="
echo "项目路径: $PROJECT_PATH"
echo "静态文件路径: $PROJECT_PATH/static/"
echo ""
echo "测试静态文件访问:"
echo "  curl -I http://localhost/static/css/style.css"
echo ""
echo "查看 Nginx 错误日志:"
echo "  sudo tail -f /var/log/nginx/product-master-error.log"
echo ""
echo -e "${GREEN}✅ 修复完成！请刷新浏览器页面测试${NC}"
