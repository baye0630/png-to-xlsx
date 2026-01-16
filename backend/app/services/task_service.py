"""
任务服务层
"""
from typing import Optional, List
from uuid import UUID, uuid4

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """任务服务类"""
    
    @staticmethod
    async def create_task() -> Task:
        """
        创建新任务
        
        Returns:
            Task: 新创建的任务对象
        """
        task = await Task.create(
            task_id=uuid4(),
            status=TaskStatus.UPLOADED
        )
        return task
    
    @staticmethod
    async def get_task(task_id: UUID) -> Optional[Task]:
        """
        根据 task_id 获取任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            Task: 任务对象，不存在时返回 None
        """
        return await Task.filter(task_id=task_id).first()
    
    @staticmethod
    async def get_tasks(
        skip: int = 0,
        limit: int = 100,
        status: Optional[TaskStatus] = None
    ) -> tuple[List[Task], int]:
        """
        获取任务列表
        
        Args:
            skip: 跳过的数量（分页）
            limit: 返回的数量（分页）
            status: 按状态过滤（可选）
            
        Returns:
            tuple: (任务列表, 总数)
        """
        query = Task.all()
        
        if status:
            query = query.filter(status=status)
        
        total = await query.count()
        tasks = await query.offset(skip).limit(limit).order_by("-created_at")
        
        return tasks, total
    
    @staticmethod
    async def update_task(task_id: UUID, update_data: TaskUpdate) -> Optional[Task]:
        """
        更新任务信息
        
        Args:
            task_id: 任务 ID
            update_data: 更新数据
            
        Returns:
            Task: 更新后的任务对象，不存在时返回 None
        """
        task = await Task.filter(task_id=task_id).first()
        if not task:
            return None
        
        # 只更新提供的字段
        update_dict = update_data.model_dump(exclude_unset=True)
        await task.update_from_dict(update_dict).save()
        
        return task
    
    @staticmethod
    async def update_task_status(
        task_id: UUID,
        status: TaskStatus,
        error_message: Optional[str] = None
    ) -> Optional[Task]:
        """
        更新任务状态（便捷方法）
        
        Args:
            task_id: 任务 ID
            status: 新状态
            error_message: 错误信息（可选）
            
        Returns:
            Task: 更新后的任务对象，不存在时返回 None
        """
        task = await Task.filter(task_id=task_id).first()
        if not task:
            return None
        
        task.status = status
        if error_message:
            task.error_message = error_message
        await task.save()
        
        return task
    
    @staticmethod
    async def delete_task(task_id: UUID) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            bool: 是否删除成功
        """
        deleted_count = await Task.filter(task_id=task_id).delete()
        return deleted_count > 0
