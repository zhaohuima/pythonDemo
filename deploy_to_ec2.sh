#!/bin/bash

# ============================================================================
# AWS EC2 部署脚本 (增强版)
# 用于将 Product Master 项目部署到 EC2 实例
# 包含完整的部署前检查清单和自动化部署流程
# ============================================================================
#
# 历史问题与经验教训 (Lessons Learned):
# ----------------------------------------------------------------------------
#
# 【问题1】Gunicorn 多 Worker 导致状态不共享 (2026-01-15)
#   症状: 用户提交请求后，轮询状态时返回 "Execution ID not found" 错误
#   原因: execution_states 字典存储在进程内存中，多个 Gunicorn worker 进程
#         各自维护独立的内存空间，导致请求被路由到不同 worker 时找不到状态
#   解决: 在 gunicorn_config.py 中设置 workers = 1，确保单 worker 运行
#   长期方案: 如需多 worker 支持，应使用 Redis 等外部存储来共享状态
#   检查点: 本脚本会自动检查 gunicorn_config.py 中的 workers 配置
#
# 【问题2】Nginx 端口配置不匹配导致 502 错误 (2026-01-15)
#   症状: 访问网站时返回 502 Bad Gateway 错误
#   原因: Nginx 配置中 proxy_pass 指向 5000 端口，但 Flask 服务运行在 5001 端口
#   解决: 更新 Nginx 配置中的端口号，确保与实际服务端口一致
#   检查点: 本脚本会自动检查 Nginx 配置与服务端口是否匹配
#
# 【问题3】浏览器缓存导致前端更新不生效 (2026-01-15)
#   症状: 部署新版本后，用户看到的仍是旧版本的 CSS/JS，页面显示异常
#   原因: Nginx 配置了 "expires 30d" 和 "Cache-Control: public, immutable"
#         导致浏览器缓存静态文件长达 30 天
#   解决: 在 HTML 模板中为静态文件 URL 添加版本号查询字符串 ?v=YYYYMMDD
#         例如: style.css?v=20260115
#   检查点: 本脚本会自动检查并更新静态文件的版本号
#
# 【问题4】CSS :has() 选择器导致样式问题 (2026-01-15)
#   症状: Markdown 内容显示为黑色背景，代码块和普通文本样式混淆
#   原因: .result-content pre 样式应用于所有 pre 标签，包括非代码块内容
#   解决: 使用 CSS :has() 选择器区分代码块和普通 pre 标签
#         - pre:has(code) 用于代码块（深色背景）
#         - pre:not(:has(code)) 用于普通内容（透明背景）
#   注意: :has() 选择器需要现代浏览器支持 (Chrome 105+, Safari 15.4+, Firefox 121+)
#
# ============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置信息
EC2_IP="13.239.2.255"
EC2_USER="ubuntu"
KEY_FILE="/Users/mazhaohui/AWS 实例密钥/My Ubuntu Key -EC2_t3.micro_product master.pem"
PROJECT_NAME="ProductMaster"
REMOTE_DIR="/home/ubuntu/$PROJECT_NAME"
SERVICE_NAME="product-master"

# RAG 相关依赖（需要特殊处理）
RAG_DEPENDENCIES="chromadb sentence-transformers transformers scipy scikit-learn"

# 计数器
CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

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
    ((CHECKS_PASSED++))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((CHECKS_FAILED++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

print_info() {
    echo -e "   ℹ️  $1"
}

ssh_cmd() {
    ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$EC2_USER@$EC2_IP" "$1"
}

# ============================================================================
# 阶段 1: 本地环境检查
# ============================================================================

local_checks() {
    print_header "阶段 1: 本地环境检查"

    # 1.1 检查密钥文件
    print_step "检查 SSH 密钥文件..."
    if [ -f "$KEY_FILE" ]; then
        chmod 400 "$KEY_FILE"
        print_success "密钥文件存在且权限已设置"
    else
        print_error "密钥文件不存在: $KEY_FILE"
        exit 1
    fi

    # 1.2 检查必要文件
    print_step "检查必要文件..."
    REQUIRED_FILES=("requirements.txt" "web_app.py" "agents.py" "config.py" "static/js/app.js" "templates/index.html")
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            print_success "文件存在: $file"
        else
            print_error "文件缺失: $file"
        fi
    done

    # 1.3 检查 requirements.txt 是否包含 RAG 依赖
    print_step "检查 requirements.txt 中的 RAG 依赖..."
    RAG_DEPS_MISSING=()
    for dep in chromadb sentence-transformers; do
        if ! grep -qi "$dep" requirements.txt 2>/dev/null; then
            RAG_DEPS_MISSING+=("$dep")
        fi
    done
    if [ ${#RAG_DEPS_MISSING[@]} -eq 0 ]; then
        print_success "RAG 依赖已在 requirements.txt 中"
    else
        print_warning "以下 RAG 依赖未在 requirements.txt 中: ${RAG_DEPS_MISSING[*]}"
        print_info "这些依赖将在 EC2 上单独安装"
    fi

    # 1.4 检查本地语法错误
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
    fi

    # 1.5 检查 JavaScript 语法（基本检查）
    print_step "检查 JavaScript 文件..."
    if [ -f "static/js/app.js" ]; then
        # 检查是否有明显的语法问题（未闭合的括号等）
        JS_SIZE=$(wc -c < "static/js/app.js")
        if [ "$JS_SIZE" -gt 1000 ]; then
            print_success "JavaScript 文件存在且大小正常 (${JS_SIZE} bytes)"
        else
            print_warning "JavaScript 文件可能不完整 (${JS_SIZE} bytes)"
        fi
    fi

    # 1.6 检查 Gunicorn workers 配置（经验教训 #1）
    print_step "检查 Gunicorn workers 配置..."
    if [ -f "gunicorn_config.py" ]; then
        WORKERS_COUNT=$(grep -E "^workers\s*=" gunicorn_config.py | grep -oE "[0-9]+" | head -1)
        if [ "$WORKERS_COUNT" = "1" ]; then
            print_success "Gunicorn workers = 1 (正确，避免状态不共享问题)"
        elif [ -n "$WORKERS_COUNT" ]; then
            print_warning "Gunicorn workers = $WORKERS_COUNT (可能导致 execution_states 不共享)"
            print_info "建议设置 workers = 1，或使用 Redis 共享状态"
        else
            print_warning "未找到 workers 配置"
        fi
    else
        print_info "未找到 gunicorn_config.py，跳过检查"
    fi

    # 1.7 检查静态文件版本号（经验教训 #3）
    print_step "检查静态文件缓存版本号..."
    if [ -f "templates/index.html" ]; then
        CSS_VERSION=$(grep -oE "style\.css\?v=[0-9]+" templates/index.html | grep -oE "[0-9]+$" | head -1)
        JS_VERSION=$(grep -oE "app\.js\?v=[0-9]+" templates/index.html | grep -oE "[0-9]+$" | head -1)
        TODAY=$(date +%Y%m%d)

        if [ -n "$CSS_VERSION" ] && [ -n "$JS_VERSION" ]; then
            print_success "静态文件版本号: CSS=v$CSS_VERSION, JS=v$JS_VERSION"
            if [ "$CSS_VERSION" != "$TODAY" ] || [ "$JS_VERSION" != "$TODAY" ]; then
                print_warning "版本号不是今天的日期，建议更新以确保浏览器加载最新文件"
                read -p "是否自动更新版本号为 $TODAY? (y/n) " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    update_static_versions
                fi
            fi
        else
            print_warning "静态文件 URL 缺少版本号，可能导致浏览器缓存问题"
            print_info "建议在 templates/index.html 中添加 ?v=YYYYMMDD 查询字符串"
            read -p "是否自动添加版本号? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                update_static_versions
            fi
        fi
    fi

    # 1.8 检查 CSS :has() 选择器（经验教训 #4）
    print_step "检查 CSS pre 标签样式..."
    if [ -f "static/css/style.css" ]; then
        if grep -q "pre:has(code)" static/css/style.css && grep -q "pre:not(:has(code))" static/css/style.css; then
            print_success "CSS 使用 :has() 选择器正确区分代码块和普通 pre 标签"
        elif grep -q "\.result-content pre {" static/css/style.css; then
            print_warning "CSS 中 .result-content pre 样式可能影响非代码块内容"
            print_info "建议使用 pre:has(code) 和 pre:not(:has(code)) 区分样式"
        fi
    fi
}

# ============================================================================
# 阶段 2: EC2 连接和资源检查
# ============================================================================

ec2_checks() {
    print_header "阶段 2: EC2 连接和资源检查"

    # 2.1 测试 SSH 连接
    print_step "测试 EC2 SSH 连接..."
    if ssh_cmd "echo 'connected'" >/dev/null 2>&1; then
        print_success "SSH 连接成功"
    else
        print_error "SSH 连接失败"
        print_info "请检查: 1) EC2 实例是否运行 2) 安全组是否允许 SSH 3) 密钥是否正确"
        exit 1
    fi

    # 2.2 检查磁盘空间
    print_step "检查 EC2 磁盘空间..."
    DISK_USAGE=$(ssh_cmd "df -h / | awk 'NR==2 {print \$5}' | tr -d '%'")
    DISK_AVAIL=$(ssh_cmd "df -h / | awk 'NR==2 {print \$4}'")
    if [ "$DISK_USAGE" -lt 80 ]; then
        print_success "磁盘使用率: ${DISK_USAGE}% (可用: ${DISK_AVAIL})"
    elif [ "$DISK_USAGE" -lt 90 ]; then
        print_warning "磁盘使用率较高: ${DISK_USAGE}% (可用: ${DISK_AVAIL})"
        print_info "建议清理 pip 缓存: pip cache purge"
    else
        print_error "磁盘空间不足: ${DISK_USAGE}% (可用: ${DISK_AVAIL})"
        print_info "请先清理磁盘空间"
    fi

    # 2.3 检查内存和 Swap
    print_step "检查 EC2 内存..."
    MEM_INFO=$(ssh_cmd "free -m | awk 'NR==2 {printf \"%d/%dMB (%.1f%%)\", \$3, \$2, \$3/\$2*100}'")
    SWAP_TOTAL=$(ssh_cmd "free -m | awk 'NR==3 {print \$2}'")
    print_success "内存使用: $MEM_INFO"

    if [ "$SWAP_TOTAL" -lt 1000 ]; then
        print_warning "Swap 空间不足 (${SWAP_TOTAL}MB)，建议至少 2GB"
        print_info "sentence-transformers 需要较多内存，可能导致服务崩溃"

        read -p "是否自动创建 2GB Swap? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_swap
        fi
    else
        print_success "Swap 空间充足: ${SWAP_TOTAL}MB"
    fi

    # 2.4 检查服务状态
    print_step "检查 $SERVICE_NAME 服务状态..."
    SERVICE_STATUS=$(ssh_cmd "sudo systemctl is-active $SERVICE_NAME 2>/dev/null || echo 'inactive'")
    if [ "$SERVICE_STATUS" = "active" ]; then
        print_success "服务正在运行"
        # 获取运行时间
        UPTIME=$(ssh_cmd "sudo systemctl show $SERVICE_NAME --property=ActiveEnterTimestamp | cut -d'=' -f2")
        print_info "运行时间: $UPTIME"
    else
        print_warning "服务未运行或不存在"
    fi

    # 2.5 检查 RAG 依赖
    print_step "检查 EC2 上的 RAG 依赖..."
    MISSING_DEPS=()
    for dep in chromadb sentence-transformers torch; do
        if ! ssh_cmd "source $REMOTE_DIR/venv/bin/activate 2>/dev/null && pip show $dep >/dev/null 2>&1"; then
            MISSING_DEPS+=("$dep")
        fi
    done
    if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
        print_success "所有 RAG 依赖已安装"
    else
        print_warning "以下依赖需要安装: ${MISSING_DEPS[*]}"
    fi

    # 2.6 检查 Nginx 端口配置（经验教训 #2）
    print_step "检查 Nginx 端口配置..."
    NGINX_PORT=$(ssh_cmd "grep -oE 'proxy_pass http://127\.0\.0\.1:[0-9]+' /etc/nginx/sites-available/product-master 2>/dev/null | grep -oE '[0-9]+$' | head -1")
    SERVICE_PORT=$(ssh_cmd "grep -oE 'port=[0-9]+' $REMOTE_DIR/web_app.py 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo '5001'")

    if [ -n "$NGINX_PORT" ]; then
        if [ "$NGINX_PORT" = "$SERVICE_PORT" ]; then
            print_success "Nginx 端口配置正确: proxy_pass -> 127.0.0.1:$NGINX_PORT"
        else
            print_error "Nginx 端口不匹配! Nginx: $NGINX_PORT, 服务: $SERVICE_PORT"
            print_info "这会导致 502 Bad Gateway 错误"
            read -p "是否自动修复端口配置? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                fix_nginx_port "$SERVICE_PORT"
            fi
        fi
    else
        print_warning "无法读取 Nginx 端口配置"
    fi
}

# ============================================================================
# 创建 Swap 空间
# ============================================================================

create_swap() {
    print_step "创建 2GB Swap 文件..."
    ssh_cmd "
        if [ ! -f /swapfile ]; then
            sudo fallocate -l 2G /swapfile
            sudo chmod 600 /swapfile
            sudo mkswap /swapfile
            sudo swapon /swapfile
            echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
            echo 'Swap 创建成功'
        else
            echo 'Swap 文件已存在'
        fi
    "
    print_success "Swap 配置完成"
}

# ============================================================================
# 修复 Nginx 端口配置（解决 502 错误）
# ============================================================================

fix_nginx_port() {
    local TARGET_PORT=$1
    print_step "修复 Nginx 端口配置为 $TARGET_PORT..."

    ssh_cmd "
        sudo sed -i 's/proxy_pass http:\/\/127\.0\.0\.1:[0-9]*/proxy_pass http:\/\/127.0.0.1:$TARGET_PORT/g' /etc/nginx/sites-available/product-master
        sudo nginx -t && sudo systemctl reload nginx
    "

    if [ $? -eq 0 ]; then
        print_success "Nginx 端口已修复为 $TARGET_PORT"
    else
        print_error "Nginx 配置修复失败，请手动检查"
    fi
}

# ============================================================================
# 更新静态文件版本号（解决浏览器缓存问题）
# ============================================================================

update_static_versions() {
    print_step "更新静态文件版本号..."
    TODAY=$(date +%Y%m%d)

    # 更新 CSS 版本号
    if grep -q "style\.css?v=" templates/index.html; then
        sed -i.bak "s/style\.css?v=[0-9]*/style.css?v=$TODAY/g" templates/index.html
    else
        sed -i.bak "s/style\.css'/style.css?v=$TODAY'/g" templates/index.html
        sed -i.bak "s/style\.css\"/style.css?v=$TODAY\"/g" templates/index.html
    fi

    # 更新 JS 版本号
    if grep -q "app\.js?v=" templates/index.html; then
        sed -i.bak "s/app\.js?v=[0-9]*/app.js?v=$TODAY/g" templates/index.html
    else
        sed -i.bak "s/app\.js'/app.js?v=$TODAY'/g" templates/index.html
        sed -i.bak "s/app\.js\"/app.js?v=$TODAY\"/g" templates/index.html
    fi

    # 清理备份文件
    rm -f templates/index.html.bak

    print_success "静态文件版本号已更新为 $TODAY"
}

# ============================================================================
# 阶段 3: 文件同步
# ============================================================================

sync_files() {
    print_header "阶段 3: 同步文件到 EC2"

    # 创建远程目录
    print_step "创建远程目录..."
    ssh_cmd "mkdir -p $REMOTE_DIR"

    # 同步文件
    print_step "同步项目文件..."
    rsync -avz --progress \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.git' \
        --exclude 'logs/*' \
        --exclude 'outputs/*' \
        --exclude '.DS_Store' \
        --exclude 'venv' \
        --exclude 'env' \
        --exclude '.cursor' \
        --exclude 'vector_db' \
        --exclude 'Agent RAG PDFs' \
        -e "ssh -i \"$KEY_FILE\" -o StrictHostKeyChecking=no" \
        ./ "$EC2_USER@$EC2_IP:$REMOTE_DIR/"

    print_success "文件同步完成"
}

# ============================================================================
# 阶段 4: 安装依赖
# ============================================================================

install_dependencies() {
    print_header "阶段 4: 安装/更新依赖"

    # 清理 pip 缓存（如果磁盘空间紧张）
    DISK_USAGE=$(ssh_cmd "df -h / | awk 'NR==2 {print \$5}' | tr -d '%'")
    if [ "$DISK_USAGE" -gt 70 ]; then
        print_step "清理 pip 缓存..."
        ssh_cmd "source $REMOTE_DIR/venv/bin/activate && pip cache purge 2>/dev/null || true"
        print_success "pip 缓存已清理"
    fi

    # 安装基础依赖
    print_step "安装基础依赖..."
    ssh_cmd "
        cd $REMOTE_DIR
        source venv/bin/activate
        pip install -q -r requirements.txt
    "
    print_success "基础依赖安装完成"

    # 检查并安装 RAG 依赖
    print_step "检查 RAG 依赖..."

    # 检查 torch
    if ! ssh_cmd "source $REMOTE_DIR/venv/bin/activate && pip show torch >/dev/null 2>&1"; then
        print_step "安装 CPU 版本 PyTorch..."
        ssh_cmd "
            cd $REMOTE_DIR
            source venv/bin/activate
            pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
        "
        print_success "PyTorch (CPU) 安装完成"
    else
        print_success "PyTorch 已安装"
    fi

    # 检查 chromadb
    if ! ssh_cmd "source $REMOTE_DIR/venv/bin/activate && pip show chromadb >/dev/null 2>&1"; then
        print_step "安装 chromadb..."
        ssh_cmd "
            cd $REMOTE_DIR
            source venv/bin/activate
            pip install --no-cache-dir chromadb
        "
        print_success "chromadb 安装完成"
    else
        print_success "chromadb 已安装"
    fi

    # 检查 sentence-transformers
    if ! ssh_cmd "source $REMOTE_DIR/venv/bin/activate && pip show sentence-transformers >/dev/null 2>&1"; then
        print_step "安装 sentence-transformers..."
        ssh_cmd "
            cd $REMOTE_DIR
            source venv/bin/activate
            pip install --no-cache-dir sentence-transformers --no-deps
            pip install --no-cache-dir transformers scipy scikit-learn
        "
        print_success "sentence-transformers 安装完成"
    else
        print_success "sentence-transformers 已安装"
    fi
}

# ============================================================================
# 阶段 5: 重启服务并验证
# ============================================================================

restart_and_verify() {
    print_header "阶段 5: 重启服务并验证"

    # 重启服务
    print_step "重启 $SERVICE_NAME 服务..."
    ssh_cmd "sudo systemctl restart $SERVICE_NAME"
    sleep 5

    # 检查服务状态
    print_step "检查服务状态..."
    SERVICE_STATUS=$(ssh_cmd "sudo systemctl is-active $SERVICE_NAME")
    if [ "$SERVICE_STATUS" = "active" ]; then
        print_success "服务启动成功"
    else
        print_error "服务启动失败"
        print_info "查看日志: sudo journalctl -u $SERVICE_NAME -n 50"
        ssh_cmd "sudo journalctl -u $SERVICE_NAME -n 20 --no-pager"
        exit 1
    fi

    # 检查 RAG 初始化
    print_step "检查 RAG 初始化..."
    sleep 3
    RAG_STATUS=$(ssh_cmd "sudo journalctl -u $SERVICE_NAME -n 50 --no-pager | grep -i 'RAG Retriever initialized' | tail -1")
    if [ -n "$RAG_STATUS" ]; then
        print_success "RAG Retriever 初始化成功"
    else
        print_warning "未检测到 RAG 初始化日志，请手动验证"
    fi

    # 检查是否有错误
    print_step "检查启动错误..."
    ERRORS=$(ssh_cmd "sudo journalctl -u $SERVICE_NAME -n 50 --no-pager | grep -i 'error\|exception\|failed' | grep -v 'DEBUG' | tail -5")
    if [ -z "$ERRORS" ]; then
        print_success "未发现启动错误"
    else
        print_warning "发现以下错误/警告:"
        echo "$ERRORS"
    fi

    # 检查内存使用
    print_step "检查服务内存使用..."
    MEM_USAGE=$(ssh_cmd "sudo systemctl status $SERVICE_NAME --no-pager | grep 'Memory:' | awk '{print \$2}'")
    print_info "服务内存使用: $MEM_USAGE"
}

# ============================================================================
# 打印部署总结
# ============================================================================

print_summary() {
    print_header "部署总结"

    echo -e "检查通过: ${GREEN}$CHECKS_PASSED${NC}"
    echo -e "检查失败: ${RED}$CHECKS_FAILED${NC}"
    echo -e "警告: ${YELLOW}$WARNINGS${NC}"
    echo ""

    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 部署成功完成！${NC}"
        echo ""
        echo "访问地址:"
        echo "  - 生产环境: https://productmaster.dpdns.org"
        echo "  - 直接访问: http://$EC2_IP:5001"
        echo ""
        echo "常用命令:"
        echo "  - 查看日志: ssh -i \"$KEY_FILE\" $EC2_USER@$EC2_IP 'sudo journalctl -u $SERVICE_NAME -f'"
        echo "  - 重启服务: ssh -i \"$KEY_FILE\" $EC2_USER@$EC2_IP 'sudo systemctl restart $SERVICE_NAME'"
        echo "  - 查看状态: ssh -i \"$KEY_FILE\" $EC2_USER@$EC2_IP 'sudo systemctl status $SERVICE_NAME'"
        echo ""
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}重要提示 (基于历史经验):${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "1. 浏览器缓存: 请使用 Cmd+Shift+R (Mac) 或 Ctrl+Shift+R (Windows) 强制刷新"
        echo "   如果仍有问题，清除浏览器缓存或使用隐私模式测试"
        echo ""
        echo "2. 如遇 'Execution ID not found' 错误:"
        echo "   检查 gunicorn_config.py 中 workers 是否为 1"
        echo ""
        echo "3. 如遇 502 Bad Gateway 错误:"
        echo "   检查 Nginx 端口配置是否与服务端口一致 (当前应为 5001)"
        echo ""
        echo "4. 如遇 Markdown 显示为原始文本:"
        echo "   检查 marked.js 是否正确加载，查看浏览器控制台错误"
        echo ""
    else
        echo -e "${RED}⚠️  部署完成但有错误，请检查上述日志${NC}"
    fi
}

# ============================================================================
# 主流程
# ============================================================================

main() {
    print_header "🚀 Product Master EC2 部署脚本 (增强版)"
    echo "EC2 IP: $EC2_IP"
    echo "项目目录: $REMOTE_DIR"
    echo "服务名称: $SERVICE_NAME"

    # 执行各阶段
    local_checks
    ec2_checks

    # 确认是否继续
    echo ""
    read -p "所有检查完成，是否继续部署? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "部署已取消"
        exit 0
    fi

    sync_files
    install_dependencies
    restart_and_verify
    print_summary
}

# 运行主流程
main "$@"
