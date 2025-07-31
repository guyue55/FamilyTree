"""
分页工具模块

该文件提供分页相关的工具函数。
遵循Django最佳实践和Google Python Style Guide。
"""

from typing import Any, Dict, List, Optional, Callable
from django.core.paginator import Paginator
from django.db.models import QuerySet
from math import ceil

def paginate_queryset(
    queryset: QuerySet,
    page: int = 1,
    page_size: int = 20,
    serializer: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    分页查询集

    Args:
        queryset: Django查询集
        page: 页码
        page_size: 每页大小
        serializer: 序列化函数

    Returns:
        Dict[str, Any]: 分页结果
    """
    # 限制页面大小
    page_size = min(page_size, 100)

    # 创建分页器
    paginator = Paginator(queryset, page_size)

    # 获取页面
    try:
        page_obj = paginator.page(page)
    except:
        # 页码无效时返回第一页
        page_obj = paginator.page(1)
        page = 1

    # 序列化数据
    items = list(page_obj.object_list)
    if serializer:
        items = [serializer(item) for item in items]

    return {
        'items': items,
        'total': paginator.count,
        'page': page,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_prev': page_obj.has_previous()
    }

def paginate_list(
    data_list: List[Any],
    page: int = 1,
    page_size: int = 20,
    serializer: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    分页列表

    Args:
        data_list: 数据列表
        page: 页码
        page_size: 每页大小
        serializer: 序列化函数

    Returns:
        Dict[str, Any]: 分页结果
    """
    # 限制页面大小
    page_size = min(page_size, 100)

    total = len(data_list)
    total_pages = ceil(total / page_size) if total > 0 else 1

    # 确保页码有效
    page = max(1, min(page, total_pages))

    # 计算切片范围
    start = (page - 1) * page_size
    end = start + page_size

    # 获取当前页数据
    items = data_list[start:end]
    if serializer:
        items = [serializer(item) for item in items]

    return {
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1
    }

__all__ = [
    'paginate_queryset',
    'paginate_list',
]