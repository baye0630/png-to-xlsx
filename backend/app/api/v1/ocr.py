"""
OCR 相关 API 路由
"""
from uuid import UUID
from fastapi import APIRouter, HTTPException, Path as PathParam

from app.services.ocr_service import OCRService
from app.services.task_service import TaskService
from app.schemas.ocr import OCRJobResponse, OCRHealthResponse
from app.schemas.common import ResponseModel
from app.core.logging import logger


router = APIRouter(prefix="/ocr", tags=["OCR 服务"])


@router.get(
    "/health",
    response_model=ResponseModel[OCRHealthResponse],
    summary="OCR 服务健康检查"
)
async def check_ocr_health():
    """
    检查 OCR 服务健康状态
    
    Returns:
        OCR 服务的健康状态和相关信息
    """
    healthy, service_info = await OCRService.check_ocr_health()
    
    return ResponseModel(
        success=healthy,
        message="OCR 服务正常" if healthy else "OCR 服务异常",
        data=OCRHealthResponse(
            healthy=healthy,
            service_info=service_info
        )
    )


@router.post(
    "/start/{task_id}",
    response_model=ResponseModel[OCRJobResponse],
    summary="启动 OCR 任务"
)
async def start_ocr_job(
    task_id: UUID = PathParam(..., description="任务 ID")
):
    """
    启动 OCR 任务
    
    **流程**：
    1. 验证任务存在且已上传图片
    2. 上传图片到 OCR 服务
    3. 获取 ocr_job_id
    4. 更新任务状态为 ocr_processing
    5. 保存 ocr_job_id 到任务
    
    **前置条件**：
    - 任务必须存在
    - 任务必须已上传图片（image_path 不为空）
    
    Args:
        task_id: 任务 ID (UUID)
    
    Returns:
        OCR 任务创建结果
    
    Raises:
        HTTPException: 任务不存在或 OCR 服务调用失败
    """
    logger.info(f"接收到 OCR 启动请求: task_id={task_id}")
    
    # 启动 OCR 任务
    success, message = await OCRService.start_ocr_job(task_id)
    
    if not success:
        logger.error(f"OCR 任务启动失败: task_id={task_id}, error={message}")
        raise HTTPException(status_code=400, detail=message)
    
    # 获取更新后的任务信息
    task = await TaskService.get_task(task_id)
    
    return ResponseModel(
        success=True,
        message=message,
        data=OCRJobResponse(
            task_id=task.task_id,
            ocr_job_id=task.ocr_job_id,
            status=task.status.value,
            message=message
        )
    )


@router.post(
    "/poll/{task_id}",
    response_model=ResponseModel[OCRJobResponse],
    summary="轮询 OCR 任务状态并获取结果"
)
async def poll_ocr_result(
    task_id: UUID = PathParam(..., description="任务 ID")
):
    """
    轮询 OCR 任务状态并获取结果
    
    **流程**：
    1. 验证任务存在且已启动 OCR（ocr_job_id 不为空）
    2. 长轮询 OCR 任务状态，直到完成或失败
    3. 如果成功，获取 OCR JSON 结果
    4. 保存 JSON 到文件
    5. 更新任务状态为 ocr_done
    
    **前置条件**：
    - 任务必须存在
    - 任务必须已启动 OCR（ocr_job_id 不为空）
    - 任务状态为 ocr_processing
    
    **注意**：
    - 此接口可能需要较长时间（最多 5 分钟）
    - 建议在后台异步调用或使用前端轮询
    
    Args:
        task_id: 任务 ID (UUID)
    
    Returns:
        OCR 任务完成结果
    
    Raises:
        HTTPException: 任务不存在、OCR 失败或超时
    """
    logger.info(f"接收到 OCR 轮询请求: task_id={task_id}")
    
    # 轮询并获取结果
    success, message = await OCRService.poll_and_fetch_result(task_id)
    
    if not success:
        logger.error(f"OCR 任务轮询失败: task_id={task_id}, error={message}")
        raise HTTPException(status_code=400, detail=message)
    
    # 获取更新后的任务信息
    task = await TaskService.get_task(task_id)
    
    return ResponseModel(
        success=True,
        message=message,
        data=OCRJobResponse(
            task_id=task.task_id,
            ocr_job_id=task.ocr_job_id,
            status=task.status.value,
            message=message
        )
    )
