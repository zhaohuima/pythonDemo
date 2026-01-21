# 测试环境指南 | Test Environment Guide

## 快速开始 | Quick Start

### 1. 设置测试环境 | Setup Test Environment

```bash
# 给脚本添加执行权限
chmod +x setup_test_env.sh start_test_server.sh

# 运行设置脚本
./setup_test_env.sh
```

### 2. 启动测试服务器 | Start Test Server

```bash
# 启动Web应用
./start_test_server.sh
```

服务器将在 `http://localhost:5000` 启动

### 3. 访问应用 | Access Application

在浏览器中打开: `http://localhost:5000`

---

## 手动设置 | Manual Setup

如果自动脚本不工作，可以手动执行以下步骤：

### 1. 激活虚拟环境

```bash
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### 3. 启动应用

```bash
python web_app.py
```

---

## 运行测试 | Run Tests

### 运行所有测试

```bash
source venv/bin/activate
pytest
```

### 运行特定测试

```bash
# 测试格式化功能
python test_formatting_quick.py

# 测试RAG功能
python test_rag.py

# 测试产品分析
python test_product_analysis.py

# 测试研究功能
python test_researcher_only.py
```

### 性能测试

```bash
# 运行性能测试
python run_productresearcheragent_performance_test.py

# 生成性能报告
python generate_performance_report.py

# 分析性能
python analyze_performance.py
```

---

## 项目结构 | Project Structure

```
pythonDemo/
├── agents.py                    # Agent定义
├── web_app.py                   # Web应用主文件
├── main.py                      # 命令行入口
├── config.py                    # 配置文件
├── skills/                      # Skills模块
│   ├── base_skill.py
│   ├── market_analysis_skill.py
│   ├── market_insights_skill.py
│   ├── core_requirements_skill.py
│   ├── target_users_skill.py
│   └── prompts/                 # Prompt模板
├── templates/                   # HTML模板
├── static/                      # 静态文件
├── logs/                        # 日志文件
├── outputs/                     # 输出文件
├── test_results/                # 测试结果
└── vector_db/                   # 向量数据库
```

---

## 配置说明 | Configuration

配置文件位于 `config.py`，包含以下设置：

- **API_KEY**: SiliconFlow API密钥
- **API_BASE_URL**: API端点
- **MODEL_NAME**: 使用的LLM模型
- **RAG_ENABLED**: 是否启用RAG功能
- **RAG_DOCUMENTS_DIR**: RAG文档目录
- **RAG_VECTOR_DB_DIR**: 向量数据库目录

---

## 功能测试 | Feature Testing

### 1. 测试Web界面

1. 启动服务器: `./start_test_server.sh`
2. 打开浏览器: `http://localhost:5000`
3. 输入产品描述进行测试

### 2. 测试Skills系统

```bash
# 测试市场分析
python -c "from skills.market_analysis_skill import MarketAnalysisSkill; skill = MarketAnalysisSkill(); print(skill.execute('test product'))"
```

### 3. 测试RAG功能

```bash
# 调试RAG
python debug_rag.py

# 测试RAG查询
python test_rag.py
```

### 4. 测试格式化输出

```bash
# 快速格式化测试
python test_formatting_quick.py

# 完整格式化测试
python test_formatting.py
```

---

## 常见问题 | Troubleshooting

### 问题1: 虚拟环境未激活

**症状**: 命令找不到或包未安装

**解决方案**:
```bash
source venv/bin/activate
```

### 问题2: 依赖包缺失

**症状**: ImportError或ModuleNotFoundError

**解决方案**:
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### 问题3: 端口被占用

**症状**: Address already in use

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :5000

# 杀死进程
kill -9 <PID>
```

### 问题4: API密钥错误

**症状**: API调用失败

**解决方案**: 检查 `config.py` 中的 API_KEY 是否正确

---

## 开发工具 | Development Tools

### IPython交互式环境

```bash
source venv/bin/activate
ipython
```

### 查看日志

```bash
# 实时查看日志
tail -f logs/server.log

# 查看最近的日志
tail -100 logs/server.log
```

### 性能分析

```bash
# 生成性能报告
python generate_performance_report.py

# 查看报告
open performance_report.html
```

---

## 部署相关 | Deployment

### Docker部署

```bash
# 构建镜像
docker build -t product-master .

# 运行容器
docker-compose up
```

### 生产环境部署

参考以下文档：
- `STAGING_ENV_SETUP.md` - 预发布环境设置
- `EC2_DEPLOYMENT.md` - AWS EC2部署
- `DOCKER_MIRROR_SETUP.md` - Docker镜像设置

---

## 联系支持 | Support

如有问题，请查看项目文档或联系开发团队。
