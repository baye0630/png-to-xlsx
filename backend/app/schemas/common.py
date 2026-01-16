"""
通用 Schema 定义
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel


T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[T] = None
    
    class Config:
        from_attributes = True
