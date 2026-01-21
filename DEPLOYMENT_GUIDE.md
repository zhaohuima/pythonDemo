# Docker Staging 环境部署指南

## 快速开始

### 日常测试部署（推荐）

使用现有 Docker 镜像快速启动容器，无需重新构建：

```bash
./deploy_to_staging.sh
```

**优点：**
- ⚡ 快速部署（约1-2分钟）
- 💾 使用已构建的镜像
- ✅ 适合日常代码测试

### 完整重建部署

仅在以下情况使用：
- 首次部署
- 更新了 requirements.txt 依赖
- 更新了 Dockerfile
- Docker 镜像损坏

```bash
./deploy_to_staging.sh --rebuild
```

**注意：**
- ⏱️ 需要约 20 分钟
- 📦 会重新安装所有依赖（PyTorch、sentence-transformers 等）

## 部署流程

脚本会自动执行以下步骤：

1. **环境检查**
   - 检查 Docker 和 Docker Compose 是否安装
   - 检查必要文件是否存在
   - 检查 Python 语法错误
   - 检查 Git 状态

2. **停止现有容器**
   - 停止并移除正在运行的容器

3. **构建镜像**（可选）
   - 默认跳过，使用现有镜像
   - 使用 `--rebuild` 参数时重新构建

4. **启动容器**
   - 启动 Web 服务容器（端口 5000）
   - 启动 Nginx 代理容器（端口 80, 443）

5. **验证部署**
   - 检查容器状态
   - 测试 Web 服务响应
   - 检查启动日志

## 访问地址

部署成功后，可以通过以下地址访问：

- **Web 服务**: http://localhost:5000
- **Nginx 代理**: http://localhost

## 常用命令

```bash
# 查看所有日志
docker-compose logs -f

# 查看 Web 服务日志
docker-compose logs -f web

# 查看 Nginx 日志
docker-compose logs -f nginx

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 查看容器状态
docker-compose ps

# 查看容器资源使用
docker stats
```

## 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker-compose logs web

# 检查容器状态
docker-compose ps
```

### Web 服务无响应

```bash
# 重启 Web 服务
docker-compose restart web

# 查看最近的错误日志
docker-compose logs --tail=50 web | grep -i error
```

### 需要完全重置

```bash
# 停止并删除所有容器
docker-compose down

# 删除镜像（可选）
docker rmi pythondemo-web

# 重新构建并部署
./deploy_to_staging.sh --rebuild
```

## 最佳实践

1. **日常开发测试**
   - 使用默认模式：`./deploy_to_staging.sh`
   - 代码更改会在容器重启后生效

2. **依赖更新后**
   - 使用重建模式：`./deploy_to_staging.sh --rebuild`
   - 确保所有新依赖被正确安装

3. **定期清理**
   - 定期清理未使用的 Docker 镜像和容器
   - 使用 `docker system prune` 清理系统

## 注意事项

⚠️ **重要提醒**
- 默认模式不会重新构建镜像，只会启动现有容器
- 如果修改了 requirements.txt 或 Dockerfile，必须使用 `--rebuild` 参数
- 重建过程需要约 20 分钟，请耐心等待
- 确保 Docker Desktop 正在运行

## 技术细节

### 容器配置

- **Web 容器**:
  - 镜像: pythondemo-web
  - 端口: 5000
  - 服务器: Gunicorn

- **Nginx 容器**:
  - 镜像: nginx:alpine
  - 端口: 80, 443
  - 作用: 反向代理

### 构建时间分析

重建模式下的主要耗时步骤：
- apt-get 更新和安装系统依赖: ~5 分钟
- pip 安装 requirements.txt: ~11 分钟
- 安装 PyTorch: ~1 分钟
- 下载 sentence-transformers 模型: ~3 分钟

总计约 20 分钟
