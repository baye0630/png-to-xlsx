"""
任务相关 API 路由
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query

from app.services.task_service import TaskService
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)
from app.schemas.common import ResponseModel
from app.models.task import TaskStatus
from app.utils.metrics import get_metrics_collector


router = APIRouter(prefix="/tasks", tags=["任务管理"])


@router.post("/", response_model=ResponseModel[TaskResponse], summary="创建任务")
async def create_task():
    """
    创建新任务
    
    - 自动生成 task_id
    - 初始状态为 uploaded
    """
    task = await TaskService.create_task()
    return ResponseModel(
        success=True,
        message="任务创建成功",
        data=TaskResponse.model_validate(task)
    )


@router.get("/{task_id}", response_model=ResponseModel[TaskResponse], summary="获取任务详情")
async def get_task(task_id: UUID):
    """
    根据 task_id 获取任务详情
    
    Args:
        task_id: 任务 ID (UUID)
    
    Returns:
        任务详情
    
    Raises:
        HTTPException: 任务不存在时返回 404
    """
    task = await TaskService.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return ResponseModel(
        success=True,
        message="获取任务成功",
        data=TaskResponse.model_validate(task)
    )


@router.get("/", response_model=ResponseModel[TaskListResponse], summary="获取任务列表")
async def get_tasks(
    skip: int = Query(0, ge=0, description="跳过的数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回的数量"),
    status: Optional[TaskStatus] = Query(None, description="按状态过滤")
):
    """
    获取任务列表（支持分页和过滤）
    
    Args:
        skip: 跳过的数量（分页）
        limit: 返回的数量（分页）
        status: 按状态过滤（可选）
    
    Returns:
        任务列表和总数
    """
    tasks, total = await TaskService.get_tasks(skip=skip, limit=limit, status=status)
    
    return ResponseModel(
        success=True,
        message="获取任务列表成功",
        data=TaskListResponse(
            total=total,
            tasks=[TaskResponse.model_validate(task) for task in tasks]
        )
    )


@router.patch("/{task_id}", response_model=ResponseModel[TaskResponse], summary="更新任务")
async def update_task(task_id: UUID, update_data: TaskUpdate):
    """
    更新任务信息
    
    Args:
        task_id: 任务 ID (UUID)
        update_data: 更新数据（只更新提供的字段）
    
    Returns:
        更新后的任务信息
    
    Raises:
        HTTPException: 任务不存在时返回 404
    """
    task = await TaskService.update_task(task_id, update_data)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return ResponseModel(
        success=True,
        message="任务更新成功",
        data=TaskResponse.model_validate(task)
    )


@router.patch("/{task_id}/status", response_model=ResponseModel[TaskResponse], summary="更新任务状态")
async def update_task_status(
    task_id: UUID,
    status: TaskStatus = Query(..., description="新状态"),
    error_message: Optional[str] = Query(None, description="错误信息")
):
    """
    更新任务状态（便捷接口）
    
    Args:
        task_id: 任务 ID (UUID)
        status: 新状态
        error_message: 错误信息（可选）
    
    Returns:
        更新后的任务信息
    
    Raises:
        HTTPException: 任务不存在时返回 404
    """
    task = await TaskService.update_task_status(task_id, status, error_message)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return ResponseModel(
        success=True,
        message="任务状态更新成功",
        data=TaskResponse.model_validate(task)
    )


@router.delete("/{task_id}", response_model=ResponseModel[None], summary="删除任务")
async def delete_task(task_id: UUID):
    """
    删除任务
    
    Args:
        task_id: 任务 ID (UUID)
    
    Returns:
        删除成功的消息
    
    Raises:
        HTTPException: 任务不存在时返回 404
    """
    success = await TaskService.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return ResponseModel(
        success=True,
        message="任务删除成功",
        data=None
    )


@router.get("/metrics/summary", response_model=ResponseModel, summary="获取系统指标")
async def get_metrics():
    """
    获取系统性能指标
    
    Returns:
        系统指标统计信息
    """
    collector = get_metrics_collector()
    metrics = collector.get_metrics()
    
    return ResponseModel(
        success=True,
        message="获取指标成功",
        data=metrics
    )
