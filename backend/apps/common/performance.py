"""
性能监控和优化工具

该文件提供性能监控和优化相关的工具函数。
遵循Django最佳实践和Google Python Style Guide。
"""

from typing import Dict, Any, Optional
import time
from django.core.cache import cache

class SimplePerformanceTracker:
    """简单的性能跟踪器"""

    @staticmethod
    def record_request(endpoint: str, method: str, response_time: float, status_code: int) -> None:
        """记录请求性能数据"""
        cache_key = f"perf_{method}_{endpoint}"

        # 获取现有统计
        stats = cache.get(cache_key, {
            'count': 0,
            'total_time': 0.0,
            'error_count': 0
        })

        # 更新统计
        stats['count'] += 1
        stats['total_time'] += response_time
        if status_code >= 400:
            stats['error_count'] += 1

        # 保存统计（缓存1小时）
        cache.set(cache_key, stats, 3600)

    @staticmethod
    def get_stats(endpoint: str = None, method: str = None) -> Dict[str, Any]:
        """获取性能统计"""
        if endpoint and method:
            cache_key = f"perf_{method}_{endpoint}"
            stats = cache.get(cache_key, {})

            if stats and stats.get('count', 0) > 0:
                return {
                    'endpoint': f"{method} {endpoint}",
                    'total_requests': stats['count'],
                    'avg_response_time': stats['total_time'] / stats['count'],
                    'error_rate': stats['error_count'] / stats['count']
                }

        return {}

# 全局性能跟踪器实例
performance_tracker = SimplePerformanceTracker()

def get_performance_stats() -> Dict[str, Any]:
    """获取性能统计信息"""
    return {
        'message': 'Performance tracking is active',
        'tracker': 'SimplePerformanceTracker'
    }

def get_endpoint_stats(endpoint: Optional[str] = None) -> Dict[str, Any]:
    """获取端点统计信息"""
    if endpoint:
        # 尝试从缓存中获取统计信息
        cache_key = f"perf_GET_{endpoint}"
        stats = cache.get(cache_key, {})
        if stats:
            return {
                'endpoint': endpoint,
                'stats': stats
            }

    return {
        'endpoint': endpoint,
        'message': 'No statistics available'
    }