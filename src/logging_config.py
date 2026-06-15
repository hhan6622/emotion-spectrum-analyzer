"""
情绪光谱仪 - 日志配置模块

集中管理项目所有日志配置，提供统一的日志记录接口
"""

import logging
import os
from pathlib import Path
from typing import Optional

from src.config import LOG_CONFIG, PROJECT_ROOT


def setup_logging(name: str = __name__) -> logging.Logger:
    """
    配置日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_CONFIG['level']))
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(LOG_CONFIG['format'])
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 创建文件处理器
    log_file_path = LOG_CONFIG['file_path']
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = __name__) -> logging.Logger:
    """
    获取日志记录器（便捷函数）
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器
    """
    return setup_logging(name)


class LogMixin:
    """
    日志混合类，为其他类提供日志功能
    
    使用方式：
        class MyClass(LogMixin):
            def __init__(self):
                super().__init__()
                self.logger.info("初始化完成")
    """
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
