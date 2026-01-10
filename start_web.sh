#!/bin/bash

# 启动 Web 应用的脚本，修复 SSL 权限问题
# Script to start web app with SSL certificate fix

echo "🔧 Setting up SSL certificates..."
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE

echo "✅ SSL certificates configured"
echo ""

echo "🚀 Starting Web Application..."
python3 web_app.py
