# 🔒 HTTPS配置指南 - 方案A (Let's Encrypt)

本指南将帮助您为 `productmaster.dpdns.org` 配置HTTPS证书。

---

## 📋 前置要求

1. ✅ 域名已注册: `productmaster.dpdns.org`
2. ✅ EC2实例运行中: `13.239.2.255`
3. ✅ Nginx已安装并运行
4. ✅ 域名DNS已配置（A记录指向EC2 IP）

---

## 🚀 快速开始（自动化）

### 方法1: 使用自动化脚本（推荐）

```bash
# 1. 确保脚本有执行权限
chmod +x setup_https.sh

# 2. 运行自动化脚本
./setup_https.sh
```

脚本会自动完成：
- ✅ 检查DNS解析
- ✅ 更新Nginx配置使用域名
- ✅ 安装certbot
- ✅ 配置SSL证书
- ✅ 设置HTTP到HTTPS重定向

---

## 📝 手动配置步骤

如果您想手动配置，请按照以下步骤：

### 步骤1: 配置DNS解析

在您的DNS服务商（dpdns.org的管理后台）添加A记录：

```
主机记录: productmaster (或 @)
记录类型: A
记录值: 13.239.2.255
TTL: 默认（或600）
```

**验证DNS解析**：
```bash
# 使用dig命令
dig +short productmaster.dpdns.org

# 或使用ping
ping productmaster.dpdns.org

# 应该返回: 13.239.2.255
```

或运行检查脚本：
```bash
chmod +x check_dns.sh
./check_dns.sh
```

---

### 步骤2: 确保安全组开放端口

在AWS EC2控制台配置安全组：

1. 进入 **EC2控制台** → **实例** → 选择您的实例
2. 点击 **安全** 标签页 → 点击安全组名称
3. 点击 **编辑入站规则**
4. 添加以下规则：

| 类型 | 协议 | 端口范围 | 来源 | 描述 |
|------|------|---------|------|------|
| HTTP | TCP | 80 | 0.0.0.0/0 | Let's Encrypt验证 |
| HTTPS | TCP | 443 | 0.0.0.0/0 | HTTPS访问 |

5. 点击 **保存规则**

---

### 步骤3: SSH连接到EC2

```bash
ssh -i "/Users/mazhaohui/AWS 实例密钥/My Ubuntu Key -EC2_t3.micro_product master.pem" \
    ubuntu@13.239.2.255
```

---

### 步骤4: 更新Nginx配置使用域名

编辑Nginx配置文件：

```bash
sudo nano /etc/nginx/sites-available/product-master
```

确保 `server_name` 使用域名：

```nginx
server {
    listen 80;
    server_name productmaster.dpdns.org;  # 使用域名
    ...
}
```

测试并重启Nginx：

```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

### 步骤5: 安装Certbot

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

---

### 步骤6: 获取SSL证书

运行certbot配置HTTPS：

```bash
sudo certbot --nginx -d productmaster.dpdns.org
```

按提示操作：
1. 输入邮箱地址（用于证书到期提醒）
2. 同意服务条款（输入 `Y`）
3. 选择是否分享邮箱（可选，输入 `Y` 或 `N`）
4. 选择是否重定向HTTP到HTTPS（推荐选择 `2` - 重定向）

Certbot会自动：
- ✅ 获取SSL证书
- ✅ 配置Nginx使用HTTPS
- ✅ 设置HTTP到HTTPS重定向
- ✅ 配置自动续期

---

### 步骤7: 验证配置

#### 检查Nginx配置

```bash
sudo nginx -t
```

应该看到：
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

#### 重启Nginx

```bash
sudo systemctl restart nginx
sudo systemctl status nginx
```

#### 检查证书

```bash
sudo certbot certificates
```

应该看到您的域名和证书路径。

#### 测试自动续期

```bash
sudo certbot renew --dry-run
```

---

### 步骤8: 访问测试

在浏览器中访问：

1. **HTTPS访问**: https://productmaster.dpdns.org
   - ✅ 应该看到安全锁图标
   - ✅ 页面样式正常加载

2. **HTTP访问**: http://productmaster.dpdns.org
   - ✅ 应该自动重定向到HTTPS

---

## 🔧 故障排查

### 问题1: DNS解析失败

**症状**: `dig productmaster.dpdns.org` 返回空或错误IP

**解决方案**:
1. 检查DNS配置是否正确
2. 等待5-10分钟让DNS生效
3. 使用 `nslookup productmaster.dpdns.org` 验证

---

### 问题2: Certbot验证失败

**症状**: certbot报错 "Failed to verify domain"

**可能原因**:
- DNS未正确配置
- 安全组未开放端口80
- Nginx未运行

**解决方案**:
```bash
# 检查DNS
dig +short productmaster.dpdns.org

# 检查Nginx状态
sudo systemctl status nginx

# 检查端口监听
sudo netstat -tlnp | grep :80
```

---

### 问题3: 证书获取成功但页面无法访问

**症状**: HTTPS返回502或连接失败

**解决方案**:
```bash
# 检查Nginx错误日志
sudo tail -f /var/log/nginx/product-master-error.log

# 检查后端服务（Flask/Gunicorn）是否运行
sudo systemctl status product-master

# 检查端口5000是否监听
sudo netstat -tlnp | grep :5000
```

---

### 问题4: 浏览器仍显示"不安全"

**症状**: 配置HTTPS后浏览器仍警告

**解决方案**:
1. 清除浏览器缓存（Ctrl+Shift+R 或 Cmd+Shift+R）
2. 检查证书是否有效：
   ```bash
   sudo certbot certificates
   ```
3. 检查Nginx SSL配置：
   ```bash
   sudo cat /etc/nginx/sites-available/product-master | grep ssl
   ```

---

## 📅 证书续期

Let's Encrypt证书有效期为90天，certbot会自动续期。

### 检查自动续期

```bash
# 查看certbot定时任务
sudo systemctl status certbot.timer

# 手动测试续期
sudo certbot renew --dry-run
```

### 手动续期（如果需要）

```bash
sudo certbot renew
sudo systemctl reload nginx
```

---

## 🔐 安全建议

1. **使用强密码**: 保护EC2实例和DNS账户
2. **定期更新**: 
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
3. **监控日志**: 
   ```bash
   sudo tail -f /var/log/nginx/product-master-access.log
   ```
4. **备份配置**: 
   ```bash
   sudo cp /etc/nginx/sites-available/product-master ~/nginx-backup.conf
   ```

---

## 📚 相关文件

- `setup_https.sh` - HTTPS自动配置脚本
- `check_dns.sh` - DNS解析检查脚本
- `nginx_product_master.conf` - Nginx配置模板
- `FIX_STYLE_AND_SSL.md` - 样式和SSL修复指南

---

## ✅ 验证清单

配置完成后，请确认：

- [ ] DNS解析正确（`dig productmaster.dpdns.org` 返回 `13.239.2.255`）
- [ ] 安全组已开放端口80和443
- [ ] Nginx配置使用域名 `productmaster.dpdns.org`
- [ ] Certbot已安装
- [ ] SSL证书已获取
- [ ] HTTPS访问正常（https://productmaster.dpdns.org）
- [ ] HTTP自动重定向到HTTPS
- [ ] 浏览器显示安全锁图标
- [ ] 页面样式正常加载
- [ ] 证书自动续期配置正常

---

**最后更新**: 2026-01-08  
**域名**: productmaster.dpdns.org  
**EC2 IP**: 13.239.2.255
