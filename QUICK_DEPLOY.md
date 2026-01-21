# 🚀 快速部署参考

## 两种部署模式

### ⚡ 快速模式（推荐日常使用）
```bash
./deploy_to_staging.sh
```
- ✅ 使用现有镜像
- ⏱️ 约 1-2 分钟
- 💡 适合代码测试

### 🔨 重建模式（仅在必要时使用）
```bash
./deploy_to_staging.sh --rebuild
```
- 🔄 重新构建镜像
- ⏱️ 约 20 分钟
- 📦 更新所有依赖

## 何时使用重建模式？

- ✓ 首次部署
- ✓ 更新了 requirements.txt
- ✓ 更新了 Dockerfile
- ✓ Docker 镜像损坏

## 访问地址

- Web: http://localhost:5000
- Nginx: http://localhost

## 常用命令

```bash
docker-compose logs -f web    # 查看日志
docker-compose restart web    # 重启服务
docker-compose down           # 停止服务
docker-compose ps             # 查看状态
```

---
📖 详细文档: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
