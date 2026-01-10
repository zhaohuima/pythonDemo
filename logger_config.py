"""
日志配置模块 | Logging Configuration Module
配置统一的日志系统，记录函数调用和执行流程
Configure unified logging system to record function calls and execution flow
"""

import logging
import os
from datetime import datetime
from config import LOG_LEVEL


def setup_logger(name: str = "ProductMaster", log_file: str = None, level: str = None):
    """
    设置日志记录器 | Setup logger
    
    Args:
        name: 日志记录器名称 | Logger name
        log_file: 日志文件路径 | Log file path (optional)
        level: 日志级别 | Log level (optional)
        
    Returns:
        配置好的日志记录器 | Configured logger
    """
    # 创建日志记录器 | Create logger
    logger = logging.getLogger(name)
    
    # 设置日志级别 | Set log level
    log_level = level or LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 避免重复添加处理器 | Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # 创建格式器 | Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器 | Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）| File handler (if log file specified)
    if log_file:
        # 确保日志目录存在 | Ensure log directory exists
        log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # 文件记录更详细的日志
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# 创建默认的日志记录器 | Create default logger
default_log_file = f"logs/product_master_{datetime.now().strftime('%Y%m%d')}.log"
logger = setup_logger("ProductMaster", default_log_file)


# 函数调用装饰器 | Function call decorator
def log_function_call(func):
    """
    装饰器：记录函数调用 | Decorator: Log function calls
    
    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            ...
    """
    def wrapper(*args, **kwargs):
        logger.debug(f"→ Calling {func.__module__}.{func.__name__}()")
        logger.debug(f"  Args: {args}")
        logger.debug(f"  Kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"✓ {func.__module__}.{func.__name__}() completed")
            return result
        except Exception as e:
            logger.error(f"✗ {func.__module__}.{func.__name__}() failed: {str(e)}", exc_info=True)
            raise
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper
