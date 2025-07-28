"""
公共模块工具函数

该模块定义了通用的工具函数，用于API开发中的常见操作。
遵循Django Ninja最佳实践和Google Python Style Guide。
"""

import math
from typing import Any, Dict, List, Optional, TypeVar
from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import HttpRequest

from .constants import PaginationDefaults


T = TypeVar('T')


def create_success_response(
    data: Any = None, 
    message: str = "success", 
    code: int = 200,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        code: 响应状态码
        request_id: 请求ID
        
    Returns:
        Dict: 标准化的成功响应，符合设计文档规范
        
    Example:
        {
            "code": 200,
            "message": "success",
            "data": {...},
            "timestamp": "2025-08-01T12:00:00Z",
            "request_id": "req_123456789"
        }
    """
    return {
        'code': code,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat() + 'Z',
        'request_id': request_id
    }


def create_error_response(
    code: int,
    message: str,
    data: Any = None,
    errors: Optional[List[Dict[str, Any]]] = None,
    request_id: Optional[str] = None
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
        Dict: 标准化的错误响应，符合设计文档规范
        
    Example:
        {
            "code": 400,
            "message": "参数错误",
            "data": null,
            "errors": [
                {
                    "field": "email",
                    "message": "邮箱格式不正确"
                }
            ],
            "timestamp": "2025-08-01T12:00:00Z",
            "request_id": "req_123456789"
        }
    """
    return {
        'code': code,
        'message': message,
        'data': data,
        'errors': errors,
        'timestamp': datetime.now().isoformat() + 'Z',
        'request_id': request_id
    }


def paginate_queryset(
    queryset: QuerySet,
    page: int = PaginationDefaults.DEFAULT_PAGE,
    page_size: int = PaginationDefaults.DEFAULT_PAGE_SIZE
) -> Dict[str, Any]:
    """
    对QuerySet进行分页
    
    Args:
        queryset: Django QuerySet对象
        page: 页码
        page_size: 每页数量
        
    Returns:
        Dict: 包含分页数据和分页信息的字典
    """
    # 限制分页参数
    page = max(1, page)
    page_size = max(
        PaginationDefaults.MIN_PAGE_SIZE,
        min(PaginationDefaults.MAX_PAGE_SIZE, page_size)
    )
    
    paginator = Paginator(queryset, page_size)
    
    # 处理页码超出范围的情况
    if page > paginator.num_pages:
        page = paginator.num_pages if paginator.num_pages > 0 else 1
    
    page_obj = paginator.get_page(page)
    
    return {
        'items': list(page_obj.object_list),
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': paginator.count,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_prev': page_obj.has_previous()
        }
    }


def create_paginated_response(
    data: Any = None,
    total: Optional[int] = None,
    page: int = PaginationDefaults.DEFAULT_PAGE,
    page_size: int = PaginationDefaults.DEFAULT_PAGE_SIZE,
    queryset: Optional[QuerySet] = None,
    serializer_func: Optional[callable] = None,
    message: str = "success",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建分页响应（支持多种数据源）
    
    Args:
        data: 直接传入的数据列表（与queryset二选一）
        total: 总数量（当使用data时必须提供）
        page: 页码
        page_size: 每页数量
        queryset: Django QuerySet对象（与data二选一）
        serializer_func: 序列化函数
        message: 响应消息
        request_id: 请求ID
        
    Returns:
        Dict: 标准化的分页响应，符合设计文档规范
        
    Example:
        {
            "code": 200,
            "message": "success",
            "data": {
                "items": [...],
                "pagination": {
                    "page": 1,
                    "page_size": 20,
                    "total": 100,
                    "total_pages": 5,
                    "has_next": true,
                    "has_prev": false
                }
            },
            "timestamp": "2025-08-01T12:00:00Z",
            "request_id": "req_123456789"
        }
    """
    if queryset is not None:
        # 使用QuerySet分页
        paginated_data = paginate_queryset(queryset, page, page_size)
        
        # 如果提供了序列化函数，则序列化数据
        if serializer_func:
            paginated_data['items'] = [
                serializer_func(item) for item in paginated_data['items']
            ]
    else:
        # 使用直接数据分页
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
        
        # 序列化数据
        if serializer_func and isinstance(items, list):
            items = [serializer_func(item) for item in items]
        
        paginated_data = {
            'items': items,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
    
    return create_success_response(
        data=paginated_data,
        message=message,
        request_id=request_id
    )


def apply_search_filter(queryset: QuerySet, search: str, search_fields: List[str]) -> QuerySet:
    """
    应用搜索过滤
    
    Args:
        queryset: Django QuerySet对象
        search: 搜索关键词
        search_fields: 搜索字段列表
        
    Returns:
        QuerySet: 过滤后的QuerySet
    """
    if not search or not search_fields:
        return queryset
    
    from django.db.models import Q
    
    search_query = Q()
    for field in search_fields:
        search_query |= Q(**{f"{field}__icontains": search})
    
    return queryset.filter(search_query)


def apply_ordering(queryset: QuerySet, ordering: str, allowed_fields: List[str]) -> QuerySet:
    """
    应用排序
    
    Args:
        queryset: Django QuerySet对象
        ordering: 排序字段（支持-前缀表示降序）
        allowed_fields: 允许排序的字段列表
        
    Returns:
        QuerySet: 排序后的QuerySet
    """
    if not ordering:
        return queryset
    
    # 处理降序标识
    desc = ordering.startswith('-')
    field = ordering[1:] if desc else ordering
    
    # 检查字段是否允许排序
    if field not in allowed_fields:
        return queryset
    
    return queryset.order_by(ordering)


def apply_date_filter(
    queryset: QuerySet, 
    field_name: str, 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None
) -> QuerySet:
    """
    应用日期范围过滤
    
    Args:
        queryset: Django QuerySet对象
        field_name: 日期字段名
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        QuerySet: 过滤后的QuerySet
    """
    if start_date:
        queryset = queryset.filter(**{f"{field_name}__gte": start_date})
    
    if end_date:
        queryset = queryset.filter(**{f"{field_name}__lte": end_date})
    
    return queryset


def get_request_id(request: HttpRequest) -> Optional[str]:
    """
    从请求中获取请求ID
    
    Args:
        request: HTTP请求对象
        
    Returns:
        str: 请求ID
    """
    return getattr(request, 'request_id', None)


def validate_file_upload(
    file: Any, 
    allowed_types: List[str], 
    max_size: int
) -> Dict[str, Any]:
    """
    验证文件上传
    
    Args:
        file: 上传的文件对象
        allowed_types: 允许的文件类型列表
        max_size: 最大文件大小（字节）
        
    Returns:
        Dict: 验证结果
    """
    errors = []
    
    # 检查文件类型
    if hasattr(file, 'content_type'):
        if file.content_type not in allowed_types:
            errors.append({
                'field': 'file',
                'message': f'不支持的文件类型: {file.content_type}',
                'code': 'invalid_file_type',
                'value': file.content_type
            })
    
    # 检查文件大小
    if hasattr(file, 'size'):
        if file.size > max_size:
            errors.append({
                'field': 'file',
                'message': f'文件大小超过限制: {file.size} > {max_size}',
                'code': 'file_too_large',
                'value': file.size
            })
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }