"""
日志工具模块

该文件提供日志相关的工具函数。
遵循Django最佳实践和Google Python Style Guide。
"""

from typing import Any, Dict, Optional, Callable, Union
import functools
import time
from config.logging_config import get_request_logger
from contextlib import contextmanager
from loguru import logger
from ..middleware import (
    get_current_request_id,
    get_current_user_id,
    get_current_endpoint,
)


class RequestLogger:
    """
    请求日志记录器

    提供便捷的日志记录方法，自动包含请求上下文信息。
    """

    @staticmethod
    def get_logger():
        """获取当前请求的日志记录器"""
        request_id = get_current_request_id()
        user_id = get_current_user_id()
        endpoint = get_current_endpoint()

        if request_id:
            return get_request_logger(
                request_id=request_id, user_id=user_id, endpoint=endpoint
            )
        else:
            # 如果没有请求上下文，返回默认日志记录器
            return logger

    @staticmethod
    def info(message: str, **kwargs):
        """记录信息级别日志"""
        RequestLogger.get_logger().info(message, **kwargs)

    @staticmethod
    def warning(message: str, **kwargs):
        """记录警告级别日志"""
        RequestLogger.get_logger().warning(message, **kwargs)

    @staticmethod
    def error(message: str, **kwargs):
        """记录错误级别日志"""
        RequestLogger.get_logger().error(message, **kwargs)

    @staticmethod
    def debug(message: str, **kwargs):
        """记录调试级别日志"""
        RequestLogger.get_logger().debug(message, **kwargs)

    @staticmethod
    def critical(message: str, **kwargs):
        """记录严重错误级别日志"""
        RequestLogger.get_logger().critical(message, **kwargs)


def log_function_call(
    level: str = "info",
    include_args: bool = False,
    include_result: bool = False,
    exclude_args: Optional[list] = None,
):
    """
    函数调用日志装饰器

    Args:
        level: 日志级别 (debug, info, warning, error, critical)
        include_args: 是否包含函数参数
        include_result: 是否包含函数返回值
        exclude_args: 要排除的参数名列表
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = f"{func.__module__}.{func.__qualname__}"

            # 准备日志数据
            log_data = {"function": func_name, "start_time": start_time}

            # 包含参数信息
            if include_args:
                exclude_list = exclude_args or []
                filtered_kwargs = {
                    k: v for k, v in kwargs.items() if k not in exclude_list
                }
                log_data["args"] = args
                log_data["kwargs"] = filtered_kwargs

            # 记录函数开始执行
            log_method = getattr(RequestLogger, level.lower(), RequestLogger.info)
            log_method(f"Function call started: {func_name}", **log_data)

            try:
                # 执行函数
                result = func(*args, **kwargs)

                # 计算执行时间
                duration = time.time() - start_time
                log_data["duration"] = duration
                log_data["status"] = "success"

                # 包含返回值
                if include_result:
                    log_data["result"] = result

                # 记录函数执行成功
                log_method(
                    f"Function call completed: {func_name} - Duration: {duration:.3f}s",
                    **log_data,
                )

                return result

            except Exception as e:
                # 计算执行时间
                duration = time.time() - start_time
                log_data["duration"] = duration
                log_data["status"] = "error"
                log_data["exception_type"] = type(e).__name__
                log_data["exception_message"] = str(e)

                # 记录函数执行失败
                RequestLogger.error(
                    f"Function call failed: {func_name} - {type(e).__name__}: {str(e)}",
                    **log_data,
                )

                # 重新抛出异常
                raise

        return wrapper

    return decorator


def log_database_query(query_type: str = "unknown"):
    """
    数据库查询日志装饰器

    Args:
        query_type: 查询类型 (select, insert, update, delete, etc.)
    """
    return decorator


@contextmanager
def log_operation(operation_name: str, level: str = "info", **context_data):
    """
    操作日志上下文管理器

    Args:
        operation_name: 操作名称
        level: 日志级别
        **context_data: 额外的上下文数据
    """
    start_time = time.time()
    log_method = getattr(RequestLogger, level.lower(), RequestLogger.info)

    # 记录操作开始
    log_method(
        f"Operation started: {operation_name}",
        operation=operation_name,
        start_time=start_time,
        **context_data,
    )

    try:
        yield

        # 记录操作成功
        duration = time.time() - start_time
        log_method(
            f"Operation completed: {operation_name} - Duration: {duration:.3f}s",
            operation=operation_name,
            duration=duration,
            status="success",
            **context_data,
        )

    except Exception as e:
        # 记录操作失败
        duration = time.time() - start_time
        RequestLogger.error(
            f"Operation failed: {operation_name} - {type(e).__name__}: {str(e)}",
            operation=operation_name,
            duration=duration,
            status="error",
            exception_type=type(e).__name__,
            exception_message=str(e),
            **context_data,
        )
        raise


def log_api_call(
    api_name: str,
    include_request_data: bool = False,
    include_response_data: bool = False,
    exclude_fields: Optional[list] = None,
):
    """
    API调用日志装饰器

    Args:
        api_name: API名称
        include_request_data: 是否包含请求数据
        include_response_data: 是否包含响应数据
        exclude_fields: 要排除的字段列表
    """
    return decorator


class AuditLogger:
    """
    审计日志记录器

    用于记录重要的业务操作和安全事件。
    """

    @staticmethod
    def log_user_action(
        action: str,
        resource: str,
        resource_id: Optional[Union[str, int]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """记录用户操作"""
        log_data = {
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "details": details or {},
        }

        RequestLogger.info(f"User action: {action} on {resource}", **log_data)

    @staticmethod
    def log_security_event(
        event_type: str,
        severity: str = "warning",
        details: Optional[Dict[str, Any]] = None,
    ):
        """记录安全事件"""
        log_data = {
            "event_type": event_type,
            "severity": severity,
            "details": details or {},
        }

        log_method = getattr(RequestLogger, severity.lower(), RequestLogger.warning)
        log_method(f"Security event: {event_type}", **log_data)

    @staticmethod
    def log_data_change(
        table: str,
        operation: str,
        record_id: Optional[Union[str, int]] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
    ):
        """记录数据变更"""
        log_data = {
            "table": table,
            "operation": operation,
            "record_id": record_id,
            "old_values": old_values or {},
            "new_values": new_values or {},
        }

        RequestLogger.info(f"Data change: {operation} on {table}", **log_data)


# 便捷的全局日志记录器实例
request_logger = RequestLogger()
audit_logger = AuditLogger()
