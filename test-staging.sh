#!/bin/bash

# Staging 环境测试脚本

set -e

echo "=========================================="
echo "🧪 测试 Product Master Staging 环境"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_endpoint() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    echo -n "测试 $description... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ 通过${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ 失败${NC} (HTTP $response, 期望 $expected_status)"
        return 1
    fi
}

# 1. 检查服务是否运行
echo "1️⃣ 检查服务状态..."
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}❌ 错误: 服务未运行。请先运行: docker-compose up -d${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 服务正在运行${NC}"
echo ""

# 2. 等待服务就绪
echo "2️⃣ 等待服务就绪..."
sleep 5
echo ""

# 3. 测试健康检查端点
echo "3️⃣ 测试健康检查端点..."
test_endpoint "http://localhost/health" "Nginx 健康检查"
test_endpoint "http://localhost:5000/" "Flask 应用健康检查"
echo ""

# 4. 测试静态文件
echo "4️⃣ 测试静态文件..."
test_endpoint "http://localhost/static/css/style.css" "CSS 文件"
test_endpoint "http://localhost/static/js/app.js" "JavaScript 文件"
echo ""

# 5. 测试 API 端点
echo "5️⃣ 测试 API 端点..."
test_endpoint "http://localhost/api/rag/status" "RAG 状态 API"
test_endpoint "http://localhost/api/documents" "文档列表 API"
echo ""

# 6. 测试主页
echo "6️⃣ 测试主页..."
test_endpoint "http://localhost/" "主页"
echo ""

# 7. 测试编排 API（需要较长时间）
echo "7️⃣ 测试编排 API（发送测试请求）..."
echo -n "发送测试请求... "
response=$(curl -s -X POST http://localhost/api/orchestrate \
    -H "Content-Type: application/json" \
    -d '{"user_input": "测试产品需求"}' \
    -w "\n%{http_code}" || echo "000")

http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ 请求已接受${NC}"
    execution_id=$(echo "$response" | head -n1 | grep -o '"execution_id":"[^"]*' | cut -d'"' -f4)
    if [ -n "$execution_id" ]; then
        echo "   执行 ID: $execution_id"
        echo "   查看状态: curl http://localhost/api/status/$execution_id"
    fi
else
    echo -e "${RED}✗ 请求失败${NC} (HTTP $http_code)"
fi
echo ""

# 8. 检查日志
echo "8️⃣ 检查服务日志（最近 5 行）..."
echo "--- Web 服务日志 ---"
docker-compose logs --tail=5 web
echo ""
echo "--- Nginx 日志 ---"
docker-compose logs --tail=5 nginx
echo ""

echo "=========================================="
echo -e "${GREEN}✅ 测试完成！${NC}"
echo "=========================================="
echo ""
echo "📝 访问应用:"
echo "   - 主页: http://localhost"
echo "   - API: http://localhost/api/"
echo ""
echo "📊 查看日志:"
echo "   docker-compose logs -f web"
echo "   docker-compose logs -f nginx"
echo ""
