#!/bin/bash

# Cloudflare DNS自动配置脚本
# 使用Cloudflare API自动添加A记录

set -e

DOMAIN="productmaster.dpdns.org"
ROOT_DOMAIN="dpdns.org"
SUBDOMAIN="productmaster"
TARGET_IP="13.239.2.255"

echo "🌐 Cloudflare DNS自动配置脚本"
echo "=============================="
echo "域名: $DOMAIN"
echo "根域名: $ROOT_DOMAIN"
echo "子域名: $SUBDOMAIN"
echo "目标IP: $TARGET_IP"
echo ""

# 检查jq是否安装（用于解析JSON）
if ! command -v jq &> /dev/null; then
    echo "📦 安装jq（JSON解析工具）..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install jq
        else
            echo "❌ 请先安装Homebrew，然后运行: brew install jq"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update && sudo apt-get install -y jq
    else
        echo "⚠️  请手动安装jq: https://stedolan.github.io/jq/download/"
        exit 1
    fi
fi

echo "✅ jq已安装"
echo ""

# 获取Cloudflare API Token
echo "🔑 步骤1: 配置Cloudflare API"
echo ""
echo "需要Cloudflare API Token来配置DNS记录"
echo ""
echo "获取API Token的方法:"
echo "1. 登录 https://dash.cloudflare.com/"
echo "2. 点击右上角头像 → My Profile"
echo "3. 进入 API Tokens 标签页"
echo "4. 点击 Create Token"
echo "5. 使用 'Edit zone DNS' 模板"
echo "6. 选择区域: $ROOT_DOMAIN"
echo "7. 复制生成的Token"
echo ""

# 支持从命令行参数或环境变量获取Token
if [ -n "$1" ]; then
    CF_API_TOKEN="$1"
    echo "✅ 使用命令行参数提供的Token"
elif [ -n "$CF_API_TOKEN" ]; then
    echo "✅ 使用环境变量中的Token"
else
    read -p "请输入Cloudflare API Token: " CF_API_TOKEN
fi

if [ -z "$CF_API_TOKEN" ]; then
    echo "❌ API Token不能为空"
    echo ""
    echo "使用方法:"
    echo "  ./setup_cloudflare_dns.sh [API_TOKEN]"
    echo "  或"
    echo "  CF_API_TOKEN=your_token ./setup_cloudflare_dns.sh"
    exit 1
fi

echo ""

# 步骤2: 获取Zone ID
echo "📡 步骤2: 获取Zone ID..."
ZONE_RESPONSE=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$ROOT_DOMAIN" \
    -H "Authorization: Bearer $CF_API_TOKEN" \
    -H "Content-Type: application/json")

# 检查API响应
if echo "$ZONE_RESPONSE" | jq -e '.success == false' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$ZONE_RESPONSE" | jq -r '.errors[0].message' 2>/dev/null || echo "Unknown error")
    echo "❌ API错误: $ERROR_MSG"
    echo ""
    echo "请检查:"
    echo "1. API Token是否正确"
    echo "2. API Token是否有权限访问域名 $ROOT_DOMAIN"
    exit 1
fi

ZONE_ID=$(echo "$ZONE_RESPONSE" | jq -r '.result[0].id' 2>/dev/null)

if [ -z "$ZONE_ID" ] || [ "$ZONE_ID" = "null" ]; then
    echo "❌ 无法找到域名 $ROOT_DOMAIN 的Zone ID"
    echo ""
    echo "请检查:"
    echo "1. 域名是否在您的Cloudflare账户中"
    echo "2. API Token是否有权限访问该域名"
    exit 1
fi

echo "✅ Zone ID: $ZONE_ID"
echo ""

# 步骤3: 检查现有记录
echo "🔍 步骤3: 检查现有DNS记录..."
EXISTING_RECORD=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?type=A&name=$DOMAIN" \
    -H "Authorization: Bearer $CF_API_TOKEN" \
    -H "Content-Type: application/json")

