"""
OCR 相关 Schema 定义
"""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class OCRJobResponse(BaseModel):
    """OCR 任务响应模型"""
    task_id: UUID
    ocr_job_id: str
    status: str
    message: str
    
    class Config:
        from_attributes = True


class OCRHealthResponse(BaseModel):
    """OCR 健康检查响应模型"""
    healthy: bool
    service_info: Optional[dict] = None
    
    class Config:
        from_attributes = True
