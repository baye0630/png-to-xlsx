"""
任务相关 Schema 定义
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.task import TaskStatus


class TaskBase(BaseModel):
    """任务基础模型"""
    pass


class TaskCreate(TaskBase):
    """创建任务的请求模型"""
    # 创建时不需要任何字段，系统会自动生成 task_id 和初始状态
    pass


class TaskUpdate(BaseModel):
    """更新任务的请求模型"""
    image_path: Optional[str] = None
    ocr_json_path: Optional[str] = None
    excel_path: Optional[str] = None
    ocr_job_id: Optional[str] = None
    status: Optional[TaskStatus] = None
    error_message: Optional[str] = None


class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: UUID
    image_path: Optional[str] = None
    ocr_json_path: Optional[str] = None
    excel_path: Optional[str] = None
    ocr_job_id: Optional[str] = None
    status: TaskStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    total: int
    tasks: List[TaskResponse]
    
    class Config:
        from_attributes = True
