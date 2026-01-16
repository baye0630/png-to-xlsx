"""
全局异常处理器
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import logger


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    HTTP 异常处理器
    
    处理所有 HTTP 异常（如 404, 500 等）
    """
    logger.warning(
        f"HTTP异常: {exc.status_code} - {exc.detail} | "
        f"请求: {request.method} {request.url.path}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.detail),
            "error_type": "http_error",
            "status_code": exc.status_code
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    请求验证异常处理器
    
    处理请求参数验证失败的情况
    """
    errors = exc.errors()
    logger.warning(
        f"请求验证失败: {errors} | "
        f"请求: {request.method} {request.url.path}"
    )
    
    # 格式化错误信息
    error_messages = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "请求参数验证失败",
            "errors": error_messages,
            "error_type": "validation_error"
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    通用异常处理器
    
    处理所有未被捕获的异常，避免系统崩溃
    """
    logger.error(
        f"未捕获的异常: {type(exc).__name__}: {str(exc)} | "
        f"请求: {request.method} {request.url.path}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "服务器内部错误，请稍后重试",
            "error_type": "internal_error",
            "detail": str(exc) if logger.level <= 10 else None  # 仅在 DEBUG 模式下返回详细信息
        }
    )
