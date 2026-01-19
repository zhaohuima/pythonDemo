# Docker 镜像加速器配置指南

## macOS Docker Desktop 配置方法

### 步骤 1: 打开 Docker Desktop 设置

1. 点击菜单栏的 **Docker 图标**（鲸鱼图标）
2. 选择 **Settings**（设置）或 **Preferences**（偏好设置）

### 步骤 2: 配置镜像加速器

1. 在左侧菜单中找到 **Docker Engine**
2. 在右侧的 JSON 配置中添加以下内容：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

**或者**，如果已有配置，在 `registry-mirrors` 数组中添加镜像源。

### 步骤 3: 应用配置

1. 点击 **Apply & Restart**（应用并重启）
2. 等待 Docker Desktop 重启完成

### 步骤 4: 验证配置

运行以下命令验证配置是否生效：

```bash
docker info | grep -A 10 "Registry Mirrors"
```

应该能看到配置的镜像源。

## 常用国内镜像源

- **中科大镜像**: `https://docker.mirrors.ustc.edu.cn`
- **网易镜像**: `https://hub-mirror.c.163.com`
- **百度云镜像**: `https://mirror.baidubce.com`
- **阿里云镜像**: `https://<你的ID>.mirror.aliyuncs.com` (需要登录阿里云获取)

## 配置完成后

配置完成后，重新运行启动脚本：

```bash
./docker-compose-start.sh
```
