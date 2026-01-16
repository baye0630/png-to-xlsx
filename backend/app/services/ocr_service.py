"""
OCR 服务层
封装 OCR 相关的业务逻辑
"""
from typing import Optional, Tuple
from uuid import UUID
import json
from pathlib import Path
import asyncio

from app.clients.ocr_client import get_ocr_client
from app.services.task_service import TaskService
from app.models.task import TaskStatus
from app.core.logging import logger
from app.core.config import get_settings

settings = get_settings()


class OCRService:
    """OCR 服务类"""
    
    @staticmethod
    async def start_ocr_job(task_id: UUID) -> Tuple[bool, str]:
        """
        启动 OCR 任务
        
        流程：
        1. 获取任务信息
        2. 验证图片路径存在
        3. 上传图片到 OCR 服务
        4. 获取 job_id
        5. 更新任务的 ocr_job_id 和状态
        
        Args:
            task_id: 任务 ID
            
        Returns:
            tuple: (是否成功, 消息)
        """
        # 1. 获取任务
        task = await TaskService.get_task(task_id)
        if not task:
            return False, f"任务不存在: {task_id}"
        
        # 2. 验证图片路径
        if not task.image_path:
            return False, "任务尚未上传图片"
        
        logger.info(f"开始 OCR 任务: task_id={task_id}, image_path={task.image_path}")
        
        # 3. 上传图片到 OCR 服务
        ocr_client = get_ocr_client()
        success, job_id, error_msg = await ocr_client.create_job_from_file(task.image_path)
        
        if not success:
            # OCR 任务创建失败
            error_message = f"OCR 任务创建失败: {error_msg}"
            task.status = TaskStatus.OCR_FAILED
            task.error_message = error_message
            await task.save()
            logger.error(f"{error_message}, task_id={task_id}")
            return False, error_message
        
        # 4. 更新任务信息
        task.ocr_job_id = job_id
        task.status = TaskStatus.OCR_PROCESSING
        task.error_message = None  # 清除之前的错误信息
        await task.save()
        
        logger.info(f"OCR 任务创建成功: task_id={task_id}, job_id={job_id}, status={task.status}")
        
        return True, f"OCR 任务创建成功，job_id: {job_id}"
    
    @staticmethod
    async def check_ocr_health() -> Tuple[bool, Optional[dict]]:
        """
        检查 OCR 服务健康状态
        
        Returns:
            tuple: (是否健康, 健康信息)
        """
        ocr_client = get_ocr_client()
        return await ocr_client.health_check()
    
    @staticmethod
    async def get_ocr_job_status(job_id: str) -> Tuple[bool, Optional[dict], Optional[str]]:
        """
        获取 OCR 任务状态
        
        Args:
            job_id: OCR 任务 ID
            
        Returns:
            tuple: (是否成功, 状态数据, 错误信息)
        """
        ocr_client = get_ocr_client()
        return await ocr_client.get_job_status(job_id)
    
    @staticmethod
    async def get_ocr_result_json(job_id: str) -> Tuple[bool, Optional[dict], Optional[str]]:
        """
        获取 OCR 任务的 JSON 结果
        
        Args:
            job_id: OCR 任务 ID
            
        Returns:
            tuple: (是否成功, JSON 数据, 错误信息)
        """
        ocr_client = get_ocr_client()
        return await ocr_client.get_job_result_json(job_id)
    
    @staticmethod
    async def poll_and_fetch_result(task_id: UUID, max_wait_seconds: int = 300) -> Tuple[bool, str]:
        """
        轮询 OCR 任务状态并获取结果
        
        流程：
        1. 获取任务信息（包含 ocr_job_id）
        2. 长轮询任务状态，直到完成或失败
        3. 如果成功，获取 OCR JSON 结果
        4. 保存 JSON 到文件
        5. 更新任务状态为 ocr_done
        
        Args:
            task_id: 任务 ID
            max_wait_seconds: 最大等待时间（秒）
            
        Returns:
            tuple: (是否成功, 消息)
        """
        # 1. 获取任务
        task = await TaskService.get_task(task_id)
        if not task:
            return False, f"任务不存在: {task_id}"
        
        if not task.ocr_job_id:
            return False, "任务尚未创建 OCR job"
        
        job_id = task.ocr_job_id
        logger.info(f"开始轮询 OCR 任务: task_id={task_id}, job_id={job_id}")
        
        # 2. 轮询任务状态
        ocr_client = get_ocr_client()
        since_seq = 0
        start_time = asyncio.get_event_loop().time()
        is_done = False
        is_success = False
        last_event_type = None
        
        while not is_done:
            # 检查超时
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > max_wait_seconds:
                error_msg = f"OCR 任务超时（{max_wait_seconds}秒）"
                task.status = TaskStatus.OCR_FAILED
                task.error_message = error_msg
                await task.save()
                logger.error(f"{error_msg}: task_id={task_id}, job_id={job_id}")
                return False, error_msg
            
            # 长轮询获取状态
            success, status_data, error_msg = await ocr_client.get_job_status(
                job_id, 
                since_seq=since_seq,
                timeout_ms=25000
            )
            
            if not success:
                error_message = f"获取 OCR 任务状态失败: {error_msg}"
                task.status = TaskStatus.OCR_FAILED
                task.error_message = error_message
                await task.save()
                logger.error(f"{error_message}: task_id={task_id}, job_id={job_id}")
                return False, error_message
            
            # 解析状态
            is_done = status_data.get('done', False)
            events = status_data.get('events', [])
            last_seq = status_data.get('last_seq', since_seq)
            
            # 记录事件
            for event in events:
                event_type = event.get('type')
                logger.info(f"OCR 任务事件: task_id={task_id}, job_id={job_id}, event={event_type}")
                last_event_type = event_type
                
                if event_type == 'finished':
                    is_success = True
                elif event_type == 'failed':
                    is_success = False
            
            # 更新序号，准备下次轮询
            since_seq = last_seq
            
            # 如果未完成，短暂等待后继续（避免过于频繁）
            if not is_done:
                await asyncio.sleep(1)
        
        # 3. 根据最终状态处理
        if not is_success:
            error_msg = f"OCR 任务失败: 最后事件={last_event_type}"
            task.status = TaskStatus.OCR_FAILED
            task.error_message = error_msg
            await task.save()
            logger.error(f"{error_msg}: task_id={task_id}, job_id={job_id}")
            return False, error_msg
        
        logger.info(f"OCR 任务完成: task_id={task_id}, job_id={job_id}")
        
        # 4. 获取 OCR JSON 结果
        success, json_data, error_msg = await ocr_client.get_job_result_json(job_id)
        
        if not success:
            error_message = f"获取 OCR JSON 结果失败: {error_msg}"
            task.status = TaskStatus.OCR_FAILED
            task.error_message = error_message
            await task.save()
            logger.error(f"{error_message}: task_id={task_id}, job_id={job_id}")
            return False, error_message
        
        # 5. 保存 JSON 到文件
        ocr_json_dir = Path(settings.data_paths['ocr_json'])
        ocr_json_dir.mkdir(parents=True, exist_ok=True)
        
        json_filename = f"{task_id}.json"
        json_path = ocr_json_dir / json_filename
        
        # 转换为绝对路径
        json_path_abs = json_path.resolve()
        
        # 清理 JSON 数据中的转义双引号
        try:
            for page in json_data.get('pages', []):
                for block in page.get('parsing_res_list', []):
                    if 'block_content' in block and block['block_content']:
                        # 将 \" 替换为 "
                        block['block_content'] = block['block_content'].replace('\\"', '"')
        except Exception as e:
            logger.warning(f"清理转义字符时出错: {str(e)}")
        
        try:
            with open(json_path_abs, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            logger.info(f"OCR JSON 已保存: task_id={task_id}, path={json_path_abs}")
        except Exception as e:
            error_msg = f"保存 OCR JSON 失败: {str(e)}"
            task.status = TaskStatus.OCR_FAILED
            task.error_message = error_msg
            await task.save()
            logger.error(f"{error_msg}: task_id={task_id}")
            return False, error_msg
        
        # 6. 更新任务状态（保存绝对路径）
        task.ocr_json_path = str(json_path_abs)
        task.status = TaskStatus.OCR_DONE
        task.error_message = None
        await task.save()
        
        logger.info(f"OCR 任务完成并保存: task_id={task_id}, status={task.status}, json_path={json_path_abs}")
        
        return True, f"OCR 任务完成，JSON 已保存到: {json_path_abs}"
