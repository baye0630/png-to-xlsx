"""
日志配置模块
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


def setup_logging():
    """配置日志"""
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    # 详细格式：包含文件名、函数名、行号
    detailed_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "[%(filename)s:%(funcName)s:%(lineno)d] - %(message)s"
    )
    simple_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 创建格式化器
    detailed_formatter = logging.Formatter(detailed_format, datefmt=date_format)
    simple_formatter = logging.Formatter(simple_format, datefmt=date_format)
    
    # 控制台处理器（简单格式）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # 应用日志文件处理器（详细格式，按大小轮转）
    app_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(detailed_formatter)
    
    # 错误日志文件处理器（只记录 ERROR 及以上）
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # 访问日志处理器（按天轮转）
    access_handler = TimedRotatingFileHandler(
        log_dir / "access.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(simple_formatter)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    
    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").addHandler(access_handler)
    logging.getLogger("tortoise").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)


logger = setup_logging()


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)
