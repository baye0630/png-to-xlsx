"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.core.logging import logger
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.core.middleware import RequestLoggingMiddleware, ErrorTrackingMiddleware
from app.api.v1 import task as task_router
from app.api.v1 import upload as upload_router
from app.api.v1 import ocr as ocr_router
from app.api.v1 import excel as excel_router
from app.api.v1 import table as table_router


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("应用启动中...")
    
    # 初始化数据目录
    for dir_name, dir_path in settings.data_paths.items():
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"数据目录已创建: {dir_name} -> {dir_path}")
    
    # 初始化数据库
    try:
        await init_db()
        logger.info("数据库连接成功")
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise
    
    logger.info("应用启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("应用关闭中...")
    await close_db()
    logger.info("数据库连接已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)


# 配置中间件
# 注意：中间件的添加顺序很重要，后添加的先执行

# 1. CORS 中间件（最外层）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 错误追踪中间件
app.add_middleware(ErrorTrackingMiddleware)

# 3. 请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# 配置异常处理器
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# 注册 API 路由
app.include_router(task_router.router, prefix="/api/v1")
app.include_router(upload_router.router, prefix="/api/v1")
app.include_router(ocr_router.router, prefix="/api/v1")
app.include_router(excel_router.router, prefix="/api/v1")
app.include_router(table_router.router, prefix="/api/v1")
logger.info("API 路由已注册")


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    from tortoise import Tortoise
    from app.services.ocr_service import OCRService
    
    # 检查数据库连接
    db_status = "connected"
    try:
        conn = Tortoise.get_connection("default")
        await conn.execute_query("SELECT 1")
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
        logger.error(f"数据库健康检查失败: {e}")
    
    # 检查 OCR 服务
    ocr_status = "unknown"
    try:
        ocr_healthy, ocr_info = await OCRService.check_ocr_health()
        ocr_status = "connected" if ocr_healthy else "disconnected"
    except Exception as e:
        ocr_status = f"error: {str(e)}"
        logger.error(f"OCR 健康检查失败: {e}")
    
    # 检查数据目录
    data_dirs_status = {}
    for dir_name, dir_path in settings.data_paths.items():
        data_dirs_status[dir_name] = {
            "path": str(dir_path),
            "exists": Path(dir_path).exists()
        }
    
    # 整体健康状态
    is_healthy = (db_status == "connected" and ocr_status == "connected")
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": Path(__file__).stat().st_mtime,
        "database": db_status,
        "ocr_service": ocr_status,
        "data_directories": data_dirs_status,
        "debug_mode": settings.debug
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )
