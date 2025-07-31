from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Type, Union
import functools
import logging
import time
from django.conf import settings
from django.core.cache import cache
import traceback
from config.exception_config import (
    EXCEPTION_HANDLING_CONFIG,
    PERFORMANCE_MONITORING_CONFIG,
    SENSITIVE_DATA_CONFIG,
    ALERT_CONFIG,
    EXCEPTION_CATEGORIES
)

"""
异常处理工具模块

该模块提供异常处理相关的工具函数和装饰器，包括异常捕获、
重试机制、异常统计等功能。遵循Django最佳实践和Google Python Style Guide。

设计原则：
- 健壮性：全面的异常捕获和处理机制
- 通用性：适用于各种场景的工具函数
- 可观测性：详细的异常统计和监控
- 性能优化：最小化性能开销
"""

logger = logging.getLogger(__name__)

class ExceptionStatistics:
    """异常统计类"""

    def __init__(self):
        self.cache_prefix = 'exception_stats'
        self.cache_timeout = 3600  # 1小时

    def record_exception(self, exception_type: str, path: str, user_id: Optional[str] = None):
        """记录异常统计"""
        timestamp = datetime.now()

        # 记录总体异常统计
        self._increment_counter(f"{self.cache_prefix}:total")
        self._increment_counter(f"{self.cache_prefix}:by_type:{exception_type}")
        self._increment_counter(f"{self.cache_prefix}:by_path:{path}")

        if user_id:
            self._increment_counter(f"{self.cache_prefix}:by_user:{user_id}")

        # 记录时间窗口统计（最近1小时）
        hour_key = timestamp.strftime("%Y%m%d%H")
        self._increment_counter(f"{self.cache_prefix}:hourly:{hour_key}")

        # 记录连续异常
        self._record_consecutive_errors(path)

    def _increment_counter(self, key: str):
        """增加计数器"""
        try:
            current = cache.get(key, 0)
            cache.set(key, current + 1, self.cache_timeout)
        except Exception as e:
            logger.warning(f"Failed to increment counter {key}: {e}")

    def _record_consecutive_errors(self, path: str):
        """记录连续异常"""
        key = f"{self.cache_prefix}:consecutive:{path}"
        try:
            consecutive = cache.get(key, 0) + 1
            cache.set(key, consecutive, 300)  # 5分钟超时

            # 检查是否需要告警
            threshold = ALERT_CONFIG['ALERT_THRESHOLDS']['CONSECUTIVE_ERRORS']
            if consecutive >= threshold:
                self._trigger_alert(f"Consecutive errors on {path}: {consecutive}")
        except Exception as e:
            logger.warning(f"Failed to record consecutive errors: {e}")

    def _trigger_alert(self, message: str):
        """触发告警"""
        if ALERT_CONFIG['ENABLE_EMAIL_ALERTS']:
            # 这里可以集成邮件发送功能
            logger.critical(f"ALERT: {message}")

    def get_statistics(self) -> Dict[str, Any]:
        """获取异常统计信息"""
        try:
            stats = {
                'total_exceptions': cache.get(f"{self.cache_prefix}:total", 0),
                'by_type': {},
                'by_path': {},
                'hourly': {}
            }

            # 获取按类型统计
            for category, exceptions in EXCEPTION_CATEGORIES.items():
                for exc_type in exceptions:
                    count = cache.get(f"{self.cache_prefix}:by_type:{exc_type}", 0)
                    if count > 0:
                        stats['by_type'][exc_type] = count

            return stats
        except Exception as e:
            logger.warning(f"Failed to get statistics: {e}")
            return {}

class SensitiveDataFilter:
    """敏感数据过滤器"""

    def filter_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """过滤字典中的敏感数据"""
        if not self.enabled or not isinstance(data, dict):
            return data

        filtered_data = {}
        for key, value in data.items():
            if self._is_sensitive_field(key):
                filtered_data[key] = self.replacement
            elif isinstance(value, dict):
                filtered_data[key] = self.filter_dict(value)
            elif isinstance(value, list):
                filtered_data[key] = self.filter_list(value)
            else:
                filtered_data[key] = value

        return filtered_data

    def filter_list(self, data: List[Any]) -> List[Any]:
        """过滤列表中的敏感数据"""
        if not self.enabled or not isinstance(data, list):
            return data

        filtered_data = []
        for item in data:
            if isinstance(item, dict):
                filtered_data.append(self.filter_dict(item))
            elif isinstance(item, list):
                filtered_data.append(self.filter_list(item))
            else:
                filtered_data.append(item)

        return filtered_data

    def filter_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """过滤HTTP头中的敏感数据"""
        if not self.enabled or not isinstance(headers, dict):
            return headers

        filtered_headers = {}
        for key, value in headers.items():
            if self._is_sensitive_header(key):
                filtered_headers[key] = self.replacement
            else:
                filtered_headers[key] = value

        return filtered_headers

    def _is_sensitive_field(self, field_name: str) -> bool:
        """检查字段名是否敏感"""
        return field_name.lower() in self.sensitive_fields

    def _is_sensitive_header(self, header_name: str) -> bool:
        """检查HTTP头是否敏感"""
        return header_name.lower() in self.sensitive_headers

def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    异常重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 退避倍数
        exceptions: 需要重试的异常类型
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise

                    logger.warning(
                        f"Function {func.__name__} failed on attempt {attempt + 1}, "
                        f"retrying in {current_delay}s: {e}"
                    )

                    time.sleep(current_delay)
                    current_delay *= backoff

            raise last_exception

        return wrapper
    return decorator

def safe_execute(
    func: Callable,
    default_return: Any = None,
    log_exceptions: bool = True,
    exception_types: tuple = (Exception,)
) -> Any:
    """
    安全执行函数，捕获异常并返回默认值

    Args:
        func: 要执行的函数
        default_return: 异常时的默认返回值
        log_exceptions: 是否记录异常日志
        exception_types: 要捕获的异常类型

    Returns:
        函数执行结果或默认值
    """
    try:
        return func()
    except exception_types as e:
        if log_exceptions:
            logger.exception(f"Safe execution failed for {func.__name__}: {e}")
        return default_return

def exception_context(
    operation_name: str,
    log_level: str = 'ERROR',
    reraise: bool = True
):
    """
    异常上下文管理器装饰器

    Args:
        operation_name: 操作名称
        log_level: 日志级别
        reraise: 是否重新抛出异常
    """
    return decorator

def get_exception_info(exception: Exception) -> Dict[str, Any]:
    """
    获取异常详细信息

    Args:
        exception: 异常对象

    Returns:
        异常信息字典
    """
    return {
        'type': type(exception).__name__,
        'message': str(exception),
        'module': getattr(exception, '__module__', 'unknown'),
        'traceback': traceback.format_exc() if settings.DEBUG else None,
        'timestamp': datetime.now().isoformat(),
        'args': getattr(exception, 'args', []),
    }

def categorize_exception(exception: Exception) -> str:
    """
    对异常进行分类

    Args:
        exception: 异常对象

    Returns:
        异常分类
    """
    exception_type = f"{exception.__class__.__module__}.{exception.__class__.__name__}"

    for category, exception_types in EXCEPTION_CATEGORIES.items():
        if exception_type in exception_types:
            return category

    return 'UNKNOWN'

def format_exception_for_logging(
    exception: Exception,
    request_data: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    格式化异常信息用于日志记录

    Args:
        exception: 异常对象
        request_data: 请求数据
        user_id: 用户ID
        request_id: 请求ID

    Returns:
        格式化的异常信息
    """
    filter_tool = SensitiveDataFilter()

    log_data = {
        'exception_info': get_exception_info(exception),
        'category': categorize_exception(exception),
        'user_id': user_id,
        'request_id': request_id,
        'timestamp': datetime.now().isoformat(),
    }

    if request_data:
        log_data['request_data'] = filter_tool.filter_dict(request_data)

    return log_data

# 全局异常统计实例
exception_stats = ExceptionStatistics()