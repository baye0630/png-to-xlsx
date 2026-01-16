"""
重试工具模块
提供自动重试机制，增强系统稳定性
"""
import asyncio
from typing import TypeVar, Callable, Optional, Tuple
from functools import wraps

from app.core.logging import logger


T = TypeVar('T')


async def retry_async(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple = (Exception,),
    retry_on_result: Optional[Callable[[any], bool]] = None
) -> any:
    """
    异步函数重试装饰器
    
    Args:
        func: 要执行的异步函数
        max_retries: 最大重试次数
        initial_delay: 初始延迟时间（秒）
        backoff_factor: 延迟时间倍增因子
        exceptions: 需要重试的异常类型
        retry_on_result: 基于返回值判断是否重试的函数
        
    Returns:
        函数执行结果
    """
    last_exception = None
    delay = initial_delay
    
    for attempt in range(max_retries + 1):
        try:
            result = await func()
            
            # 如果提供了结果判断函数，检查是否需要重试
            if retry_on_result and attempt < max_retries:
                if retry_on_result(result):
                    logger.warning(
                        f"函数 {func.__name__} 返回值需要重试 "
                        f"(尝试 {attempt + 1}/{max_retries + 1})"
                    )
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
                    continue
            
            return result
            
        except exceptions as e:
            last_exception = e
            
            if attempt < max_retries:
                logger.warning(
                    f"函数 {func.__name__} 执行失败: {str(e)} "
                    f"(尝试 {attempt + 1}/{max_retries + 1})，"
                    f"{delay}秒后重试..."
                )
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error(
                    f"函数 {func.__name__} 重试 {max_retries} 次后仍然失败: {str(e)}"
                )
    
    # 所有重试都失败了，抛出最后一次的异常
    raise last_exception


def with_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple = (Exception,)
):
    """
    异步函数重试装饰器（装饰器版本）
    
    使用示例:
    @with_retry(max_retries=3, initial_delay=1.0)
    async def my_function():
        # 函数体
        pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async def _func():
                return await func(*args, **kwargs)
            
            return await retry_async(
                _func,
                max_retries=max_retries,
                initial_delay=initial_delay,
                backoff_factor=backoff_factor,
                exceptions=exceptions
            )
        
        return wrapper
    
    return decorator


class RetryConfig:
    """重试配置类"""
    
    # OCR 相关重试配置
    OCR_MAX_RETRIES = 3
    OCR_INITIAL_DELAY = 2.0
    OCR_BACKOFF_FACTOR = 2.0
    
    # 文件操作重试配置
    FILE_MAX_RETRIES = 2
    FILE_INITIAL_DELAY = 0.5
    FILE_BACKOFF_FACTOR = 2.0
    
    # API 请求重试配置
    API_MAX_RETRIES = 3
    API_INITIAL_DELAY = 1.0
    API_BACKOFF_FACTOR = 1.5
