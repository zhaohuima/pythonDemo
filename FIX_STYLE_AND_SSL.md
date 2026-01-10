# 🔧 修复样式加载和HTTPS配置指南

## 问题描述

1. **样式没有加载**：访问 `http://13.239.2.255` 时，CSS文件无法加载
2. **浏览器显示"不安全"**：使用HTTP协议导致浏览器警告

## 解决方案

### 问题1：修复样式加载问题

样式无法加载通常是因为Nginx没有正确配置静态文件路径。需要确保Nginx直接提供静态文件，而不是通过Flask代理。

#### 步骤1：检查当前Nginx配置

```bash
# SSH连接到EC2
ssh -i "密钥路径" ubuntu@13.239.2.255

# 检查Nginx配置是否存在
sudo cat /etc/nginx/sites-available/product-master

# 检查Nginx是否运行
sudo systemctl status nginx
```

#### 步骤2：创建/更新Nginx配置

将项目中的 `nginx_product_master.conf` 文件上传到EC2，或直接在EC2上创建：

```bash
# 在EC2上创建配置文件
sudo nano /etc/nginx/sites-available/product-master
```

复制 `nginx_product_master.conf` 的内容到该文件。

**重要**：确保静态文件路径正确：
```nginx
location /static/ {
    alias /home/ubuntu/ProductMaster/static/;  # 确保路径正确
    ...
}
```

#### 步骤3：检查静态文件权限

```bash
# 检查静态文件是否存在
ls -la /home/ubuntu/ProductMaster/static/css/style.css

# 如果不存在，检查项目目录
ls -la /home/ubuntu/ProductMaster/

# 修复权限（如果需要）
sudo chown -R ubuntu:www-data /home/ubuntu/ProductMaster/
sudo chmod -R 755 /home/ubuntu/ProductMaster/
sudo chmod -R 644 /home/ubuntu/ProductMaster/static/
```

#### 步骤4：启用配置并重启Nginx

```bash
# 创建软链接（如果还没有）
sudo ln -s /etc/nginx/sites-available/product-master /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 如果测试通过，重启Nginx
sudo systemctl restart nginx

# 检查状态
sudo systemctl status nginx
```

#### 步骤5：验证静态文件访问

在浏览器中访问：
```
http://13.239.2.255/static/css/style.css
```

如果能看到CSS内容，说明静态文件配置成功。

### 问题2：配置HTTPS（解决"不安全"提示）

#### 方案A：使用Let's Encrypt免费证书（推荐，需要域名）

如果您有域名指向 `13.239.2.255`：

```bash
# 1. 安装Certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# 2. 获取SSL证书（替换 your-domain.com 为您的域名）
sudo certbot --nginx -d your-domain.com

# 3. 测试自动续期
sudo certbot renew --dry-run
```

Certbot会自动：
- 获取SSL证书
- 配置Nginx使用HTTPS
- 设置HTTP到HTTPS的重定向
- 配置自动续期

#### 方案B：使用自签名证书（仅用于测试，浏览器仍会警告）

```bash
# 1. 创建证书目录
sudo mkdir -p /etc/nginx/ssl

# 2. 生成自签名证书
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/product-master.key \
    -out /etc/nginx/ssl/product-master.crt

# 填写证书信息（可以全部回车使用默认值）
```

然后更新Nginx配置，取消注释HTTPS部分并修改证书路径：

```nginx
server {
    listen 443 ssl http2;
    server_name 13.239.2.255;
    
    ssl_certificate /etc/nginx/ssl/product-master.crt;
    ssl_certificate_key /etc/nginx/ssl/product-master.key;
    
    # ... 其他配置
}
```

#### 方案C：使用Cloudflare（推荐，无需服务器配置）

1. 注册Cloudflare账号
2. 添加您的域名到Cloudflare
3. 配置DNS，将域名指向 `13.239.2.255`
4. 在Cloudflare中启用"始终使用HTTPS"
5. Cloudflare会自动提供HTTPS，无需在服务器上配置证书

