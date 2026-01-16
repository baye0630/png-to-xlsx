"""
性能监控和指标收集模块
"""
import time
from typing import Dict, Any, Optional
from contextlib import contextmanager
from collections import defaultdict
from datetime import datetime

from app.core.logging import logger


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self._metrics: Dict[str, Any] = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'errors': 0,
            'last_updated': None
        })
    
    def record_operation(
        self,
        operation: str,
        duration: float,
        success: bool = True
    ):
        """
        记录操作指标
        
        Args:
            operation: 操作名称
            duration: 操作耗时（秒）
            success: 是否成功
        """
        metric = self._metrics[operation]
        metric['count'] += 1
        metric['total_time'] += duration
        metric['min_time'] = min(metric['min_time'], duration)
        metric['max_time'] = max(metric['max_time'], duration)
        if not success:
            metric['errors'] += 1
        metric['last_updated'] = datetime.now()
        
        # 记录到日志
        status = "成功" if success else "失败"
        logger.info(
            f"[指标] {operation} - {status} | "
            f"耗时: {duration:.3f}s | "
            f"累计: {metric['count']}次"
        )
    
    def get_metrics(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """
        获取指标统计
        
        Args:
            operation: 操作名称，不指定则返回所有指标
            
        Returns:
            指标统计数据
        """
        if operation:
            metric = self._metrics.get(operation)
            if not metric:
                return {}
            
            avg_time = metric['total_time'] / metric['count'] if metric['count'] > 0 else 0
            error_rate = metric['errors'] / metric['count'] if metric['count'] > 0 else 0
            
            return {
                'operation': operation,
                'count': metric['count'],
                'errors': metric['errors'],
                'error_rate': f"{error_rate * 100:.2f}%",
                'avg_time': f"{avg_time:.3f}s",
                'min_time': f"{metric['min_time']:.3f}s",
                'max_time': f"{metric['max_time']:.3f}s",
                'last_updated': metric['last_updated'].isoformat() if metric['last_updated'] else None
            }
        else:
            # 返回所有指标
            result = {}
            for op, metric in self._metrics.items():
                avg_time = metric['total_time'] / metric['count'] if metric['count'] > 0 else 0
                error_rate = metric['errors'] / metric['count'] if metric['count'] > 0 else 0
                
                result[op] = {
                    'count': metric['count'],
                    'errors': metric['errors'],
                    'error_rate': f"{error_rate * 100:.2f}%",
                    'avg_time': f"{avg_time:.3f}s",
                    'min_time': f"{metric['min_time']:.3f}s",
                    'max_time': f"{metric['max_time']:.3f}s",
                    'last_updated': metric['last_updated'].isoformat() if metric['last_updated'] else None
                }
            
            return result
    
    def reset(self, operation: Optional[str] = None):
        """
        重置指标
        
        Args:
            operation: 操作名称，不指定则重置所有指标
        """
        if operation:
            if operation in self._metrics:
                del self._metrics[operation]
        else:
            self._metrics.clear()


# 全局指标收集器
_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """获取全局指标收集器"""
    return _metrics_collector


@contextmanager
def track_performance(operation: str):
    """
    性能追踪上下文管理器
    
    使用示例:
    with track_performance("ocr_processing"):
        # 执行操作
        pass
    """
    start_time = time.time()
    success = True
    
    try:
        yield
    except Exception as e:
        success = False
        raise
    finally:
        duration = time.time() - start_time
        _metrics_collector.record_operation(operation, duration, success)
