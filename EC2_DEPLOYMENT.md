# 🚀 AWS EC2 部署指南

本指南将帮助您将 Product Master 项目部署到 AWS EC2 实例。

## 📋 前置要求

- AWS EC2 实例运行中
- EC2 公有 IP: `13.239.2.255`
- 系统: Ubuntu Server 24.04 LTS
- 本地已安装 SSH 客户端
- 已获得 EC2 密钥文件

---

## 🔑 第一步：准备密钥文件

密钥文件位置：
```
/Users/mazhaohui/AWS 实例密钥/My Ubuntu Key -EC2_t3.micro_product master.pem
```

设置正确的权限：
```bash
chmod 400 "/Users/mazhaohui/AWS 实例密钥/My Ubuntu Key -EC2_t3.micro_product master.pem"
```

---

## 🔐 第二步：配置 EC2 安全组

确保 EC2 安全组允许以下端口：

1. **SSH (端口 22)** - 用于连接和管理
2. **HTTP (端口 5000)** - 用于 Web 应用访问

在 AWS 控制台：
1. 进入 EC2 → 安全组
2. 添加入站规则：
   - 类型: SSH, 端口: 22, 来源: 您的 IP 或 0.0.0.0/0
   - 类型: 自定义 TCP, 端口: 5000, 来源: 0.0.0.0/0 (或您的 IP)

---

## 📤 第三步：部署项目到 EC2

### 方法 A: 使用自动部署脚本（推荐）

```bash
# 在项目根目录执行
chmod +x deploy_to_ec2.sh
./deploy_to_ec2.sh
```

脚本会自动：
- 测试 EC2 连接
- 创建项目目录
- 同步项目文件到 EC2

### 方法 B: 手动部署

#### 1. 测试连接

```bash
ssh -i "/Users/mazhaohui/AWS 实例密钥/My Ubuntu Key -EC2_t3.micro_product master.pem" \
    ubuntu@13.239.2.255
```

如果连接成功，您会看到 Ubuntu 欢迎信息。

#### 2. 在 EC2 上创建项目目录

```bash
ssh -i "/Users/mazhaohui/AWS 实例密钥/My Ubuntu Key -EC2_t3.micro_product master.pem" \
    ubuntu@13.239.2.255 "mkdir -p ~/ProductMaster"
```

#### 3. 同步项目文件

```bash
rsync -avz --progress \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude 'logs/*' \
    --exclude 'outputs/*' \
    --exclude '.DS_Store' \
    -e "ssh -i \"/Users/mazhaohui/AWS 实例密钥/My Ubuntu Key -EC2_t3.micro_product master.pem\"" \
    ./ ubuntu@13.239.2.255:~/ProductMaster/
```

---

## ⚙️ 第四步：在 EC2 上设置环境

### 1. SSH 连接到 EC2

```bash
ssh -i "/Users/mazhaohui/AWS 实例密钥/My Ubuntu Key -EC2_t3.micro_product master.pem" \
    ubuntu@13.239.2.255
```

### 2. 运行设置脚本

```bash
cd ~/ProductMaster
chmod +x deploy_setup_ec2.sh
./deploy_setup_ec2.sh
```

或者手动执行：

```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装 Python 和工具
sudo apt install -y python3 python3-pip python3-venv git curl

# 进入项目目录
cd ~/ProductMaster

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 创建必要目录
mkdir -p logs outputs
```

### 3. 配置 API 密钥

编辑 `config.py` 文件：

```bash
nano config.py
```

设置您的 API 密钥：
```python
API_KEY = "your-api-key-here"
API_BASE_URL = "https://api.siliconflow.cn/v1"
MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
```

---

## 🚀 第五步：启动 Web 应用

### 方法 A: 直接运行（测试用）

```bash
cd ~/ProductMaster
source venv/bin/activate
python3 web_app.py
```

应用将在 `http://13.239.2.255:5000` 运行。

**注意**: 这种方式在 SSH 断开后会停止。建议使用方法 B。

### 方法 B: 使用 systemd 服务（生产环境）

#### 创建服务文件

```bash
sudo nano /etc/systemd/system/product-master.service
```

粘贴以下内容：

```ini
[Unit]
Description=Product Master Web Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ProductMaster
Environment="PATH=/home/ubuntu/ProductMaster/venv/bin"
ExecStart=/home/ubuntu/ProductMaster/venv/bin/python3 /home/ubuntu/ProductMaster/web_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 启动服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start product-master

# 查看状态
sudo systemctl status product-master

# 设置开机自启
sudo systemctl enable product-master
```

#### 查看日志

```bash
# 实时查看日志
sudo journalctl -u product-master -f

# 查看最近 100 行日志
sudo journalctl -u product-master -n 100
```

---

## 🌐 第六步：访问应用

在浏览器中访问：
```
http://13.239.2.255:5000
```

---

## 🔧 常用管理命令

### 服务管理

```bash
# 启动服务
sudo systemctl start product-master

# 停止服务
sudo systemctl stop product-master

# 重启服务
sudo systemctl restart product-master

# 查看状态
sudo systemctl status product-master

# 查看日志
sudo journalctl -u product-master -f
```

### 更新代码

```bash
# 在本地执行（从项目目录）
./deploy_to_ec2.sh

# 在 EC2 上重启服务
ssh -i "密钥路径" ubuntu@13.239.2.255 "sudo systemctl restart product-master"
```

### 查看应用日志

```bash
# systemd 日志
sudo journalctl -u product-master -f

# 应用日志文件
tail -f ~/ProductMaster/logs/product_master_$(date +%Y%m%d).log
```

---

## 🔒 安全建议

1. **使用 Nginx 反向代理**（推荐）
   - 配置 HTTPS
   - 隐藏后端端口
   - 更好的安全性和性能

2. **限制安全组访问**
   - 只允许特定 IP 访问端口 5000
   - 使用 VPN 或堡垒机

3. **定期更新系统**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **使用环境变量存储敏感信息**
   - 不要将 API 密钥提交到代码仓库
   - 使用 `.env` 文件或 AWS Secrets Manager

---

## 🐛 故障排查

### 无法连接 EC2

1. 检查安全组是否允许 SSH (端口 22)
2. 检查密钥文件权限：`chmod 400 密钥文件`
3. 检查 EC2 实例状态是否运行中

### 应用无法访问

1. 检查安全组是否允许端口 5000
2. 检查服务状态：`sudo systemctl status product-master`
3. 查看日志：`sudo journalctl -u product-master -n 50`
4. 检查防火墙：`sudo ufw status`

### 服务启动失败

1. 检查 Python 虚拟环境是否正确
2. 检查依赖是否安装：`pip list`
3. 检查配置文件是否正确
4. 查看详细错误：`sudo journalctl -u product-master -n 100`

---

## 📞 支持

如遇问题，请检查：
- 应用日志：`~/ProductMaster/logs/`
- systemd 日志：`sudo journalctl -u product-master`
- EC2 系统日志：AWS 控制台 → EC2 → 实例 → 监控

---

## ✅ 部署检查清单

- [ ] 密钥文件权限已设置 (400)
- [ ] EC2 安全组已配置（SSH 22, HTTP 5000）
- [ ] 项目文件已同步到 EC2
- [ ] Python 环境和依赖已安装
- [ ] API 密钥已配置
- [ ] systemd 服务已创建并启动
- [ ] 应用可以正常访问
- [ ] 日志记录正常

---

**部署完成后，您的 Product Master 应用将在 `http://13.239.2.255:5000` 运行！** 🎉
