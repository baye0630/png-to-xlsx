"""
Excel 生成相关 API 路由
"""
from uuid import UUID
from pathlib import Path
from datetime import datetime
import re
from fastapi import APIRouter, HTTPException, Path as PathParam
from fastapi.responses import FileResponse

from app.services.excel_service import ExcelService
from app.services.task_service import TaskService
from app.schemas.common import ResponseModel
from app.core.logging import logger


router = APIRouter(prefix="/excel", tags=["Excel 服务"])


@router.post(
    "/generate/{task_id}",
    response_model=ResponseModel,
    summary="生成 Excel 文件"
)
async def generate_excel(
    task_id: UUID = PathParam(..., description="任务 ID")
):
    """
    根据任务的 OCR JSON 生成 Excel 文件（多表 → 多 Sheet）
    
    前置条件：
    - 任务状态必须为 ocr_done
    - OCR JSON 文件必须存在
    
    Args:
        task_id: 任务 ID
        
    Returns:
        生成结果，包含 Excel 文件路径和 Sheet 数量
        
    Raises:
        HTTPException: 任务不存在或状态错误
    """
    logger.info(f"开始为任务 {task_id} 生成 Excel")
    
    # 检查任务是否存在
    task = await TaskService.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    
    # 生成 Excel
    success, message, excel_path = await ExcelService.generate_excel_from_ocr(task_id)
    
    if not success:
        logger.error(f"生成 Excel 失败: {message}")
        raise HTTPException(status_code=400, detail=message)
    
    # 获取最新任务状态
    task = await TaskService.get_task(task_id)
    
    return ResponseModel(
        success=True,
        message=message,
        data={
            "task_id": str(task.task_id),
            "excel_path": excel_path,
            "status": task.status.value,
            "message": message
        }
    )


@router.get(
    "/download/{task_id}",
    summary="下载 Excel 文件"
)
async def download_excel(
    task_id: UUID = PathParam(..., description="任务 ID")
):
    """
    下载生成的 Excel 文件
    
    前置条件：
    - 任务状态必须为 excel_generated 或 editable
    - Excel 文件必须存在
    
    Args:
        task_id: 任务 ID
        
    Returns:
        Excel 文件
        
    Raises:
        HTTPException: 任务不存在或文件不存在
    """
    logger.info(f"下载任务 {task_id} 的 Excel 文件")
    
    # 检查任务是否存在
    task = await TaskService.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    
    # 检查 Excel 文件是否存在
    if not task.excel_path:
        raise HTTPException(status_code=400, detail="Excel 文件尚未生成")
    
    excel_path = Path(task.excel_path)
    if not excel_path.exists():
        raise HTTPException(status_code=404, detail="Excel 文件不存在")
    
    # 返回文件（图片名称_修改时间）
    image_stem = "image"
    if task.image_path:
        image_stem = Path(task.image_path).stem or image_stem

    # 仅保留安全字符，避免下载名异常
    image_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", image_stem).strip("_") or "image"

    updated_at = task.updated_at or datetime.utcnow()
    updated_stamp = updated_at.strftime("%Y%m%d_%H%M%S")
    filename = f"{image_stem}_{updated_stamp}.xlsx"
    return FileResponse(
        path=str(excel_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
