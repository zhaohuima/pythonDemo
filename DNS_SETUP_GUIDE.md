# 🌐 DNS A记录配置指南

为域名 `productmaster.dpdns.org` 配置DNS A记录，指向EC2服务器。

---

## 📋 需要配置的信息

- **主机记录**: `productmaster` (或 `@`)
- **记录类型**: `A`
- **记录值**: `13.239.2.255`
- **TTL**: 默认（或600秒）

---

## 🔧 配置步骤（通用方法）

### 步骤1: 登录DNS服务商管理后台

访问您的DNS服务商管理后台（dpdns.org的管理界面）

### 步骤2: 找到DNS管理/域名解析

通常在以下位置：
- "DNS管理"
- "域名解析"
- "DNS设置"
- "域名管理" → "DNS解析"

### 步骤3: 添加A记录

1. 点击 **"添加记录"** 或 **"新增记录"**
2. 填写以下信息：

| 字段 | 值 | 说明 |
|------|-----|------|
| **主机记录** | `productmaster` | 子域名部分（如果要使用 `productmaster.dpdns.org`）<br>或填写 `@`（如果要使用根域名 `dpdns.org`） |
| **记录类型** | `A` | IPv4地址记录 |
| **记录值** | `13.239.2.255` | EC2服务器的IP地址 |
| **TTL** | `600` 或默认 | 缓存时间（秒） |

3. 点击 **"保存"** 或 **"确认"**

### 步骤4: 等待DNS生效

- **通常需要**: 5-10分钟
- **最长可能需要**: 24-48小时（但通常很快）

---

## 🌍 常见DNS服务商配置方法

### 1. 腾讯云DNSPod

1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 进入 **域名与网站** → **DNS解析DNSPod**
3. 找到域名 `dpdns.org`
4. 点击 **"添加记录"**
5. 填写：
   - 主机记录: `productmaster`
   - 记录类型: `A`
   - 记录值: `13.239.2.255`
   - TTL: `600`
6. 点击 **"确定"**

### 2. 阿里云DNS

1. 登录 [阿里云控制台](https://dns.console.aliyun.com/)
2. 进入 **域名解析**
3. 找到域名 `dpdns.org`
4. 点击 **"添加记录"**
5. 填写：
   - 主机记录: `productmaster`
   - 记录类型: `A`
   - 记录值: `13.239.2.255`
   - TTL: `10分钟`
6. 点击 **"确认"**

### 3. Cloudflare

1. 登录 [Cloudflare控制台](https://dash.cloudflare.com/)
2. 选择域名 `dpdns.org`
3. 进入 **DNS** 标签页
4. 点击 **"Add record"**
5. 填写：
   - Type: `A`
   - Name: `productmaster`
   - IPv4 address: `13.239.2.255`
   - Proxy status: `DNS only` (灰色云朵)
   - TTL: `Auto`
6. 点击 **"Save"**

### 4. 其他DNS服务商

大多数DNS服务商的配置方法类似：
1. 登录管理后台
2. 找到DNS解析/域名管理
3. 添加A记录
4. 填写主机记录、记录类型、记录值
5. 保存

---

## ✅ 验证DNS配置

### 方法1: 使用dig命令（推荐）

```bash
dig +short productmaster.dpdns.org
```

**期望输出**: `13.239.2.255`

### 方法2: 使用nslookup

```bash
nslookup productmaster.dpdns.org
```

**期望输出**: 显示 `Address: 13.239.2.255`

### 方法3: 使用ping

```bash
ping productmaster.dpdns.org
```

**期望输出**: 显示 `PING productmaster.dpdns.org (13.239.2.255)`

### 方法4: 在线DNS查询工具

访问以下网站查询：
- https://www.whatsmydns.net/
- https://dnschecker.org/
- https://mxtoolbox.com/DNSLookup.aspx

输入 `productmaster.dpdns.org`，应该返回 `13.239.2.255`

---

## 🔍 故障排查

### 问题1: DNS记录添加后无法解析

**可能原因**:
- DNS记录未保存成功
- 等待时间不够（需要5-10分钟）
- DNS服务商服务器问题

**解决方案**:
1. 检查DNS记录是否已保存
2. 等待更长时间（最多24小时）
3. 清除本地DNS缓存：
   ```bash
   # macOS
   sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
   
   # Linux
   sudo systemd-resolve --flush-caches
   
   # Windows
   ipconfig /flushdns
   ```

### 问题2: 解析到错误的IP地址

**检查**:
1. 确认DNS记录值是否正确
2. 检查是否有多个A记录冲突
3. 清除DNS缓存后重试

### 问题3: 部分地区解析正常，部分不正常

**原因**: DNS传播时间不同，某些DNS服务器可能还未更新

**解决方案**: 等待更长时间（最多48小时）

---

## 📝 配置示例

### 示例1: 使用子域名（推荐）

```
主机记录: productmaster
完整域名: productmaster.dpdns.org
记录类型: A
记录值: 13.239.2.255
```

### 示例2: 使用根域名

```
主机记录: @
完整域名: dpdns.org
记录类型: A
记录值: 13.239.2.255
```

**注意**: 如果使用根域名，需要确保不会影响现有的网站服务。

---

## 🚀 DNS配置完成后

DNS配置并生效后，运行以下命令配置HTTPS：

```bash
# 从本地执行
./retry_certbot_local.sh

# 或SSH到EC2执行
ssh -i "密钥路径" ubuntu@13.239.2.255
sudo bash ~/retry_certbot.sh
```

---

## 📞 需要帮助？

如果您使用的是特定DNS服务商，请告诉我：
1. DNS服务商名称（如：腾讯云、阿里云、Cloudflare等）
2. 是否有API访问密钥
3. 遇到的具体问题

我可以提供更详细的配置步骤或尝试通过API自动配置。

---

**最后更新**: 2026-01-08  
**域名**: productmaster.dpdns.org  
**目标IP**: 13.239.2.255
