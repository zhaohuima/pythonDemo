# 🔑 获取 AWS Access Key 指南

## 重要说明

AWS CLI 需要的是 **Access Key ID** 和 **Secret Access Key**，不是控制台登录密码。

您的信息：
- 邮箱：***REMOVED***
- 密码：***REMOVED***（用于登录控制台）

## 获取 Access Key 的步骤

### 方法 1: 通过 AWS 控制台（推荐）

1. **登录 AWS 控制台**
   - 访问：https://console.aws.amazon.com/
   - 使用邮箱：***REMOVED***
   - 密码：***REMOVED***

2. **进入 IAM 服务**
   - 在搜索框输入 "IAM"
   - 点击 "IAM" 服务

3. **获取访问密钥**
   - 点击右上角您的用户名（***REMOVED***）
   - 选择 "Security credentials"（安全凭证）
   - 向下滚动到 "Access keys" 部分
   - 点击 "Create access key"（创建访问密钥）

4. **选择用途**
   - 选择 "Command Line Interface (CLI)"
   - 勾选确认框
   - 点击 "Next"

5. **下载密钥**
   - 可选：添加描述标签
   - 点击 "Create access key"
   - ⚠️ **重要**：立即下载或复制以下信息：
     - **Access Key ID**（例如：AKIAIOSFODNN7EXAMPLE）
     - **Secret Access Key**（例如：wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY）
   - ⚠️ Secret Access Key **只显示一次**，请妥善保存！

### 方法 2: 如果已有 Access Key

如果您之前创建过 Access Key，可以在同一页面查看 Access Key ID（但无法查看 Secret，需要重新创建）。

---

## 配置 AWS CLI

获取 Access Key 后，运行：

```bash
aws configure
```

输入以下信息：

```
AWS Access Key ID [None]: [粘贴您的 Access Key ID]
AWS Secret Access Key [None]: [粘贴您的 Secret Access Key]
Default region name [None]: ap-southeast-1
Default output format [None]: json
```

**区域选择**：
- 如果您的 EC2 在亚太地区：`ap-southeast-1`（新加坡）或 `ap-southeast-2`（悉尼）
- 如果在美国：`us-east-1`（弗吉尼亚）或 `us-west-2`（俄勒冈）
- 不确定的话，可以在 EC2 控制台查看实例所在区域

---

## 验证配置

配置完成后，运行：

```bash
aws sts get-caller-identity
```

如果成功，会显示您的 AWS 账户信息。

---

## 完成配置后

配置完成后，告诉我，我会帮您运行安全组配置脚本！