RECORD_ID=$(echo "$EXISTING_RECORD" | jq -r '.result[0].id' 2>/dev/null)
EXISTING_IP=$(echo "$EXISTING_RECORD" | jq -r '.result[0].content' 2>/dev/null)

if [ -n "$RECORD_ID" ] && [ "$RECORD_ID" != "null" ]; then
    echo "⚠️  发现现有A记录:"
    echo "   记录ID: $RECORD_ID"
    echo "   当前IP: $EXISTING_IP"
    echo ""
    
    if [ "$EXISTING_IP" = "$TARGET_IP" ]; then
        echo "✅ DNS记录已正确配置！"
        echo ""
        echo "记录详情:"
        echo "  域名: $DOMAIN"
        echo "  IP: $TARGET_IP"
        echo ""
        echo "可以继续配置HTTPS了:"
        echo "  ./retry_certbot_local.sh"
        exit 0
    else
        echo "当前IP ($EXISTING_IP) 与目标IP ($TARGET_IP) 不匹配"
        read -p "是否更新现有记录? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "取消操作"
            exit 0
        fi
        
        # 更新现有记录
        echo ""
        echo "🔄 更新DNS记录..."
        UPDATE_RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
            -H "Authorization: Bearer $CF_API_TOKEN" \
            -H "Content-Type: application/json" \
            --data "{\"type\":\"A\",\"name\":\"$SUBDOMAIN\",\"content\":\"$TARGET_IP\",\"ttl\":1}")
        
        if echo "$UPDATE_RESPONSE" | jq -e '.success == true' > /dev/null 2>&1; then
            echo "✅ DNS记录已更新！"
            echo ""
            echo "记录详情:"
            echo "  域名: $DOMAIN"
            echo "  IP: $TARGET_IP"
            echo ""
            echo "DNS更改通常需要1-5分钟生效"
            echo ""
            echo "可以继续配置HTTPS了:"
            echo "  ./retry_certbot_local.sh"
            exit 0
        else
            ERROR_MSG=$(echo "$UPDATE_RESPONSE" | jq -r '.errors[0].message' 2>/dev/null || echo "Unknown error")
            echo "❌ 更新失败: $ERROR_MSG"
            exit 1
        fi
    fi
else
    echo "ℹ️  未找到现有记录，将创建新记录"
    echo ""
    
    # 步骤4: 创建新记录
    echo "➕ 步骤4: 创建DNS A记录..."
    CREATE_RESPONSE=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
        -H "Authorization: Bearer $CF_API_TOKEN" \
        -H "Content-Type: application/json" \
        --data "{\"type\":\"A\",\"name\":\"$SUBDOMAIN\",\"content\":\"$TARGET_IP\",\"ttl\":1,\"proxied\":false}")
    
    if echo "$CREATE_RESPONSE" | jq -e '.success == true' > /dev/null 2>&1; then
        NEW_RECORD_ID=$(echo "$CREATE_RESPONSE" | jq -r '.result.id')
        echo "✅ DNS记录已创建！"
        echo ""
        echo "记录详情:"
        echo "  记录ID: $NEW_RECORD_ID"
        echo "  域名: $DOMAIN"
        echo "  IP: $TARGET_IP"
        echo ""
        echo "DNS更改通常需要1-5分钟生效"
        echo ""
        echo "等待DNS生效后，可以运行:"
        echo "  ./retry_certbot_local.sh"
        exit 0
    else
        ERROR_MSG=$(echo "$CREATE_RESPONSE" | jq -r '.errors[0].message' 2>/dev/null || echo "Unknown error")
        echo "❌ 创建失败: $ERROR_MSG"
        echo ""
        echo "请检查:"
        echo "1. API Token权限是否正确"
        echo "2. 域名是否在Cloudflare账户中"
        echo "3. 子域名是否已存在其他记录"
        exit 1
    fi
fi