### 快速修复脚本

创建一个修复脚本 `fix_nginx.sh`：

```bash
#!/bin/bash

set -e

echo "🔧 修复Nginx配置..."

# 检查Nginx是否安装
if ! command -v nginx &> /dev/null; then
    echo "📦 安装Nginx..."
    sudo apt update
    sudo apt install -y nginx
fi

# 备份现有配置
if [ -f /etc/nginx/sites-available/product-master ]; then
    echo "💾 备份现有配置..."
    sudo cp /etc/nginx/sites-available/product-master /etc/nginx/sites-available/product-master.backup.$(date +%Y%m%d_%H%M%S)
fi

# 创建配置文件（需要手动编辑路径）
echo "📝 创建Nginx配置..."
# 这里需要手动复制 nginx_product_master.conf 的内容

# 检查静态文件目录
PROJECT_DIR="/home/ubuntu/ProductMaster"
if [ ! -d "$PROJECT_DIR/static" ]; then
    echo "⚠️  警告: 静态文件目录不存在: $PROJECT_DIR/static"
    echo "请检查项目目录路径是否正确"
fi

# 修复权限
echo "🔐 修复文件权限..."
sudo chown -R ubuntu:www-data "$PROJECT_DIR"
sudo chmod -R 755 "$PROJECT_DIR"
sudo chmod -R 644 "$PROJECT_DIR/static/" 2>/dev/null || true

# 启用配置
echo "🔗 启用Nginx配置..."
sudo ln -sf /etc/nginx/sites-available/product-master /etc/nginx/sites-enabled/

# 测试配置
echo "🧪 测试Nginx配置..."
sudo nginx -t

# 重启Nginx
echo "🔄 重启Nginx..."
sudo systemctl restart nginx

echo "✅ 完成！"
echo ""
echo "📋 下一步："
echo "1. 访问 http://13.239.2.255/static/css/style.css 验证静态文件"
echo "2. 访问 http://13.239.2.255 查看页面样式是否正常"
echo "3. 如需HTTPS，参考上面的HTTPS配置指南"
```

## 故障排查

### 样式仍然无法加载

1. **检查浏览器控制台**
   - 按F12打开开发者工具
   - 查看Console和Network标签
   - 检查CSS文件的HTTP状态码（应该是200）

2. **检查Nginx错误日志**
   ```bash
   sudo tail -f /var/log/nginx/product-master-error.log
   ```

3. **检查静态文件路径**
   ```bash
   # 确认文件存在
   ls -la /home/ubuntu/ProductMaster/static/css/style.css
   
   # 测试Nginx是否能访问
   sudo -u www-data cat /home/ubuntu/ProductMaster/static/css/style.css
   ```

4. **检查Flask应用中的静态文件URL**
   - 在浏览器中查看页面源代码
   - 检查 `<link>` 标签中的CSS路径
   - 应该是 `/static/css/style.css` 而不是相对路径

### HTTPS配置后仍显示不安全

1. **检查证书是否有效**
   ```bash
   sudo openssl x509 -in /etc/letsencrypt/live/your-domain.com/cert.pem -text -noout
   ```

2. **检查Nginx SSL配置**
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

3. **清除浏览器缓存**
   - 强制刷新：Ctrl+Shift+R (Windows/Linux) 或 Cmd+Shift+R (Mac)

## 验证清单

- [ ] Nginx配置已更新并启用
- [ ] 静态文件路径正确
- [ ] 文件权限正确（755目录，644文件）
- [ ] Nginx配置测试通过
- [ ] Nginx服务运行正常
- [ ] 可以直接访问 `/static/css/style.css`
- [ ] 页面样式正常显示
- [ ] HTTPS配置完成（如果适用）
- [ ] 浏览器不再显示"不安全"警告

## 相关文件

- `nginx_product_master.conf` - Nginx配置文件模板
- `NGINX_SETUP.md` - Nginx设置详细文档
- `deploy_to_ec2.sh` - 部署脚本

---

**最后更新**: 2026-01-08
