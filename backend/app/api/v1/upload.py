"""
图片上传相关 API 路由
"""
from uuid import UUID
from fastapi import APIRouter, File, UploadFile, HTTPException, Path as PathParam

from app.services.upload_service import UploadService
from app.services.task_service import TaskService
from app.schemas.upload import UploadResponse
from app.schemas.common import ResponseModel
from app.core.logging import logger


router = APIRouter(prefix="/upload", tags=["文件上传"])


@router.post(
    "/image/{task_id}",
    response_model=ResponseModel[UploadResponse],
    summary="上传图片并绑定任务"
)
async def upload_image(
    task_id: UUID = PathParam(..., description="任务 ID"),
    file: UploadFile = File(..., description="图片文件")
):
    """
    上传图片并与任务绑定
    
    **存储位置**：`data/images/{task_id}.{ext}`
    
    **流程**：
    1. 验证任务是否存在
    2. 验证图片格式（支持：png, jpg, jpeg, gif, bmp, webp）
    3. 保存图片到 data/images/ 目录
    4. 更新任务的 image_path 字段
    5. 更新任务状态为 uploaded
    
    **支持的图片格式**：
    - PNG (.png)
    - JPEG (.jpg, .jpeg)
    - GIF (.gif)
    - BMP (.bmp)
    - WebP (.webp)
    
    Args:
        task_id: 任务 ID (UUID)
        file: 上传的图片文件
    
    Returns:
        上传成功的响应信息
    
    Raises:
        HTTPException: 任务不存在或上传失败
    """
    logger.info(f"接收到图片上传请求: task_id={task_id}, filename={file.filename}")
    
    # 执行上传并绑定
    success, message = await UploadService.upload_and_bind_image(task_id, file)
    
    if not success:
        logger.error(f"图片上传失败: task_id={task_id}, error={message}")
        raise HTTPException(status_code=400, detail=message)
    
    # 获取更新后的任务信息
    task = await TaskService.get_task(task_id)
    
    return ResponseModel(
        success=True,
        message=message,
        data=UploadResponse(
            task_id=task.task_id,
            image_path=task.image_path,
            message=message
        )
    )


@router.post(
    "/image",
    response_model=ResponseModel[UploadResponse],
    summary="创建任务并上传图片"
)
async def create_task_and_upload(
    file: UploadFile = File(..., description="图片文件")
):
    """
    创建新任务并上传图片（一站式接口）
    
    这是一个便捷接口，自动完成：
    1. 创建新任务
    2. 上传图片并绑定
    
    **存储位置**：`data/images/{task_id}.{ext}`
    
    Args:
        file: 上传的图片文件
    
    Returns:
        创建的任务信息和上传结果
    """
    logger.info(f"接收到创建任务+上传图片请求: filename={file.filename}")
    
    # 1. 创建新任务
    task = await TaskService.create_task()
    logger.info(f"任务创建成功: task_id={task.task_id}")
    
    # 2. 上传图片并绑定
    success, message = await UploadService.upload_and_bind_image(task.task_id, file)
    
    if not success:
        logger.error(f"图片上传失败: task_id={task.task_id}, error={message}")
        # 上传失败，但任务已创建，返回错误但保留任务
        raise HTTPException(
            status_code=400,
            detail=f"任务已创建但图片上传失败: {message}"
        )
    
    # 3. 获取更新后的任务信息
    task = await TaskService.get_task(task.task_id)
    
    return ResponseModel(
        success=True,
        message=f"任务创建并上传成功",
        data=UploadResponse(
            task_id=task.task_id,
            image_path=task.image_path,
            message=message
        )
    )
