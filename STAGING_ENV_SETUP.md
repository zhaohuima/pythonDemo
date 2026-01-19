# 🐳 Staging 环境搭建指南

本文档说明如何在本地 Mac Mini 上使用 Docker Compose 搭建 Staging 环境，用于模拟生产环境 `https://productmaster.dpdns.org/`。

## 📋 前置要求

1. **Docker Desktop** 已安装并运行
2. **Docker Compose** 已安装（Docker Desktop 自带）
3. 确保端口 **80** 和 **5000** 未被占用

## 🚀 快速开始

### 1. 启动 Staging 环境

```bash
# 使用启动脚本（推荐）
chmod +x docker-compose-start.sh
./docker-compose-start.sh

# 或手动启动
docker-compose up -d --build
```

### 2. 访问应用

- **通过 Nginx（推荐）**: http://localhost
- **直接访问 Flask**: http://localhost:5000

### 3. 查看服务状态

```bash
# 查看所有服务状态
docker-compose ps

# 查看 Web 服务日志
docker-compose logs -f web

# 查看 Nginx 日志
docker-compose logs -f nginx
```

## 🏗️ 架构说明

Staging 环境包含两个服务：

1. **web** - Flask 应用服务（Gunicorn）
   - 端口: 5000（内部）
   - 容器名: `product-master-web`

2. **nginx** - Nginx 反向代理
   - 端口: 80（HTTP）
   - 容器名: `product-master-nginx`
   - 代理到 `web:5000`

## 📁 文件说明

### Docker 相关文件

- `Dockerfile` - Flask 应用镜像定义
- `docker-compose.yml` - Docker Compose 配置
- `.dockerignore` - Docker 构建忽略文件
- `requirements-docker.txt` - Docker 环境额外依赖
- `gunicorn_config.py` - Gunicorn 服务器配置
- `nginx-staging.conf` - Nginx 配置文件（Staging 环境）

### 数据卷挂载

以下目录会被挂载到容器中，数据会持久化：

- `./logs` → `/app/logs` - 日志文件
- `./outputs` → `/app/outputs` - 输出结果
- `./knowledge_base` → `/app/knowledge_base` - 知识库文档
- `./vector_db` → `/app/vector_db` - 向量数据库

## 🔧 常用命令

### 启动和停止

```bash
# 启动服务（后台运行）
docker-compose up -d

# 停止服务
docker-compose down

# 停止并删除卷（清理数据）
docker-compose down -v

# 重启服务
docker-compose restart

# 重启特定服务
docker-compose restart web
docker-compose restart nginx
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f web
docker-compose logs -f nginx

# 查看最近 100 行日志
docker-compose logs --tail=100 web
```

### 进入容器

```bash
# 进入 Web 容器
docker-compose exec web bash

# 进入 Nginx 容器
docker-compose exec nginx sh
```

### 重建镜像

```bash
# 重建镜像（不缓存）
docker-compose build --no-cache

# 重建并启动
docker-compose up -d --build
```

## 🧪 测试

### 1. 健康检查

```bash
# 检查 Web 服务健康状态
curl http://localhost:5000/

# 检查 Nginx 健康状态
curl http://localhost/health
```

### 2. 功能测试

1. 访问 http://localhost
2. 在输入框中输入产品需求
3. 点击 "Start Orchestration" 按钮
4. 观察执行进度和结果

### 3. API 测试

```bash
# 测试编排 API
curl -X POST http://localhost/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"user_input": "开发一个在线学习平台"}'

# 获取执行状态（替换 EXECUTION_ID）
curl http://localhost/api/status/EXECUTION_ID

# 获取执行结果（替换 EXECUTION_ID）
curl http://localhost/api/result/EXECUTION_ID
```

## 🐛 故障排查

### 问题 1: 端口被占用

```bash
# 检查端口占用
lsof -i :80
lsof -i :5000

# 修改 docker-compose.yml 中的端口映射
# 例如: "8080:80" 改为使用 8080 端口
```

### 问题 2: 服务无法启动

```bash
# 查看详细错误日志
docker-compose logs web
docker-compose logs nginx

# 检查容器状态
docker-compose ps

# 检查镜像是否构建成功
docker images | grep product-master
```

### 问题 3: 静态文件无法加载

```bash
# 检查静态文件挂载
docker-compose exec nginx ls -la /usr/share/nginx/html/static/

# 检查 Nginx 配置
docker-compose exec nginx cat /etc/nginx/conf.d/default.conf
```

### 问题 4: API 超时

- LLM 调用可能需要较长时间（最长 10 分钟）
- Nginx 已配置超时时间为 600 秒（10 分钟）
- 如果仍然超时，可以增加 `nginx-staging.conf` 中的超时时间

## 🔄 与生产环境的差异

| 项目 | Staging 环境 | 生产环境 |
|------|-------------|---------|
| 域名 | localhost | productmaster.dpdns.org |
| HTTPS | ❌ HTTP only | ✅ HTTPS (Let's Encrypt) |
| SSL 证书 | ❌ | ✅ |
| 服务器 | Docker 容器 | AWS EC2 Ubuntu 24.04 |
| 数据持久化 | Docker 卷 | 本地文件系统 |

## 📝 注意事项

1. **开发模式**: `docker-compose.yml` 中挂载了代码目录 (`./:/app`)，修改代码后需要重启服务才能生效
2. **生产模式**: 移除代码目录挂载，代码会打包到镜像中
3. **数据备份**: 定期备份 `logs/`, `outputs/`, `knowledge_base/`, `vector_db/` 目录
4. **资源限制**: Docker Desktop 默认资源限制可能影响性能，可在 Docker Desktop 设置中调整

## 🚀 部署到生产环境

在 Staging 环境测试通过后，可以部署到生产环境：

1. 确保所有功能在 Staging 环境正常工作
2. 使用 `deploy_to_ec2.sh` 脚本部署到 AWS EC2
3. 参考 `EC2_DEPLOYMENT.md` 了解详细部署步骤

## 📚 相关文档

- `README.md` - 项目总体说明
- `EC2_DEPLOYMENT.md` - EC2 部署指南
- `NGINX_SETUP.md` - Nginx 配置说明
- `HTTPS_SETUP_GUIDE.md` - HTTPS 配置指南
