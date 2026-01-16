"""
上传相关 Schema 定义
"""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """上传响应模型"""
    task_id: UUID
    image_path: str
    file_size: Optional[str] = None
    message: str
    
    class Config:
        from_attributes = True
