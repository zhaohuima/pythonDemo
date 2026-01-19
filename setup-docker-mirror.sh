#!/bin/bash

# 配置 Docker 镜像加速器脚本
# 用于解决 Docker Hub 访问慢或无法访问的问题

echo "=========================================="
echo "🔧 配置 Docker 镜像加速器"
echo "=========================================="
echo ""

# 检查操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    DOCKER_CONFIG_FILE="$HOME/.docker/daemon.json"
    echo "检测到 macOS 系统"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    DOCKER_CONFIG_FILE="/etc/docker/daemon.json"
    echo "检测到 Linux 系统"
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    exit 1
fi

# 创建配置目录
mkdir -p "$(dirname "$DOCKER_CONFIG_FILE")"

# 备份现有配置
if [ -f "$DOCKER_CONFIG_FILE" ]; then
    echo "📋 备份现有配置..."
    cp "$DOCKER_CONFIG_FILE" "${DOCKER_CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 创建或更新配置
echo "📝 配置镜像加速器..."

# 国内常用的 Docker 镜像加速器
MIRRORS=(
    "https://docker.mirrors.ustc.edu.cn"
    "https://hub-mirror.c.163.com"
    "https://mirror.baidubce.com"
)

# 读取现有配置或创建新配置
if [ -f "$DOCKER_CONFIG_FILE" ]; then
    # 使用 Python 来安全地更新 JSON
    python3 << EOF
import json
import sys

config_file = "$DOCKER_CONFIG_FILE"
mirrors = $MIRRORS

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}

if 'registry-mirrors' not in config:
    config['registry-mirrors'] = []

# 添加镜像源（如果不存在）
for mirror in mirrors:
    if mirror not in config['registry-mirrors']:
        config['registry-mirrors'].append(mirror)

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("✅ 配置已更新")
EOF
else
    # 创建新配置
    python3 << EOF
import json

config = {
    "registry-mirrors": $MIRRORS
}

with open("$DOCKER_CONFIG_FILE", 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("✅ 配置已创建")
EOF
fi

echo ""
echo "=========================================="
echo "✅ 镜像加速器配置完成！"
echo "=========================================="
echo ""
echo "📋 配置的镜像源:"
cat "$DOCKER_CONFIG_FILE" | grep -A 10 "registry-mirrors" || echo "   (配置读取失败)"
echo ""
echo "⚠️  重要提示:"
echo "   1. 如果使用 macOS，配置已应用到 Docker Desktop"
echo "   2. 如果使用 Linux，需要重启 Docker 服务:"
echo "      sudo systemctl restart docker"
echo ""
echo "🔄 对于 Docker Desktop (macOS):"
echo "   1. 点击菜单栏的 Docker 图标"
echo "   2. 选择 Settings (设置)"
echo "   3. 选择 Docker Engine"
echo "   4. 确认配置已应用，或手动添加镜像源"
echo "   5. 点击 Apply & Restart"
echo ""
echo "📝 配置文件位置: $DOCKER_CONFIG_FILE"
echo ""
