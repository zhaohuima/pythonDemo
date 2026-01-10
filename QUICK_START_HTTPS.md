# 🚀 HTTPS配置快速开始

由于本地网络限制，请按照以下步骤手动配置HTTPS：

---

## 方法1: 使用远程脚本（推荐）

### 步骤1: 上传脚本到EC2

```bash
# 在本地项目目录执行
scp -i "/Users/mazhaohui/AWS 实例密钥/My Ubuntu Key -EC2_t3.micro_product master.pem" \
    setup_https_remote.sh \
    ubuntu@13.239.2.255:/home/ubuntu/
```

### 步骤2: SSH连接到EC2

```bash
ssh -i "/Users/mazhaohui/AWS 实例密钥/My Ubuntu Key -EC2_t3.micro_product master.pem" \
    ubuntu@13.239.2.255
```

### 步骤3: 运行配置脚本

```bash
# 进入home目录
cd ~

# 给脚本执行权限
chmod +x setup_https_remote.sh

# 运行脚本（需要sudo）
sudo bash setup_https_remote.sh
```

脚本会自动完成所有配置！

---

## 方法2: 手动配置（逐步执行）

### 步骤1: 确保DNS已配置

在DNS服务商添加A记录：
- 主机记录: `productmaster` (或 `@`)
- 记录类型: `A`
- 记录值: `13.239.2.255`

等待5-10分钟让DNS生效。

### 步骤2: 配置EC2安全组

在AWS控制台：
1. EC2 → 实例 → 选择您的实例
2. 安全 → 编辑入站规则
3. 添加：
   - HTTP (80), 来源: 0.0.0.0/0
   - HTTPS (443), 来源: 0.0.0.0/0

### 步骤3: SSH连接到EC2

```bash
ssh -i "/Users/mazhaohui/AWS 实例密钥/My Ubuntu Key -EC2_t3.micro_product master.pem" \
    ubuntu@13.239.2.255
```

### 步骤4: 更新Nginx配置使用域名

```bash
# 编辑Nginx配置
sudo nano /etc/nginx/sites-available/product-master

# 确保server_name使用域名
server_name productmaster.dpdns.org;

# 测试并重启
sudo nginx -t
sudo systemctl restart nginx
```

### 步骤5: 安装certbot

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

### 步骤6: 配置SSL证书

```bash
sudo certbot --nginx -d productmaster.dpdns.org
```

按提示操作：
1. 输入邮箱地址
2. 同意服务条款 (Y)
3. 选择重定向HTTP到HTTPS (推荐选择2)

### 步骤7: 验证

访问：
- https://productmaster.dpdns.org ✅ 应该看到安全锁
- http://productmaster.dpdns.org ✅ 应该自动重定向到HTTPS

---

## 故障排查

### 问题1: DNS未生效

```bash
# 在EC2上检查DNS
dig +short productmaster.dpdns.org

# 应该返回: 13.239.2.255
```

### 问题2: Certbot验证失败

检查：
- 安全组是否开放端口80
- DNS是否正确解析
- Nginx是否运行

```bash
sudo systemctl status nginx
sudo netstat -tlnp | grep :80
```

### 问题3: 证书获取成功但无法访问

检查：
- Nginx配置是否正确
- 后端服务是否运行

```bash
sudo nginx -t
sudo systemctl status product-master
sudo tail -f /var/log/nginx/product-master-error.log
```

---

## 相关文件

- `setup_https_remote.sh` - 在EC2上运行的配置脚本
- `HTTPS_SETUP_GUIDE.md` - 详细配置指南
- `SECURITY_GROUP_HTTPS.md` - 安全组配置说明

---

**推荐使用方法1（远程脚本）**，最简单快捷！
