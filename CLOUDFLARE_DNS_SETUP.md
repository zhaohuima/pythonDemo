# 🌐 Cloudflare DNS配置指南

使用Cloudflare API自动配置DNS A记录。

---

## 🚀 快速开始（自动化）

### 方法1: 使用自动化脚本（推荐）

```bash
# 1. 确保脚本有执行权限
chmod +x setup_cloudflare_dns.sh

# 2. 运行脚本
./setup_cloudflare_dns.sh
```

脚本会自动：
- ✅ 获取Cloudflare Zone ID
- ✅ 检查现有DNS记录
- ✅ 创建或更新A记录
- ✅ 验证配置结果

---

## 🔑 获取Cloudflare API Token

### 步骤1: 登录Cloudflare

访问：https://dash.cloudflare.com/

### 步骤2: 创建API Token

1. 点击右上角 **头像** → **My Profile**
2. 进入 **API Tokens** 标签页
3. 点击 **Create Token**
4. 选择 **Edit zone DNS** 模板
5. 配置权限：
   - **Zone** → **DNS** → **Edit**
   - **Zone Resources** → 选择 **Include** → **Specific zone** → 选择 `dpdns.org`
6. 点击 **Continue to summary**
7. 点击 **Create Token**
8. **复制Token**（只显示一次，请保存好）

### 步骤3: 使用Token

运行脚本时，输入刚才复制的Token即可。

---

## 📝 手动配置（Cloudflare控制台）

如果您不想使用API，也可以手动配置：

### 步骤1: 登录Cloudflare控制台

访问：https://dash.cloudflare.com/

### 步骤2: 选择域名

点击域名 `dpdns.org`

### 步骤3: 进入DNS设置

点击左侧菜单 **DNS** → **Records**

### 步骤4: 添加A记录

1. 点击 **Add record**
2. 填写：
   - **Type**: `A`
   - **Name**: `productmaster`
   - **IPv4 address**: `13.239.2.255`
   - **Proxy status**: `DNS only` (灰色云朵，不启用代理)
   - **TTL**: `Auto`
3. 点击 **Save**

### 步骤5: 验证

等待1-5分钟，然后验证DNS：

```bash
dig +short productmaster.dpdns.org
# 应该返回: 13.239.2.255
```

---

## ✅ 验证DNS配置

### 方法1: 使用脚本

```bash
./check_dns_status.sh
```

### 方法2: 使用dig命令

```bash
dig +short productmaster.dpdns.org
```

**期望输出**: `13.239.2.255`

### 方法3: 使用nslookup

```bash
nslookup productmaster.dpdns.org
```

### 方法4: 在线工具

访问以下网站查询：
- https://www.whatsmydns.net/
- https://dnschecker.org/

输入 `productmaster.dpdns.org`，应该返回 `13.239.2.255`

---

## 🔧 故障排查

### 问题1: API Token无效

**错误信息**: `API error: Invalid API Token`

**解决方案**:
1. 检查Token是否正确复制（没有多余空格）
2. 确认Token有权限访问 `dpdns.org`
3. 重新创建Token

### 问题2: 找不到Zone ID

**错误信息**: `Unable to find Zone ID`

**解决方案**:
1. 确认域名 `dpdns.org` 在您的Cloudflare账户中
2. 检查API Token权限是否包含该域名
3. 确认域名状态为"Active"

### 问题3: DNS记录创建失败

**可能原因**:
- 记录已存在
- API权限不足
- 域名配置错误

**解决方案**:
1. 检查现有记录：在Cloudflare控制台查看DNS记录
2. 如果记录存在，脚本会自动更新
3. 确认API Token权限

### 问题4: DNS解析未生效

**解决方案**:
1. 等待1-5分钟（Cloudflare通常很快）
2. 清除本地DNS缓存：
   ```bash
   # macOS
   sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
   
   # Linux
   sudo systemd-resolve --flush-caches
   ```
3. 使用不同DNS服务器查询：
   ```bash
   dig @8.8.8.8 +short productmaster.dpdns.org
   dig @1.1.1.1 +short productmaster.dpdns.org
   ```

---

## 📋 DNS配置完成后

DNS配置并生效后，运行HTTPS配置：

```bash
# 检查DNS状态
./check_dns_status.sh

# 如果DNS已生效，配置HTTPS
./retry_certbot_local.sh
```

---

## 🔐 安全建议

1. **保护API Token**:
   - 不要将Token提交到代码仓库
   - 使用环境变量存储Token
   - 定期轮换Token

2. **使用最小权限**:
   - API Token只授予必要的权限
   - 只允许访问特定域名

3. **监控DNS记录**:
   - 定期检查DNS记录
   - 设置DNS变更通知

---

## 📚 相关文件

- `setup_cloudflare_dns.sh` - Cloudflare DNS自动配置脚本
- `check_dns_status.sh` - DNS状态检查脚本
- `retry_certbot_local.sh` - HTTPS配置脚本
- `DNS_SETUP_GUIDE.md` - 通用DNS配置指南

---

## 🎯 完整流程

1. **配置DNS**:
   ```bash
   ./setup_cloudflare_dns.sh
   ```

2. **等待DNS生效** (1-5分钟):
   ```bash
   ./check_dns_status.sh
   ```

3. **配置HTTPS**:
   ```bash
   ./retry_certbot_local.sh
   ```

4. **验证HTTPS**:
   - 访问 https://productmaster.dpdns.org
   - 应该看到安全锁图标 ✅

---

**最后更新**: 2026-01-08  
**域名**: productmaster.dpdns.org  
**DNS服务商**: Cloudflare
