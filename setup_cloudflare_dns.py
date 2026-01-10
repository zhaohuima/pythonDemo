#!/usr/bin/env python3
"""
Cloudflare DNS自动配置脚本 (Python版本)
使用Cloudflare API自动添加A记录
"""

import sys
import json
import requests
from typing import Optional, Dict, Any

DOMAIN = "productmaster.dpdns.org"
# 尝试两种可能的根域名配置
ROOT_DOMAIN_OPTIONS = ["productmaster.dpdns.org", "dpdns.org"]
SUBDOMAIN = "@"  # 如果productmaster.dpdns.org是根域名，使用@作为记录名
TARGET_IP = "13.239.2.255"

def get_zone_id(api_token: str) -> tuple[Optional[str], Optional[str]]:
    """获取Zone ID，返回(zone_id, root_domain)"""
    print("📡 步骤2: 获取Zone ID...")
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # 尝试查找所有可能的根域名
    for root_domain in ROOT_DOMAIN_OPTIONS:
        print(f"  尝试查找域名: {root_domain}...")
        url = f"https://api.cloudflare.com/client/v4/zones?name={root_domain}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("success"):
                continue
            
            zones = data.get("result", [])
            if zones:
                zone_id = zones[0].get("id")
                zone_name = zones[0].get("name")
                print(f"✅ 找到域名: {zone_name}")
                print(f"✅ Zone ID: {zone_id}")
                return zone_id, zone_name
                
        except Exception as e:
            print(f"  查找 {root_domain} 时出错: {e}")
            continue
    
    # 如果都找不到，列出所有可用的域名
    print("\n⚠️  无法找到域名，正在列出您账户中的所有域名...")
    try:
        url = "https://api.cloudflare.com/client/v4/zones"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            all_zones = data.get("result", [])
            if all_zones:
                print("\n您账户中的域名列表:")
                for zone in all_zones:
                    print(f"  - {zone.get('name')} (状态: {zone.get('status')})")
                print(f"\n请确认 {DOMAIN} 对应的根域名是什么")
            else:
                print("  未找到任何域名")
        else:
            print("  无法获取域名列表")
    except Exception as e:
        print(f"  获取域名列表时出错: {e}")
    
    print(f"\n❌ 无法找到域名")
    print("\n请检查:")
    print(f"- 确认域名在Cloudflare控制台中")
    print("- API Token权限是否包含该域名")
    return None, None

def check_existing_record(zone_id: str, root_domain: str, api_token: str) -> Optional[Dict[str, Any]]:
    """检查现有DNS记录"""
    print("\n🔍 步骤3: 检查现有DNS记录...")
    
    # 如果根域名是productmaster.dpdns.org，记录名应该是@
    # 如果根域名是dpdns.org，记录名应该是productmaster
    if root_domain == "productmaster.dpdns.org":
        record_name = "@"
        search_name = root_domain
    else:
        record_name = "productmaster"
        search_name = DOMAIN
    
    print(f"  查找记录: {search_name}")
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={search_name}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            return None
        
        records = data.get("result", [])
        if records:
            record = records[0]
            print(f"⚠️  发现现有A记录:")
            print(f"   记录ID: {record.get('id')}")
            print(f"   当前IP: {record.get('content')}")
            return record
        
        print("ℹ️  未找到现有记录，将创建新记录")
        return None
        
    except Exception as e:
        print(f"⚠️  检查记录时出错: {e}")
        return None

def update_record(zone_id: str, record_id: str, root_domain: str, api_token: str) -> bool:
    """更新现有DNS记录"""
    print("\n🔄 更新DNS记录...")
    
    # 确定记录名
    if root_domain == "productmaster.dpdns.org":
        record_name = "@"
    else:
        record_name = "productmaster"
    
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "A",
        "name": record_name,
        "content": TARGET_IP,
        "ttl": 1
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            print("✅ DNS记录已更新！")
            print(f"\n记录详情:")
            print(f"  域名: {DOMAIN}")
            print(f"  IP: {TARGET_IP}")
            return True
        else:
            errors = data.get("errors", [])
            error_msg = errors[0].get("message", "Unknown error") if errors else "Unknown error"
            print(f"❌ 更新失败: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False

def create_record(zone_id: str, root_domain: str, api_token: str) -> bool:
    """创建新DNS记录"""
    print("\n➕ 步骤4: 创建DNS A记录...")
    
    # 确定记录名
    if root_domain == "productmaster.dpdns.org":
        record_name = "@"
    else:
        record_name = "productmaster"
    
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "A",
        "name": record_name,
        "content": TARGET_IP,
        "ttl": 1,
        "proxied": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            record_id = data.get("result", {}).get("id")
            print("✅ DNS记录已创建！")
            print(f"\n记录详情:")
            print(f"  记录ID: {record_id}")
            print(f"  域名: {DOMAIN}")
            print(f"  IP: {TARGET_IP}")
            return True
        else:
            errors = data.get("errors", [])
            error_msg = errors[0].get("message", "Unknown error") if errors else "Unknown error"
            print(f"❌ 创建失败: {error_msg}")
            print("\n请检查:")
            print("1. API Token权限是否正确")
            print("2. 域名是否在Cloudflare账户中")
            print("3. 子域名是否已存在其他记录")
            return False
            
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

def main():
    print("🌐 Cloudflare DNS自动配置脚本")
    print("=" * 30)
    print(f"域名: {DOMAIN}")
    print(f"目标IP: {TARGET_IP}")
    print()
    
    # 获取API Token
    if len(sys.argv) > 1:
        api_token = sys.argv[1]
        print("✅ 使用命令行参数提供的Token")
    elif "CF_API_TOKEN" in os.environ:
        api_token = os.environ["CF_API_TOKEN"]
        print("✅ 使用环境变量中的Token")
    else:
        print("❌ 请提供Cloudflare API Token")
        print("\n使用方法:")
        print(f"  python3 {sys.argv[0]} [API_TOKEN]")
        print("  或")
        print(f"  CF_API_TOKEN=your_token python3 {sys.argv[0]}")
        sys.exit(1)
    
    print()
    
    # 获取Zone ID
    zone_id, root_domain = get_zone_id(api_token)
    if not zone_id or not root_domain:
        sys.exit(1)
    
    print(f"\n✅ 使用根域名: {root_domain}")
    
    # 检查现有记录
    existing_record = check_existing_record(zone_id, root_domain, api_token)
    
    if existing_record:
        record_id = existing_record.get("id")
        existing_ip = existing_record.get("content")
        
        if existing_ip == TARGET_IP:
            print("\n✅ DNS记录已正确配置！")
            print(f"\n记录详情:")
            print(f"  域名: {DOMAIN}")
            print(f"  IP: {TARGET_IP}")
            print("\n可以继续配置HTTPS了:")
            print("  ./retry_certbot_local.sh")
            sys.exit(0)
        else:
            print(f"\n当前IP ({existing_ip}) 与目标IP ({TARGET_IP}) 不匹配")
            print("正在更新记录...")
            if update_record(zone_id, record_id, root_domain, api_token):
                print("\nDNS更改通常需要1-5分钟生效")
                print("\n可以继续配置HTTPS了:")
                print("  ./retry_certbot_local.sh")
                sys.exit(0)
            else:
                sys.exit(1)
    else:
        # 创建新记录
        if create_record(zone_id, root_domain, api_token):
            print("\nDNS更改通常需要1-5分钟生效")
            print("\n等待DNS生效后，可以运行:")
            print("  ./retry_certbot_local.sh")
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == "__main__":
    import os
    main()
