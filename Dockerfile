# ============================================================================
# Product Master Docker 镜像
# 用于模拟 EC2 生产环境的 Staging 测试
# ============================================================================

# 使用 Python 3.12 slim 镜像（本地已有）
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖（添加重试机制）
RUN for i in 1 2 3 4 5; do \
        apt-get update && \
        apt-get install -y --no-install-recommends --fix-missing \
            build-essential \
            curl && \
        rm -rf /var/lib/apt/lists/* && \
        break || sleep 10; \
    done

# 复制依赖文件
COPY requirements.txt .
COPY requirements-docker.txt .

# 安装 Python 依赖
RUN pip install -r requirements.txt

# 安装 RAG 相关依赖（CPU 版本的 PyTorch）
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements-docker.txt

# 预下载 HuggingFace embedding 模型（避免运行时下载超时）
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p logs outputs knowledge_base/documents vector_db

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# 启动命令 - 使用 Gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "web_app:app"]
