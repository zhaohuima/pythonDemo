# 🔐 Nginx 反向代理配置说明

## 架构概览

```
用户浏览器
     │
     ▼
┌─────────────────────────────────────┐
│         AWS EC2 安全组               │
│    ✅ 端口 22 (SSH)                  │
│    ✅ 端口 80 (HTTP)                 │
│    ✅ 端口 443 (HTTPS - 预留)        │
│    ❌ 端口 5000 (已关闭公网访问)      │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│           Nginx (端口 80)            │
│  • 反向代理                          │
│  • 请求限流 (10 req/s)              │
│  • 安全头                            │
│  • 静态文件缓存                      │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│     Gunicorn (127.0.0.1:5000)       │
│  • 生产级 WSGI 服务器                │
│  • 2 个工作进程                      │
│  • 仅监听本地回环地址                │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│         Flask 应用                   │
│      Product Master                  │
└─────────────────────────────────────┘
```

## 安全改进

| 改进项 | 之前 | 之后 |
|--------|------|------|
| **服务器类型** | Flask 开发服务器 | Gunicorn 生产服务器 |
| **暴露端口** | 5000（直接暴露） | 80（Nginx 代理） |
| **访问控制** | 无 | Nginx 请求限流 |
| **安全头** | 无 | X-Frame-Options, X-XSS-Protection 等 |
| **静态文件** | Flask 处理 | Nginx 直接提供（带缓存） |
| **攻击面** | 后端直接暴露 | 隐藏在 Nginx 后 |

## 访问地址

### 新地址（推荐）
```
http://13.239.2.255
```

### 旧地址（已禁用）
```
http://13.239.2.255:5000  ❌ 无法从公网访问
```

## 服务管理

### Nginx
```bash
# 查看状态
sudo systemctl status nginx

# 重启
sudo systemctl restart nginx

# 查看日志
sudo tail -f /var/log/nginx/product-master-access.log
sudo tail -f /var/log/nginx/product-master-error.log

# 测试配置
sudo nginx -t
```

### Gunicorn (Product Master)
```bash
# 查看状态
sudo systemctl status product-master

# 重启
sudo systemctl restart product-master

# 查看日志
sudo journalctl -u product-master -f
```

## 配置文件位置

| 文件 | 路径 |
|------|------|
| Nginx 主配置 | `/etc/nginx/nginx.conf` |
| 站点配置 | `/etc/nginx/sites-available/product-master` |
| Nginx 日志 | `/var/log/nginx/` |
| Gunicorn 服务 | `/etc/systemd/system/product-master.service` |
| 应用代码 | `/home/ubuntu/ProductMaster/` |

## Nginx 配置详解

### 请求限流
```nginx
# 每秒最多 10 个请求，突发 20 个
limit_req zone=api_limit burst=20 nodelay;

# 每 IP 最多 10 个并发连接
limit_conn conn_limit 10;
```

### 安全头
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;        # 防止点击劫持
add_header X-Content-Type-Options "nosniff" always;    # 防止 MIME 嗅探
add_header X-XSS-Protection "1; mode=block" always;    # XSS 防护
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### 超时设置
```nginx
proxy_connect_timeout 60s;   # 连接超时
proxy_send_timeout 300s;     # 发送超时（LLM 调用可能较慢）
proxy_read_timeout 300s;     # 读取超时
```

## 添加 HTTPS（可选）

如果有域名，可以使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书（替换 your-domain.com）
sudo certbot --nginx -d your-domain.com

# 自动续期（已自动配置）
sudo certbot renew --dry-run
```

## 故障排查

### 1. 502 Bad Gateway
```bash
# 检查 Gunicorn 是否运行
sudo systemctl status product-master

# 检查端口监听
ss -tlnp | grep 5000

# 查看 Gunicorn 日志
sudo journalctl -u product-master -n 50
```

### 2. 504 Gateway Timeout
- LLM API 调用超时
- 增加 Nginx 超时设置
- 检查 API 服务状态

### 3. 403 Forbidden
```bash
# 检查文件权限
ls -la /home/ubuntu/ProductMaster/static/

# 修复权限
sudo chown -R ubuntu:www-data /home/ubuntu/ProductMaster/
sudo chmod -R 755 /home/ubuntu/ProductMaster/
```

### 4. Nginx 配置错误
```bash
# 测试配置语法
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

## 性能优化建议

1. **启用 Gzip 压缩**
   ```nginx
   gzip on;
   gzip_types text/plain text/css application/json application/javascript;
   ```

2. **增加工作进程**
   编辑 `/etc/systemd/system/product-master.service`：
   ```
   ExecStart=... --workers 4 ...
   ```

3. **使用 Unix Socket**（可选）
   更高性能的本地通信方式

## 安全组规则

当前配置：
| 端口 | 协议 | 来源 | 用途 |
|------|------|------|------|
| 22 | TCP | 您的 IP | SSH 管理 |
| 80 | TCP | 0.0.0.0/0 | HTTP |
| 443 | TCP | 0.0.0.0/0 | HTTPS（预留） |

---

**配置日期**: 2026-01-08
**版本**: 1.0.0
