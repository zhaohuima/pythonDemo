#!/bin/bash

# DNS状态检查脚本
# 检查DNS A记录是否已配置并生效

DOMAIN="productmaster.dpdns.org"
EXPECTED_IP="13.239.2.255"

echo "🔍 DNS状态检查"
echo "=============="
echo "域名: $DOMAIN"
echo "期望IP: $EXPECTED_IP"
echo ""

# 检查dig命令是否可用
if command -v dig &> /dev/null; then
    echo "📡 使用dig查询DNS..."
    DNS_IP=$(dig +short $DOMAIN | tail -n1)
    
    if [ -z "$DNS_IP" ]; then
        echo "❌ DNS解析失败: 无法解析域名 $DOMAIN"
        echo ""
        echo "可能的原因:"
        echo "1. DNS记录尚未配置"
        echo "2. DNS记录已配置但未生效（等待5-10分钟）"
        echo "3. DNS服务商服务器问题"
        echo ""
        echo "请检查DNS配置:"
        echo "  主机记录: productmaster (或 @)"
        echo "  记录类型: A"
        echo "  记录值: $EXPECTED_IP"
        exit 1
    else
        echo "✅ DNS解析成功: $DOMAIN -> $DNS_IP"
        
        if [ "$DNS_IP" = "$EXPECTED_IP" ]; then
            echo "✅ DNS解析正确！"
            echo ""
            echo "可以继续配置HTTPS了:"
            echo "  ./retry_certbot_local.sh"
            exit 0
        else
            echo "⚠️  DNS解析不匹配:"
            echo "  期望: $EXPECTED_IP"
            echo "  实际: $DNS_IP"
            echo ""
            echo "请检查DNS记录值是否正确"
            exit 1
        fi
    fi
else
    echo "⚠️  dig命令未安装，尝试使用nslookup..."
    
    if command -v nslookup &> /dev/null; then
        DNS_IP=$(nslookup $DOMAIN 2>/dev/null | grep -A 1 "Name:" | tail -n1 | awk '{print $2}')
        
        if [ -z "$DNS_IP" ]; then
            echo "❌ DNS解析失败"
            exit 1
        else
            echo "✅ DNS解析: $DOMAIN -> $DNS_IP"
            
            if [ "$DNS_IP" = "$EXPECTED_IP" ]; then
                echo "✅ DNS解析正确！"
                exit 0
            else
                echo "⚠️  DNS解析不匹配"
                exit 1
            fi
        fi
    else
        echo "❌ 无法检查DNS（dig和nslookup都未安装）"
        echo ""
        echo "请手动检查DNS配置，或访问:"
        echo "  https://www.whatsmydns.net/"
        echo "  输入: $DOMAIN"
        exit 1
    fi
fi
