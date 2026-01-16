"""
上传服务层
"""
from pathlib import Path
from typing import Optional
from uuid import UUID
import aiofiles
from fastapi import UploadFile

from app.core.config import get_settings
from app.core.logging import logger
from app.services.task_service import TaskService
from app.models.task import TaskStatus


settings = get_settings()


class UploadService:
    """文件上传服务类"""
    
    # 支持的图片格式
    ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
    
    @staticmethod
    def get_image_storage_path(task_id: UUID, file_extension: str) -> Path:
        """
        获取图片存储路径
        
        存储规则：data/images/{task_id}.{ext}
        
        Args:
            task_id: 任务 ID
            file_extension: 文件扩展名（包含点，如 .png）
            
        Returns:
            Path: 图片存储的完整路径
        """
        images_dir = settings.data_paths["images"]
        filename = f"{task_id}{file_extension}"
        return Path(images_dir) / filename
    
    @staticmethod
    def validate_image_file(file: UploadFile) -> tuple[bool, Optional[str]]:
        """
        验证上传的图片文件
        
        Args:
            file: 上传的文件对象
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        # 检查文件名
        if not file.filename:
            return False, "文件名不能为空"
        
        # 获取文件扩展名
        file_extension = Path(file.filename).suffix.lower()
        
        # 检查文件类型
        if file_extension not in UploadService.ALLOWED_IMAGE_EXTENSIONS:
            return False, f"不支持的图片格式，支持的格式：{', '.join(UploadService.ALLOWED_IMAGE_EXTENSIONS)}"
        
        # 检查 content type
        if file.content_type and not file.content_type.startswith("image/"):
            return False, f"文件类型错误：{file.content_type}"
        
        return True, None
    
    @staticmethod
    async def save_uploaded_image(
        task_id: UUID,
        file: UploadFile
    ) -> tuple[bool, str, Optional[str]]:
        """
        保存上传的图片文件
        
        Args:
            task_id: 任务 ID
            file: 上传的文件对象
            
        Returns:
            tuple: (是否成功, 保存路径或错误信息, 文件大小信息)
        """
        try:
            # 验证文件
            is_valid, error_msg = UploadService.validate_image_file(file)
            if not is_valid:
                return False, error_msg, None
            
            # 获取文件扩展名
            file_extension = Path(file.filename).suffix.lower()
            
            # 确定存储路径
            storage_path = UploadService.get_image_storage_path(task_id, file_extension)
            
            # 确保目录存在
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 异步保存文件
            file_size = 0
            async with aiofiles.open(storage_path, 'wb') as f:
                while chunk := await file.read(8192):  # 8KB chunks
                    await f.write(chunk)
                    file_size += len(chunk)
            
            # 验证文件是否保存成功
            if not storage_path.exists():
                return False, "文件保存失败", None
            
            # 构造相对路径（使用绝对路径以避免路径问题）
            # 存储绝对路径，但如果可能则转换为相对路径
            try:
                # 尝试获取相对于项目根目录的路径
                project_root = Path.cwd().parent if Path.cwd().name == "backend" else Path.cwd()
                relative_path = str(storage_path.relative_to(project_root))
            except ValueError:
                # 如果无法计算相对路径，使用绝对路径
                relative_path = str(storage_path.absolute())
            
            # 格式化文件大小
            size_info = UploadService.format_file_size(file_size)
            
            logger.info(f"图片保存成功: task_id={task_id}, path={relative_path}, size={size_info}")
            
            return True, relative_path, size_info
            
        except Exception as e:
            logger.error(f"保存图片失败: task_id={task_id}, error={str(e)}")
            return False, f"保存失败: {str(e)}", None
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes: 文件大小（字节）
            
        Returns:
            str: 格式化后的大小（如 "1.23 MB"）
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    @staticmethod
    async def upload_and_bind_image(
        task_id: UUID,
        file: UploadFile
    ) -> tuple[bool, str]:
        """
        上传图片并与任务绑定（一站式服务）
        
        Args:
            task_id: 任务 ID
            file: 上传的文件对象
            
        Returns:
            tuple: (是否成功, 消息)
        """
        # 1. 检查任务是否存在
        task = await TaskService.get_task(task_id)
        if not task:
            return False, f"任务不存在: {task_id}"
        
        # 2. 保存图片
        success, path_or_error, size_info = await UploadService.save_uploaded_image(task_id, file)
        if not success:
            return False, path_or_error
        
        # 3. 更新任务的 image_path
        task.image_path = path_or_error
        task.status = TaskStatus.UPLOADED
        await task.save()
        
        message = f"图片上传成功，已保存到: {path_or_error}"
        if size_info:
            message += f"，大小: {size_info}"
        
        return True, message
    
    @staticmethod
    def delete_image(image_path: str) -> bool:
        """
        删除图片文件
        
        Args:
            image_path: 图片路径
            
        Returns:
            bool: 是否删除成功
        """
        try:
            path = Path(image_path)
            if path.exists():
                path.unlink()
                logger.info(f"图片删除成功: {image_path}")
                return True
            else:
                logger.warning(f"图片不存在: {image_path}")
                return False
        except Exception as e:
            logger.error(f"删除图片失败: {image_path}, error={str(e)}")
            return False
