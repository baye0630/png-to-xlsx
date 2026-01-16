"""
中间件模块
"""
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    
    记录每个请求的详细信息，包括：
    - 请求 ID（用于追踪）
    - 请求方法和路径
    - 响应状态码
    - 响应时间
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求 ID
        request_id = str(uuid.uuid4())[:8]
        
        # 记录请求开始
        start_time = time.time()
        
        # 提取请求信息
        method = request.method
        url = str(request.url)
        client = request.client.host if request.client else "unknown"
        
        logger.info(
            f"[{request_id}] → {method} {url} | Client: {client}"
        )
        
        # 将 request_id 添加到请求状态中，便于在其他地方使用
        request.state.request_id = request_id
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算响应时间
            process_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            # 记录响应
            logger.info(
                f"[{request_id}] ← {method} {url} | "
                f"Status: {response.status_code} | "
                f"Time: {process_time:.2f}ms"
            )
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
            
            return response
            
        except Exception as e:
            # 记录错误
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"[{request_id}] ✗ {method} {url} | "
                f"Error: {type(e).__name__}: {str(e)} | "
                f"Time: {process_time:.2f}ms",
                exc_info=True
            )
            raise


class ErrorTrackingMiddleware(BaseHTTPMiddleware):
    """
    错误追踪中间件
    
    追踪所有错误响应（4xx, 5xx），便于监控和分析
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 追踪错误响应
        if response.status_code >= 400:
            request_id = getattr(request.state, 'request_id', 'unknown')
            method = request.method
            url = str(request.url)
            status_code = response.status_code
            
            # 根据状态码级别记录不同级别的日志
            if status_code >= 500:
                logger.error(
                    f"[{request_id}] 服务器错误 {status_code} | {method} {url}"
                )
            elif status_code >= 400:
                logger.warning(
                    f"[{request_id}] 客户端错误 {status_code} | {method} {url}"
                )
        
        return response
