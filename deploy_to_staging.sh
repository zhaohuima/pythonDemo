#!/bin/bash

# ============================================================================
# 本地 Docker Staging 环境部署脚本
# 用于将 Product Master 项目部署到本地 Docker staging 环境
# ============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置信息
PROJECT_NAME="Product Master"
COMPOSE_FILE="docker-compose.yml"

# ============================================================================
# 辅助函数
# ============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================================${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "   ℹ️  $1"
}

# ============================================================================
# 阶段 1: 本地环境检查
# ============================================================================

local_checks() {
    print_header "阶段 1: 本地环境检查"

    # 1.1 检查 Docker
    print_step "检查 Docker 是否安装..."
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        print_success "Docker 已安装: $DOCKER_VERSION"
    else
        print_error "Docker 未安装，请先安装 Docker Desktop"
        exit 1
    fi

    # 1.2 检查 Docker Compose
    print_step "检查 Docker Compose 是否安装..."
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version)
        print_success "Docker Compose 已安装: $COMPOSE_VERSION"
    else
        print_error "Docker Compose 未安装"
        exit 1
    fi

    # 1.3 检查 Docker 是否运行
    print_step "检查 Docker 服务状态..."
    if docker info &> /dev/null; then
        print_success "Docker 服务正在运行"
    else
        print_error "Docker 服务未运行，请启动 Docker Desktop"
        exit 1
    fi

    # 1.4 检查必要文件
    print_step "检查必要文件..."
    REQUIRED_FILES=("$COMPOSE_FILE" "Dockerfile" "requirements.txt" "web_app.py" "agents.py")
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            print_success "文件存在: $file"
        else
            print_error "文件缺失: $file"
            exit 1
        fi
    done

    # 1.5 检查 Python 语法
    print_step "检查 Python 语法错误..."
    PYTHON_FILES=$(find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" 2>/dev/null | head -20)
    SYNTAX_ERRORS=0
    for pyfile in $PYTHON_FILES; do
        if ! python3 -m py_compile "$pyfile" 2>/dev/null; then
            print_error "语法错误: $pyfile"
            SYNTAX_ERRORS=1
        fi
    done
    if [ $SYNTAX_ERRORS -eq 0 ]; then
        print_success "Python 文件语法检查通过"
    else
        print_error "发现 Python 语法错误，请修复后重试"
        exit 1
    fi

    # 1.6 检查 Git 状态
    print_step "检查 Git 状态..."
    if git diff --quiet && git diff --cached --quiet; then
        print_success "所有更改已提交"
    else
        print_warning "有未提交的更改"
        git status --short
        echo ""
        read -p "是否继续部署? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "部署已取消"
            exit 0
        fi
    fi
}

# ============================================================================
# 阶段 2: 停止现有容器
# ============================================================================

stop_containers() {
    print_header "阶段 2: 停止现有容器"

    print_step "停止并移除现有容器..."
    if docker-compose ps -q 2>/dev/null | grep -q .; then
        docker-compose down
        print_success "现有容器已停止并移除"
    else
        print_info "没有运行中的容器"
    fi
}

# ============================================================================
# 阶段 3: 构建新镜像
# ============================================================================

build_images() {
    print_header "阶段 3: 构建 Docker 镜像"

    print_step "构建 Docker 镜像..."
    print_info "这可能需要几分钟时间..."

    if docker-compose build --no-cache; then
        print_success "Docker 镜像构建成功"
    else
        print_error "Docker 镜像构建失败"
        exit 1
    fi
}

# ============================================================================
# 阶段 4: 启动容器
# ============================================================================

start_containers() {
    print_header "阶段 4: 启动容器"

    print_step "启动 Docker 容器..."
    if docker-compose up -d; then
        print_success "容器启动成功"
    else
        print_error "容器启动失败"
        exit 1
    fi

    # 等待服务启动
    print_step "等待服务启动..."
    sleep 10
}

# ============================================================================
# 阶段 5: 验证部署
# ============================================================================

verify_deployment() {
    print_header "阶段 5: 验证部署"

    # 5.1 检查容器状态
    print_step "检查容器状态..."
    CONTAINERS=$(docker-compose ps --services)
    for container in $CONTAINERS; do
        STATUS=$(docker-compose ps -q $container | xargs docker inspect -f '{{.State.Status}}')
        if [ "$STATUS" = "running" ]; then
            print_success "容器 $container 正在运行"
        else
            print_error "容器 $container 状态异常: $STATUS"
        fi
    done

    # 5.2 检查 Web 服务健康状态
    print_step "检查 Web 服务健康状态..."
    MAX_RETRIES=30
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -f http://localhost:5000/ &> /dev/null; then
            print_success "Web 服务响应正常"
            break
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
                print_error "Web 服务无响应"
                print_info "查看日志: docker-compose logs web"
                docker-compose logs --tail=20 web
                exit 1
            fi
            sleep 2
        fi
    done

    # 5.3 检查 Nginx 服务
    print_step "检查 Nginx 服务..."
    if curl -f http://localhost/ &> /dev/null; then
        print_success "Nginx 服务响应正常"
    else
        print_warning "Nginx 服务无响应（可能配置问题）"
        print_info "查看日志: docker-compose logs nginx"
    fi

    # 5.4 检查日志中的错误
    print_step "检查启动日志..."
    ERRORS=$(docker-compose logs web | grep -i "error\|exception\|failed" | grep -v "DEBUG" | tail -5)
    if [ -z "$ERRORS" ]; then
        print_success "未发现启动错误"
    else
        print_warning "发现以下错误/警告:"
        echo "$ERRORS"
    fi

    # 5.5 显示容器资源使用
    print_step "容器资源使用情况..."
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker-compose ps -q)
}

# ============================================================================
# 打印部署总结
# ============================================================================

print_summary() {
    print_header "部署总结"

    echo -e "${GREEN}🎉 Staging 环境部署成功！${NC}"
    echo ""
    echo "访问地址:"
    echo "  - Web 服务: http://localhost:5000"
    echo "  - Nginx 代理: http://localhost"
    echo ""
    echo "常用命令:"
    echo "  - 查看日志: docker-compose logs -f"
    echo "  - 查看 Web 日志: docker-compose logs -f web"
    echo "  - 查看 Nginx 日志: docker-compose logs -f nginx"
    echo "  - 重启服务: docker-compose restart"
    echo "  - 停止服务: docker-compose down"
    echo "  - 查看状态: docker-compose ps"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}测试提示:${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "1. 打开浏览器访问: http://localhost:5000"
    echo "2. 测试 Product Research 功能，验证格式化改进"
    echo "3. 检查输出是否有清晰的段落分隔和列表格式"
    echo "4. 使用 Cmd+Shift+R (Mac) 或 Ctrl+Shift+R (Windows) 强制刷新浏览器"
    echo ""
}

# ============================================================================
# 主流程
# ============================================================================

main() {
    print_header "🚀 $PROJECT_NAME - Docker Staging 环境部署"
    echo "Docker Compose 文件: $COMPOSE_FILE"
    echo ""

    # 执行各阶段
    local_checks

    # 确认是否继续
    echo ""
    read -p "所有检查完成，是否继续部署? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "部署已取消"
        exit 0
    fi

    stop_containers
    build_images
    start_containers
    verify_deployment
    print_summary
}

# 运行主流程
main "$@"
