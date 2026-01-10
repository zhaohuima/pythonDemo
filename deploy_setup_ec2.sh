#!/bin/bash

# 在 EC2 上设置 Product Master 的脚本
# 此脚本需要在 EC2 实例上运行

set -e

PROJECT_NAME="ProductMaster"
PROJECT_DIR="/home/ubuntu/$PROJECT_NAME"
SERVICE_NAME="product-master"

echo "🔧 在 EC2 上设置 Product Master..."
echo "======================================"

# 更新系统
echo ""
echo "📦 更新系统包..."
sudo apt update
sudo apt upgrade -y

# 安装 Python 和必要工具
echo ""
echo "🐍 安装 Python 和相关工具..."
sudo apt install -y python3 python3-pip python3-venv git curl

# 创建虚拟环境
echo ""
echo "📦 创建 Python 虚拟环境..."
cd "$PROJECT_DIR"
python3 -m venv venv
source venv/bin/activate

# 升级 pip
echo ""
echo "⬆️  升级 pip..."
pip install --upgrade pip

# 安装项目依赖
echo ""
echo "📚 安装项目依赖..."
pip install -r requirements.txt

# 创建日志和输出目录
echo ""
echo "📁 创建必要的目录..."
mkdir -p logs outputs

# 设置目录权限
chmod 755 logs outputs

# 创建 systemd 服务文件
echo ""
echo "⚙️  创建 systemd 服务..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Product Master Web Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python3 $PROJECT_DIR/web_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd
sudo systemctl daemon-reload

echo ""
echo "✅ 设置完成！"
echo ""
echo "📋 使用说明："
echo ""
echo "1. 编辑配置文件（设置 API 密钥）:"
echo "   nano $PROJECT_DIR/config.py"
echo ""
echo "2. 启动服务:"
echo "   sudo systemctl start $SERVICE_NAME"
echo ""
echo "3. 查看服务状态:"
echo "   sudo systemctl status $SERVICE_NAME"
echo ""
echo "4. 查看日志:"
echo "   sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "5. 设置开机自启:"
echo "   sudo systemctl enable $SERVICE_NAME"
echo ""
echo "6. 停止服务:"
echo "   sudo systemctl stop $SERVICE_NAME"
echo ""
echo "⚠️  注意："
echo "   - 确保 EC2 安全组允许端口 5000 的入站流量"
echo "   - 访问地址: http://$EC2_IP:5000"
echo "   - 如需使用域名，请配置反向代理（如 Nginx）"
