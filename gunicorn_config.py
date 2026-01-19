"""
Gunicorn 配置文件
用于生产环境和 Docker 环境
"""

import multiprocessing
import os

# 服务器 socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker 进程
# 注意：由于 execution_states 存储在进程内存中，多worker会导致状态不共享
# 如需多worker支持，需要使用Redis等外部存储来共享状态
workers = 1  # 单worker确保状态共享
worker_class = "sync"
worker_connections = 1000
timeout = 600  # 10分钟，LLM 调用可能需要较长时间
keepalive = 5

# 日志
accesslog = "-"  # 输出到 stdout
errorlog = "-"   # 输出到 stderr
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = "product-master"

# 服务器钩子
def on_starting(server):
    """服务器启动时调用"""
    server.log.info("Starting Product Master server...")

def on_reload(server):
    """重载时调用"""
    server.log.info("Reloading Product Master server...")

def when_ready(server):
    """服务器就绪时调用"""
    server.log.info("Product Master server is ready. Spawning workers")

def on_exit(server):
    """服务器退出时调用"""
    server.log.info("Shutting down Product Master server...")
