# 🔧 静态文件加载和 HTTPS 问题修复指南

## 问题描述

访问 `http://13.239.2.255` 时遇到两个问题：

1. **页面没有加载样式** - CSS 和 JavaScript 文件无法加载
2. **浏览器提示不安全** - 地址栏显示"不安全"警告

## 问题原因

### 1. 样式未加载的原因

- Nginx 配置中的静态文件路径可能不正确
- 静态文件目录权限可能不正确
- Flask 的 `url_for('static', ...)` 生成的路径与 Nginx 配置不匹配

### 2. 浏览器提示不安全的原因

- 当前使用的是 **HTTP** 协议，而不是 **HTTPS**
- 现代浏览器会将所有 HTTP 连接标记为"不安全"
- 这是正常的安全提示，不是技术错误

## 解决方案

### 方案 A: 修复静态文件路径（推荐）

#### 步骤 1: 在 EC2 上运行修复脚本

```bash
# 1. 将修复脚本上传到 EC2
scp -i ~/AWS实例密钥文件夹/your-key.pem fix_nginx_static.sh ubuntu@13.239.2.255:~/

# 2. SSH 连接到 EC2
ssh -i ~/AWS实例密钥文件夹/your-key.pem ubuntu@13.239.2.255

# 3. 运行修复脚本
chmod +x ~/fix_nginx_static.sh
~/fix_nginx_static.sh
```

#### 步骤 2: 手动修复（如果脚本无法运行）

```bash
# 1. SSH 连接到 EC2
ssh -i ~/AWS实例密钥文件夹/your-key.pem ubuntu@13.239.2.255

# 2. 确认项目路径
ls -la /home/ubuntu/
# 应该看到 pythonDemo 或 ProductMaster 目录

# 3. 检查静态文件是否存在
ls -la /home/ubuntu/pythonDemo/static/css/
ls -la /home/ubuntu/pythonDemo/static/js/

# 4. 备份 Nginx 配置
sudo cp /etc/nginx/sites-available/product-master /etc/nginx/sites-available/product-master.backup

# 5. 编辑 Nginx 配置
sudo nano /etc/nginx/sites-available/product-master

# 6. 找到这一行（大约第 22 行）：
#    alias /home/ubuntu/ProductMaster/static/;
# 
# 修改为实际的项目路径，例如：
#    alias /home/ubuntu/pythonDemo/static/;

# 7. 保存并退出（Ctrl+X, Y, Enter）

# 8. 测试配置
sudo nginx -t

# 9. 修复文件权限
sudo chown -R ubuntu:www-data /home/ubuntu/pythonDemo/static
sudo chmod -R 755 /home/ubuntu/pythonDemo/static

# 10. 重启 Nginx
sudo systemctl restart nginx
```

#### 步骤 3: 验证修复

```bash
# 在 EC2 上测试静态文件访问
curl -I http://localhost/static/css/style.css
# 应该返回 200 OK

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/product-master-error.log
```

### 方案 B: 配置 HTTPS（解决"不安全"警告）

#### 选项 1: 使用 Let's Encrypt（需要域名）

如果您有域名（例如 `yourdomain.com`），可以使用免费的 Let's Encrypt SSL 证书：

```bash
# 1. 安装 Certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# 2. 获取 SSL 证书（替换 yourdomain.com）
sudo certbot --nginx -d yourdomain.com

# 3. 验证自动续期
sudo certbot renew --dry-run
```

配置完成后，访问 `https://yourdomain.com` 将显示为安全连接。

#### 选项 2: 自签名证书（仅用于测试）

⚠️ **注意**: 自签名证书仍会显示警告，仅用于测试环境。

```bash
# 1. 生成自签名证书
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx-selfsigned.key \
    -out /etc/nginx/ssl/nginx-selfsigned.crt

# 2. 创建 SSL 目录
sudo mkdir -p /etc/nginx/ssl

# 3. 更新 Nginx 配置以启用 HTTPS
# （需要修改 nginx_product_master.conf 并取消注释 HTTPS 部分）
```

#### 选项 3: 接受 HTTP 的不安全警告（开发/测试环境）

对于开发和测试环境，可以暂时接受浏览器的"不安全"警告。这不影响功能，只是浏览器提醒您连接未加密。

## 验证修复

### 1. 检查静态文件加载

在浏览器中打开开发者工具（F12），查看 Network 标签：

- ✅ **成功**: `style.css` 和 `app.js` 返回 200 状态码
- ❌ **失败**: 返回 404 或 403 错误

### 2. 检查页面样式

- ✅ **成功**: 页面显示正确的样式和布局
- ❌ **失败**: 页面显示为纯文本，没有样式

### 3. 检查 HTTPS（如果已配置）

- ✅ **成功**: 地址栏显示绿色锁图标 🔒
- ⚠️ **警告**: 使用自签名证书会显示警告，但连接是加密的

## 常见问题排查

### 问题 1: 静态文件返回 404

**原因**: Nginx 配置中的路径不正确

**解决**:
```bash
# 检查实际路径
ls -la /home/ubuntu/pythonDemo/static/css/style.css

# 更新 Nginx 配置中的路径
sudo nano /etc/nginx/sites-available/product-master
# 修改 alias 路径为实际路径
```

### 问题 2: 静态文件返回 403

**原因**: 文件权限不正确

**解决**:
```bash
# 修复权限
sudo chown -R ubuntu:www-data /home/ubuntu/pythonDemo/static
sudo chmod -R 755 /home/ubuntu/pythonDemo/static

# 确保 Nginx 可以访问
sudo chmod 755 /home/ubuntu/pythonDemo
```

### 问题 3: Nginx 配置测试失败

**原因**: 配置文件语法错误

**解决**:
```bash
# 查看详细错误
sudo nginx -t

# 检查配置文件语法
sudo nginx -T | grep -A 10 "location /static"
```

### 问题 4: 修改后仍无法加载

**原因**: 浏览器缓存

**解决**:
- 按 `Ctrl+Shift+R` (Windows/Linux) 或 `Cmd+Shift+R` (Mac) 强制刷新
- 或在浏览器中清除缓存

## 快速检查清单

- [ ] 确认项目路径正确（`/home/ubuntu/pythonDemo` 或 `/home/ubuntu/ProductMaster`）
- [ ] Nginx 配置中的 `alias` 路径正确
- [ ] 静态文件目录权限正确（755）
- [ ] Nginx 配置测试通过（`sudo nginx -t`）
- [ ] Nginx 服务已重启（`sudo systemctl restart nginx`）
- [ ] 浏览器强制刷新（`Ctrl+Shift+R`）

## 相关文件

- Nginx 配置文件: `/etc/nginx/sites-available/product-master`
- 静态文件目录: `/home/ubuntu/pythonDemo/static/`
- Nginx 错误日志: `/var/log/nginx/product-master-error.log`
- Nginx 访问日志: `/var/log/nginx/product-master-access.log`

---

**最后更新**: 2026-01-08
