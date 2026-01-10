#!/bin/bash

# DNS解析检查脚本
# 用于验证域名是否正确指向EC2

DOMAIN="productmaster.dpdns.org"
EC2_IP="13.239.2.255"

echo "🔍 DNS解析检查"
echo "=============="
echo "域名: $DOMAIN"
echo "期望IP: $EC2_IP"
echo ""

# 检查dig命令是否可用
if ! command -v dig &> /dev/null; then
    echo "⚠️  dig命令未安装，尝试使用ping..."
    PING_RESULT=$(ping -c 1 $DOMAIN 2>/dev/null | grep -oP '(\d+\.\d+\.\d+\.\d+)' | head -n1)
    if [ -z "$PING_RESULT" ]; then
        echo "❌ 无法解析域名 $DOMAIN"
        echo ""
        echo "请检查DNS配置:"
        echo "  主机记录: productmaster (或 @)"
        echo "  记录类型: A"
        echo "  记录值: $EC2_IP"
        exit 1
    else
        DNS_IP="$PING_RESULT"
    fi
else
    DNS_IP=$(dig +short $DOMAIN | tail -n1)
fi

if [ -z "$DNS_IP" ]; then
    echo "❌ 无法解析域名 $DOMAIN"
    echo ""
    echo "可能的原因:"
    echo "1. DNS记录尚未生效（等待5-10分钟）"
    echo "2. DNS配置错误"
    echo ""
    echo "请检查DNS配置:"
    echo "  主机记录: productmaster (或 @)"
    echo "  记录类型: A"
    echo "  记录值: $EC2_IP"
    exit 1
fi

echo "📡 DNS解析结果: $DOMAIN -> $DNS_IP"
echo ""

if [ "$DNS_IP" = "$EC2_IP" ]; then
    echo "✅ DNS解析正确！"
    echo ""
    echo "可以继续配置HTTPS了"
    exit 0
else
    echo "⚠️  DNS解析不匹配"
    echo "  期望: $EC2_IP"
    echo "  实际: $DNS_IP"
    echo ""
    echo "请检查DNS配置，确保域名指向正确的IP地址"
    exit 1
fi
