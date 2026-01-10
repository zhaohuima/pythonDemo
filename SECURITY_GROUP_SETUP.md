# 🔐 EC2 安全组配置指南

## 方法 1: 使用自动化脚本（推荐）

### 前提条件
1. 安装 AWS CLI
   ```bash
   # macOS
   brew install awscli
   
   # 或下载安装包
   # https://aws.amazon.com/cli/
   ```

2. 配置 AWS 凭证
   ```bash
   aws configure
   ```
   
   需要输入：
   - AWS Access Key ID
   - AWS Secret Access Key  
   - Default region (例如: `ap-southeast-1` 或 `us-east-1`)
   - Default output format (`json`)

3. 运行配置脚本
   ```bash
   ./configure_security_group.sh
   ```

脚本会自动：
- 查找您的 EC2 实例
- 获取安全组 ID
- 添加端口 5000 的入站规则
- 可选择只允许您的 IP 或所有 IP

---

## 方法 2: 手动在 AWS 控制台配置

### 步骤详解

#### 1. 登录 AWS 控制台
访问：https://console.aws.amazon.com/ec2/

#### 2. 找到您的实例
- 在左侧菜单点击 "Instances"（实例）
- 找到 IP 为 `13.239.2.255` 的实例

#### 3. 进入安全组设置
- 点击实例 ID 进入详情页
- 点击 "Security"（安全）标签页
- 点击安全组名称（例如：`sg-0123456789abcdef0`）

#### 4. 添加入站规则
- 点击 "Edit inbound rules"（编辑入站规则）
- 点击 "Add rule"（添加规则）
- 配置如下：
  ```
  类型: Custom TCP
  端口范围: 5000
  来源: 
    - 选项 A: My IP（推荐，只允许您的 IP）
    - 选项 B: 0.0.0.0/0（允许所有 IP，仅用于测试）
  描述: Product Master Web App
  ```
- 点击 "Save rules"（保存规则）

#### 5. 验证
等待几秒钟，然后访问：`http://13.239.2.255:5000`

---

## 方法 3: 使用 AWS CLI 命令（手动）

如果您已配置 AWS CLI，可以直接运行：

### 获取实例和安全组信息
```bash
# 获取实例 ID
INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=ip-address,Values=13.239.2.255" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text)

# 获取安全组 ID
SG_ID=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' \
    --output text)

echo "实例 ID: $INSTANCE_ID"
echo "安全组 ID: $SG_ID"
```

### 添加规则（允许所有 IP）
```bash
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 5000 \
    --cidr 0.0.0.0/0 \
    --description "Product Master Web App"
```

### 添加规则（只允许您的 IP）
```bash
# 获取您的 IP
MY_IP=$(curl -s https://api.ipify.org)

# 添加规则
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 5000 \
    --cidr ${MY_IP}/32 \
    --description "Product Master Web App - My IP"
```

---

## 🔍 验证配置

### 检查安全组规则
```bash
aws ec2 describe-security-groups \
    --group-ids $SG_ID \
    --query 'SecurityGroups[0].IpPermissions[?FromPort==`5000`]' \
    --output json
```

### 测试连接
```bash
# 测试端口是否开放
curl -v http://13.239.2.255:5000

# 或使用 telnet
telnet 13.239.2.255 5000
```

---

## ⚠️ 常见问题

### 1. 仍然无法访问
- 检查安全组规则是否已保存
- 等待 1-2 分钟让规则生效
- 确认应用正在运行：`sudo systemctl status product-master`
- 检查防火墙：`sudo ufw status`

### 2. 权限错误
如果使用 AWS CLI 时遇到权限错误，确保您的 IAM 用户有以下权限：
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeSecurityGroups",
                "ec2:AuthorizeSecurityGroupIngress"
            ],
            "Resource": "*"
        }
    ]
}
```

### 3. 规则已存在
如果提示规则已存在，可以：
- 查看现有规则：`aws ec2 describe-security-groups --group-ids $SG_ID`
- 删除旧规则后重新添加
- 或直接使用现有规则

---

## 🔒 安全建议

1. **生产环境**：只允许特定 IP 访问（使用 `/32` CIDR）
2. **测试环境**：可以使用 `0.0.0.0/0`，但测试完成后建议删除
3. **定期检查**：定期审查安全组规则，删除不需要的规则

---

## 📞 需要帮助？

如果遇到问题：
1. 检查 AWS CLI 配置：`aws configure list`
2. 检查实例状态：AWS 控制台 → EC2 → 实例
3. 查看安全组规则：AWS 控制台 → EC2 → 安全组
