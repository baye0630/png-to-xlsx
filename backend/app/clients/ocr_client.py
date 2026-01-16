"""
OCR 服务客户端
封装 PaddleOCR 表格识别服务的调用
"""
from typing import Optional, Dict, Any, Tuple
import httpx
from pathlib import Path

from app.core.config import get_settings
from app.core.logging import logger
from app.utils.retry import with_retry, RetryConfig


settings = get_settings()


class OCRClient:
    """OCR 服务客户端"""
    
    def __init__(self):
        self.base_url = settings.ocr_base_url
        self.token = settings.ocr_token
        self.timeout = 30.0  # 默认超时 30 秒
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    async def health_check(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        健康检查
        
        Returns:
            tuple: (是否成功, 响应数据)
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"OCR 服务健康检查成功: {data}")
                    return True, data
                else:
                    logger.error(f"OCR 服务健康检查失败: status={response.status_code}")
                    return False, None
                    
        except Exception as e:
            logger.error(f"OCR 服务健康检查异常: {str(e)}")
            return False, None
    
    @with_retry(
        max_retries=RetryConfig.OCR_MAX_RETRIES,
        initial_delay=RetryConfig.OCR_INITIAL_DELAY,
        backoff_factor=RetryConfig.OCR_BACKOFF_FACTOR,
        exceptions=(httpx.HTTPError, httpx.TimeoutException)
    )
    async def create_job_from_file(
        self, 
        image_path: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        上传图片创建 OCR 任务（带重试）
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            tuple: (是否成功, job_id, 错误信息)
        """
        try:
            # 验证文件存在
            file_path = Path(image_path)
            if not file_path.exists():
                error_msg = f"图片文件不存在: {image_path}"
                logger.error(error_msg)
                return False, None, error_msg
            
            # 读取文件
            with open(file_path, 'rb') as f:
                files = {
                    'file': (file_path.name, f, 'image/png')
                }
                
                # 发送请求
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/jobs-from-uploading",
                        headers=self._get_headers(),
                        files=files
                    )
                    
                    # 接受 200 或 201 作为成功状态码
                    if response.status_code in [200, 201]:
                        data = response.json()
                        job_id = data.get('job_id')
                        
                        if job_id:
                            logger.info(f"OCR 任务创建成功: job_id={job_id}, status={response.status_code}")
                            return True, job_id, None
                        else:
                            error_msg = "响应中未包含 job_id"
                            logger.error(f"OCR 任务创建失败: {error_msg}, response={data}")
                            return False, None, error_msg
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                        logger.error(f"OCR 任务创建失败: {error_msg}")
                        return False, None, error_msg
                        
        except Exception as e:
            error_msg = f"创建 OCR 任务异常: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    async def get_job_status(
        self, 
        job_id: str,
        since_seq: int = 0,
        timeout_ms: int = 25000,
        max_events: int = 50
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        长轮询获取任务状态
        
        Args:
            job_id: 任务 ID
            since_seq: 起始序号
            timeout_ms: 超时时间（毫秒）
            max_events: 最大事件数
            
        Returns:
            tuple: (是否成功, 事件数据, 错误信息)
        """
        try:
            params = {
                'since_seq': since_seq,
                'timeout_ms': timeout_ms,
                'max_events': max_events
            }
            
            async with httpx.AsyncClient(timeout=timeout_ms / 1000 + 5) as client:
                response = await client.get(
                    f"{self.base_url}/longpoll/jobs/{job_id}",
                    headers=self._get_headers(),
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"获取 OCR 任务状态成功: job_id={job_id}, done={data.get('done')}")
                    return True, data, None
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(f"获取 OCR 任务状态失败: {error_msg}")
                    return False, None, error_msg
                    
        except Exception as e:
            error_msg = f"获取 OCR 任务状态异常: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    @with_retry(
        max_retries=RetryConfig.OCR_MAX_RETRIES,
        initial_delay=RetryConfig.OCR_INITIAL_DELAY,
        backoff_factor=RetryConfig.OCR_BACKOFF_FACTOR,
        exceptions=(httpx.HTTPError, httpx.TimeoutException)
    )
    async def get_job_result_json(
        self, 
        job_id: str
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        获取 OCR 任务的 JSON 结果（带重试）
        
        Args:
            job_id: 任务 ID
            
        Returns:
            tuple: (是否成功, JSON 数据, 错误信息)
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/result/json/jobs/{job_id}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"获取 OCR JSON 结果成功: job_id={job_id}")
                    return True, data, None
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(f"获取 OCR JSON 结果失败: {error_msg}")
                    return False, None, error_msg
                    
        except Exception as e:
            error_msg = f"获取 OCR JSON 结果异常: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg


# 单例
_ocr_client = None


def get_ocr_client() -> OCRClient:
    """获取 OCR 客户端单例"""
    global _ocr_client
    if _ocr_client is None:
        _ocr_client = OCRClient()
    return _ocr_client
