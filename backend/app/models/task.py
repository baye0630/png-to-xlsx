"""
任务数据模型
"""
from tortoise import fields
from tortoise.models import Model
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    UPLOADED = "uploaded"                # 图片已上传
    OCR_PROCESSING = "ocr_processing"    # OCR 处理中
    OCR_DONE = "ocr_done"                # OCR 完成
    OCR_FAILED = "ocr_failed"            # OCR 失败
    EXCEL_GENERATED = "excel_generated"  # Excel 已生成
    EXCEL_FAILED = "excel_failed"        # Excel 生成失败
    EDITABLE = "editable"                # 可编辑状态


class Task(Model):
    """任务模型
    
    一个任务对应一次完整的图片识别与编辑导出流程
    """
    # 主键
    task_id = fields.UUIDField(pk=True)
    
    # 文件路径
    image_path = fields.CharField(max_length=512, null=True, description="上传图片的存储路径")
    ocr_json_path = fields.CharField(max_length=512, null=True, description="OCR 原始 JSON 结果路径")
    excel_path = fields.CharField(max_length=512, null=True, description="当前最新 Excel 文件路径")
    
    # OCR 相关
    ocr_job_id = fields.CharField(max_length=128, null=True, description="外部 OCR 服务的任务 ID")
    
    # 状态与错误信息
    status = fields.CharEnumField(
        TaskStatus, 
        max_length=32,
        default=TaskStatus.UPLOADED,
        description="任务状态"
    )
    error_message = fields.TextField(null=True, description="错误信息")
    
    # 时间戳
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    
    class Meta:
        table = "tasks"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Task({self.task_id}, status={self.status})"
