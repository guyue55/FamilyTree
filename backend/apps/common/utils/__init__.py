from datetime import datetime
from typing import Any, Dict, Optional
from django.http import HttpRequest
import math
from .logging import RequestLogger, log_database_query, log_operation, AuditLogger

"""
公共工具模块

该包提供项目中使用的各种工具函数和类，包括：
- 日志记录工具
- 数据处理工具
- 缓存工具
- 验证工具
等等。

遵循Google Python Style Guide和Django最佳实践。
"""


def create_success_response(
    data: Any = None,
    message: str = "success",
    code: int = 200,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    创建成功响应

    Args:
        data: 响应数据
        message: 响应消息
        code: 响应状态码
        request_id: 请求ID

    Returns:
        Dict: 标准化的成功响应
    """
    return {
        "code": code,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat() + "Z",
        "request_id": request_id,
    }


def create_error_response(
    code: int,
    message: str,
    data: Any = None,
    errors: Optional[list] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    创建错误响应

    Args:
        code: 错误状态码
        message: 错误消息
        data: 错误数据
        errors: 详细错误信息
        request_id: 请求ID

    Returns:
        Dict: 标准化的错误响应
    """
    return {
        "code": code,
        "message": message,
        "data": data,
        "errors": errors,
        "timestamp": datetime.now().isoformat() + "Z",
        "request_id": request_id,
    }


def create_paginated_response(
    data: Any = None,
    total: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    message: str = "success",
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    创建分页响应

    Args:
        data: 数据列表
        total: 总数量
        page: 页码
        page_size: 每页数量
        message: 响应消息
        request_id: 请求ID

    Returns:
        Dict: 标准化的分页响应
    """

    if data is None:
        data = []
    if total is None:
        total = len(data) if isinstance(data, list) else 0

    # 计算分页信息
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    page = max(1, min(page, total_pages))

    # 如果data是列表，进行切片
    if isinstance(data, list):
        start = (page - 1) * page_size
        end = start + page_size
        items = data[start:end]
    else:
        items = data

    paginated_data = {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }

    return create_success_response(
        data=paginated_data, message=message, request_id=request_id
    )


def get_request_id(request: HttpRequest) -> Optional[str]:
    """
    从请求中获取请求ID

    Args:
        request: HTTP请求对象

    Returns:
        str: 请求ID
    """
    return getattr(request, "request_id", None)


__all__ = [
    "RequestLogger",
    "log_database_query",
    "log_operation",
    "AuditLogger",
    "get_request_id",
    "create_success_response",
    "create_error_response",
    "create_paginated_response",
]
