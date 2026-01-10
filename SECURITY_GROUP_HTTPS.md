# 🔐 EC2安全组配置 - HTTPS支持

为支持HTTPS，需要确保EC2安全组开放以下端口：

---

## 📋 需要开放的端口

| 端口 | 协议 | 用途 | 来源 |
|------|------|------|------|
| 22 | TCP | SSH管理 | 您的IP（推荐）或 0.0.0.0/0 |
| 80 | TCP | HTTP / Let's Encrypt验证 | 0.0.0.0/0 |
| 443 | TCP | HTTPS访问 | 0.0.0.0.0/0 |

---

## 🚀 快速配置（AWS控制台）

### 步骤1: 进入安全组设置

1. 登录 [AWS EC2控制台](https://console.aws.amazon.com/ec2/)
2. 点击左侧 **实例** → 找到IP为 `13.239.2.255` 的实例
3. 点击实例ID进入详情页
4. 点击 **安全** 标签页
5. 点击安全组名称（例如：`sg-0123456789abcdef0`）

### 步骤2: 添加入站规则

1. 点击 **编辑入站规则**
2. 点击 **添加规则**

#### 规则1: HTTP (端口80)
```
类型: HTTP
协议: TCP
端口范围: 80
来源: 0.0.0.0/0
描述: Let's Encrypt验证和HTTP访问
```

#### 规则2: HTTPS (端口443)
```
类型: HTTPS
协议: TCP
端口范围: 443
来源: 0.0.0.0/0
描述: HTTPS访问
```

3. 点击 **保存规则**

---

## 🔧 使用AWS CLI配置（可选）

如果您已配置AWS CLI：

```bash
# 获取实例ID
INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=ip-address,Values=13.239.2.255" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text)

# 获取安全组ID
SG_ID=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' \
    --output text)

# 添加HTTP规则（端口80）
aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 \
    --description "HTTP for Let's Encrypt"

# 添加HTTPS规则（端口443）
aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0 \
    --description "HTTPS access"
```

---

## ✅ 验证配置

配置完成后，验证端口是否开放：

```bash
# 从本地测试HTTP
curl -I http://13.239.2.255

# 从本地测试HTTPS（配置证书后）
curl -I https://productmaster.dpdns.org

# 或在EC2上检查端口监听
ssh -i "密钥路径" ubuntu@13.239.2.255
sudo netstat -tlnp | grep -E ':(80|443)'
```

---

## 🔒 安全建议

### SSH端口（22）

**推荐配置**：只允许您的IP访问

```
类型: SSH
协议: TCP
端口范围: 22
来源: 您的IP地址/32
描述: SSH管理访问
```

**查找您的IP**：
- 访问 https://whatismyipaddress.com/
- 或运行：`curl ifconfig.me`

### HTTP/HTTPS端口（80/443）

可以开放给所有IP（0.0.0.0/0），因为：
- ✅ 这是Web服务的标准配置
- ✅ Nginx会处理安全防护
- ✅ 后端应用（Flask）只监听本地（127.0.0.1:5000）

---

## 📝 当前配置检查

运行以下命令检查当前安全组规则：

```bash
# 使用AWS CLI
aws ec2 describe-security-groups \
    --filters "Name=ip-permission.from-port,Values=80,443" \
    --query 'SecurityGroups[*].[GroupId,IpPermissions]' \
    --output table
```

或在AWS控制台查看：
1. EC2 → 安全组 → 选择您的安全组
2. 查看 **入站规则** 标签页

---

## ⚠️ 常见问题

### 问题1: 无法访问HTTP/HTTPS

**检查清单**：
- [ ] 安全组规则已添加
- [ ] 规则来源是 0.0.0.0/0（或包含您的IP）
- [ ] Nginx服务正在运行
- [ ] 端口80/443未被其他服务占用

### 问题2: Let's Encrypt验证失败

**可能原因**：
- 端口80未开放
- DNS解析未生效
- Nginx未正确配置域名

**解决方案**：
```bash
# 检查端口80是否开放
curl -I http://productmaster.dpdns.org

# 检查DNS解析
dig +short productmaster.dpdns.org

# 检查Nginx配置
sudo nginx -t
```

---

**最后更新**: 2026-01-08  
**域名**: productmaster.dpdns.org  
**EC2 IP**: 13.239.2.255
