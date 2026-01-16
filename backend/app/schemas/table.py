"""
表格数据 Schema 定义
用于前端预览和编辑的表格数据结构
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CellData(BaseModel):
    """单元格数据"""
    text: str = Field(default="", description="单元格文本内容")
    rowspan: int = Field(default=1, description="跨行数", ge=1)
    colspan: int = Field(default=1, description="跨列数", ge=1)
    is_header: bool = Field(default=False, description="是否为表头")


class TableSheet(BaseModel):
    """单个表格 Sheet 数据"""
    sheet_id: int = Field(description="Sheet ID (从 1 开始)")
    sheet_name: str = Field(description="Sheet 名称")
    rows: int = Field(description="行数", ge=0)
    cols: int = Field(description="列数", ge=0)
    data: List[List[CellData]] = Field(description="表格数据（二维数组）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sheet_id": 1,
                "sheet_name": "Table_1",
                "rows": 10,
                "cols": 5,
                "data": [
                    [
                        {"text": "标题", "rowspan": 1, "colspan": 2, "is_header": True},
                        {"text": "", "rowspan": 1, "colspan": 1, "is_header": True},
                        {"text": "备注", "rowspan": 1, "colspan": 1, "is_header": False}
                    ]
                ]
            }
        }


class TableDataResponse(BaseModel):
    """表格数据完整响应"""
    task_id: str = Field(description="任务 ID")
    status: str = Field(description="任务状态")
    total_sheets: int = Field(description="Sheet 总数", ge=0)
    sheets: List[TableSheet] = Field(description="所有 Sheet 数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "editable",
                "total_sheets": 2,
                "sheets": [
                    {
                        "sheet_id": 1,
                        "sheet_name": "Table_1",
                        "rows": 10,
                        "cols": 5,
                        "data": []
                    }
                ]
            }
        }


class TableMetadata(BaseModel):
    """表格元数据（轻量级，不包含完整数据）"""
    task_id: str = Field(description="任务 ID")
    status: str = Field(description="任务状态")
    total_sheets: int = Field(description="Sheet 总数", ge=0)
    sheets_info: List[Dict[str, Any]] = Field(
        description="Sheet 基本信息列表"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "editable",
                "total_sheets": 2,
                "sheets_info": [
                    {
                        "sheet_id": 1,
                        "sheet_name": "Table_1",
                        "rows": 10,
                        "cols": 5
                    }
                ]
            }
        }
