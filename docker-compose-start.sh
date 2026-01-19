#!/bin/bash

# Docker Compose Staging 环境启动脚本
# 用于在本地 Mac Mini 上启动 Staging 环境

set -e

echo "=========================================="
echo "🚀 启动 Product Master Staging 环境"
echo "=========================================="
echo ""

# 检查 Docker 和 Docker Compose 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装。请先安装 Docker Desktop。"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ 错误: Docker Compose 未安装。"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo "❌ 错误: Docker 未运行。请启动 Docker Desktop。"
    exit 1
fi

echo "✅ Docker 环境检查通过"
echo ""

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs outputs knowledge_base/documents vector_db
echo "✅ 目录创建完成"
echo ""

# 构建并启动服务
echo "🔨 构建 Docker 镜像..."
docker-compose build --no-cache

echo ""
echo "🚀 启动服务..."
docker-compose up -d

echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态:"
docker-compose ps

echo ""
echo "=========================================="
echo "✅ Staging 环境启动完成！"
echo "=========================================="
echo ""
echo "🌐 访问地址:"
echo "   - 通过 Nginx: http://localhost"
echo "   - 直接访问 Flask: http://localhost:5000"
echo ""
echo "📝 查看日志:"
echo "   - Web 服务: docker-compose logs -f web"
echo "   - Nginx: docker-compose logs -f nginx"
echo ""
echo "🛑 停止服务:"
echo "   docker-compose down"
echo ""
echo "🔄 重启服务:"
echo "   docker-compose restart"
echo ""
