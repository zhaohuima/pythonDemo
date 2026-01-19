#!/bin/bash

# Docker Desktop 检查脚本

echo "=========================================="
echo "🔍 检查 Docker Desktop 状态"
echo "=========================================="
echo ""

# 检查 Docker 命令是否可用
if command -v docker &> /dev/null; then
    echo "✅ Docker 命令已安装"
    docker --version
else
    echo "❌ Docker 命令未找到"
    echo "   请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

echo ""

# 检查 Docker 是否运行
if docker info &> /dev/null; then
    echo "✅ Docker Desktop 正在运行"
    echo ""
    echo "Docker 信息:"
    docker info | head -n 5
else
    echo "❌ Docker Desktop 未运行"
    echo ""
    echo "请执行以下步骤:"
    echo "1. 打开 Finder → 应用程序"
    echo "2. 找到 Docker 应用并双击启动"
    echo "3. 等待 Docker Desktop 完全启动（菜单栏显示 Docker 图标）"
    echo "4. 然后重新运行此脚本"
    exit 1
fi

echo ""

# 检查 Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose 已安装"
    docker-compose --version
elif docker compose version &> /dev/null; then
    echo "✅ Docker Compose (插件版本) 已安装"
    docker compose version
else
    echo "⚠️  Docker Compose 未找到（Docker Desktop 通常自带）"
fi

echo ""
echo "=========================================="
echo "✅ Docker 环境检查完成！"
echo "=========================================="
echo ""
echo "现在可以运行: ./docker-compose-start.sh"
