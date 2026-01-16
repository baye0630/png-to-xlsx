"""
表格数据相关 API 路由
"""
from uuid import UUID
from fastapi import APIRouter, HTTPException, Path as PathParam, Body

from app.services.table_service import TableService
from app.services.task_service import TaskService
from app.schemas.common import ResponseModel
from app.schemas.table import TableDataResponse, TableMetadata
from app.core.logging import logger


router = APIRouter(prefix="/table", tags=["表格数据服务"])


@router.get(
    "/data/{task_id}",
    response_model=ResponseModel,
    summary="获取表格数据（完整）"
)
async def get_table_data(
    task_id: UUID = PathParam(..., description="任务 ID")
):
    """
    获取任务的完整表格数据（供前端预览/编辑）
    
    直接从 OCR JSON 提取表格数据，转换为前端需要的格式
    
    前置条件：
    - 任务状态必须为 ocr_done / excel_generated / editable
    - OCR JSON 文件必须存在
    
    Args:
        task_id: 任务 ID
        
    Returns:
        完整的表格数据（包含所有单元格内容）
        
    Raises:
        HTTPException: 任务不存在或状态错误
    """
    logger.info(f"获取任务 {task_id} 的表格数据")
    
    # 检查任务是否存在
    task = await TaskService.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    
    # 获取表格数据
    success, message, table_data = await TableService.get_table_data(task_id)
    
    if not success:
        logger.error(f"获取表格数据失败: {message}")
        raise HTTPException(status_code=400, detail=message)
    
    return ResponseModel(
        success=True,
        message=message,
        data=table_data.model_dump()
    )


@router.get(
    "/metadata/{task_id}",
    response_model=ResponseModel,
    summary="获取表格元数据（轻量级）"
)
async def get_table_metadata(
    task_id: UUID = PathParam(..., description="任务 ID")
):
    """
    获取任务的表格元数据（不包含完整数据）
    
    用于快速获取表格基本信息（Sheet 数量、行列数等）
    
    前置条件：
    - 任务状态必须为 ocr_done / excel_generated / editable
    - OCR JSON 文件必须存在
    
    Args:
        task_id: 任务 ID
        
    Returns:
        表格元数据（Sheet 基本信息）
        
    Raises:
        HTTPException: 任务不存在或状态错误
    """
    logger.info(f"获取任务 {task_id} 的表格元数据")
    
    # 检查任务是否存在
    task = await TaskService.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    
    # 获取表格元数据
    success, message, metadata = await TableService.get_table_metadata(task_id)
    
    if not success:
        logger.error(f"获取表格元数据失败: {message}")
        raise HTTPException(status_code=400, detail=message)
    
    return ResponseModel(
        success=True,
        message=message,
        data=metadata.model_dump()
    )


@router.post(
    "/save/{task_id}",
    response_model=ResponseModel,
    summary="保存表格数据"
)
async def save_table_data(
    task_id: UUID = PathParam(..., description="任务 ID"),
    table_data: TableDataResponse = Body(..., description="表格数据")
):
    """
    保存编辑后的表格数据
    
    将前端编辑后的表格数据保存，并重新生成 Excel 文件
    
    Args:
        task_id: 任务 ID
        table_data: 完整的表格数据
        
    Returns:
        保存结果
        
    Raises:
        HTTPException: 任务不存在或保存失败
    """
    logger.info(f"保存任务 {task_id} 的表格数据")
    
    # 检查任务是否存在
    task = await TaskService.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    
    # 保存表格数据
    success, message = await TableService.save_table_data(task_id, table_data)
    
    if not success:
        logger.error(f"保存表格数据失败: {message}")
        raise HTTPException(status_code=400, detail=message)
    
    return ResponseModel(
        success=True,
        message=message,
        data={"task_id": str(task_id)}
    )
