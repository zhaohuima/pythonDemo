# 🔧 AWS CLI 安装和配置指南

## 快速安装步骤

### 方法 1: 使用安装脚本（推荐）

```bash
cd /Users/mazhaohui/pythonDemo
./install_aws_cli.sh
```

脚本会自动：
1. 下载 AWS CLI 安装包
2. 提示您输入密码进行安装
3. 验证安装结果

### 方法 2: 手动安装

#### 步骤 1: 下载安装包
```bash
cd /tmp
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
```

#### 步骤 2: 安装
```bash
sudo installer -pkg /tmp/AWSCLIV2.pkg -target /
```

#### 步骤 3: 验证
```bash
aws --version
```

---

## 配置 AWS 凭证

安装完成后，需要配置 AWS 凭证：

```bash
aws configure
```

需要输入以下信息：

1. **AWS Access Key ID**
   - 在 AWS 控制台 → IAM → 用户 → 安全凭证
   - 创建访问密钥（如果还没有）

2. **AWS Secret Access Key**
   - 与 Access Key ID 一起创建
   - ⚠️ 只显示一次，请妥善保存

3. **Default region name**
   - 例如：`ap-southeast-1`（新加坡）
   - 或：`us-east-1`（美国东部）
   - 根据您的 EC2 实例所在区域选择

4. **Default output format**
   - 输入：`json`

### 示例配置
```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: ap-southeast-1
Default output format [None]: json
```

---

## 验证配置

```bash
# 检查配置
aws configure list

# 测试连接
aws sts get-caller-identity
```

如果成功，会显示您的 AWS 账户信息。

---

## 获取 AWS 访问密钥

如果您还没有访问密钥：

1. 登录 AWS 控制台
2. 点击右上角用户名 → "Security credentials"（安全凭证）
3. 在 "Access keys" 部分点击 "Create access key"
4. 选择用途（例如：Command Line Interface (CLI)）
5. 下载或复制 Access Key ID 和 Secret Access Key

⚠️ **重要**：Secret Access Key 只显示一次，请妥善保存！

---

## 完成配置后

配置完成后，运行安全组配置脚本：

```bash
cd /Users/mazhaohui/pythonDemo
./configure_security_group.sh
```

脚本会自动：
- 查找您的 EC2 实例
- 配置安全组规则
- 开放端口 5000

---

## 故障排查

### 问题 1: 找不到 aws 命令
```bash
# 检查安装位置
which aws

# 如果未找到，可能需要添加到 PATH
export PATH="/usr/local/bin:$PATH"
```

### 问题 2: 权限错误
确保您的 IAM 用户有以下权限：
- `ec2:DescribeInstances`
- `ec2:DescribeSecurityGroups`
- `ec2:AuthorizeSecurityGroupIngress`

### 问题 3: 区域不匹配
确保配置的区域与 EC2 实例所在区域一致。

---

## 下一步

1. ✅ 安装 AWS CLI
2. ✅ 配置 AWS 凭证
3. ✅ 运行安全组配置脚本
4. ✅ 访问应用：http://13.239.2.255:5000
