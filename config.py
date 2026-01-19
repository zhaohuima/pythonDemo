"""
配置文件 | Configuration File
用于存储API密钥和其他配置信息
Stores API keys and other configuration information
"""

# 硅基流动 API Key | SiliconFlow API Key
API_KEY = "***REMOVED***"

# 硅基流动 API 端点 | SiliconFlow API Endpoint
API_BASE_URL = "https://api.siliconflow.cn/v1"

# LLM 模型名称 | LLM Model Name
# 可选模型: Qwen/Qwen2.5-72B-Instruct, Qwen/Qwen2.5-7B-Instruct, deepseek-ai/DeepSeek-V2.5
# 如果 72B 模型不可用，可以切换到其他模型
MODEL_NAME = "deepseek-ai/DeepSeek-V2.5"

# 项目名称 | Project Name
PROJECT_NAME = "Product Master - Multi-Agent Orchestration System"

# 日志级别 | Log Level
LOG_LEVEL = "INFO"

# RAG Configuration | RAG 配置
RAG_ENABLED = True
RAG_DOCUMENTS_DIR = "knowledge_base/documents"
RAG_VECTOR_DB_DIR = "vector_db/chroma_db"
RAG_COLLECTION_NAME = "product_knowledge"
RAG_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
RAG_CHUNK_SIZE = 1000
RAG_CHUNK_OVERLAP = 150
RAG_TOP_K = 5  # Number of relevant chunks to retrieve
