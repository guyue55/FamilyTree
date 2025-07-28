"""
通用分页工具

提供统一的分页功能，支持Django QuerySet和自定义数据源。
"""

from typing import Any, Dict, List, Optional, Callable
from math import ceil
from django.db.models import QuerySet
from django.core.paginator import Paginator
from pydantic import BaseModel, Field

from .utils import create_paginated_response


class PaginationResult(BaseModel):
    """分页结果"""
    items: List[Any] = Field([], description="数据项")
    total: int = Field(0, description="总数量")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(20, description="每页大小")
    total_pages: int = Field(0, description="总页数")
    has_next: bool = Field(False, description="是否有下一页")
    has_prev: bool = Field(False, description="是否有上一页")
    
    @classmethod
    def from_queryset(
        cls,
        queryset: QuerySet,
        page: int = 1,
        page_size: int = 20,
        serializer: Optional[Callable] = None
    ) -> 'PaginationResult':
        """从QuerySet创建分页结果"""
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
        
        return cls(
            items=items,
            total=paginator.count,
            page=page,
            page_size=page_size,
            total_pages=paginator.num_pages,
            has_next=page_obj.has_next(),
            has_prev=page_obj.has_previous()
        )
    
    @classmethod
    def from_list(
        cls,
        data_list: List[Any],
        page: int = 1,
        page_size: int = 20,
        serializer: Optional[Callable] = None
    ) -> 'PaginationResult':
        """从列表创建分页结果"""
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
        
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    
    def to_api_response(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        """转换为API响应格式"""
        return create_paginated_response(
            data=self.items,
            total=self.total,
            page=self.page,
            page_size=self.page_size,
            request_id=request_id
        )


class SearchConfig(BaseModel):
    """搜索配置"""
    query: Optional[str] = Field(None, description="搜索关键词")
    fields: List[str] = Field([], description="搜索字段")
    exact_match: bool = Field(False, description="是否精确匹配")
    case_sensitive: bool = Field(False, description="是否区分大小写")


class OrderConfig(BaseModel):
    """排序配置"""
    field: str = Field(..., description="排序字段")
    direction: str = Field("asc", regex="^(asc|desc)$", description="排序方向")
    
    def to_django_order(self) -> str:
        """转换为Django排序字符串"""
        if self.direction == "desc":
            return f"-{self.field}"
        return self.field


class FilterConfig(BaseModel):
    """过滤配置"""
    field: str = Field(..., description="过滤字段")
    operator: str = Field("eq", description="操作符")
    value: Any = Field(..., description="过滤值")
    
    def to_django_filter(self) -> Dict[str, Any]:
        """转换为Django过滤字典"""
        operator_mapping = {
            "eq": "",
            "ne": "",  # 需要特殊处理
            "gt": "__gt",
            "gte": "__gte",
            "lt": "__lt",
            "lte": "__lte",
            "in": "__in",
            "contains": "__icontains",
            "startswith": "__istartswith",
            "endswith": "__iendswith",
            "isnull": "__isnull",
        }
        
        suffix = operator_mapping.get(self.operator, "")
        filter_key = f"{self.field}{suffix}"
        
        if self.operator == "ne":
            # 不等于需要使用exclude
            return {"exclude": {filter_key: self.value}}
        
        return {filter_key: self.value}


class QueryBuilder:
    """查询构建器"""
    
    def __init__(self, queryset: QuerySet):
        self.queryset = queryset
    
    def search(self, config: SearchConfig) -> 'QueryBuilder':
        """添加搜索条件"""
        if not config.query or not config.fields:
            return self
        
        from django.db.models import Q
        
        query_obj = Q()
        for field in config.fields:
            if config.exact_match:
                if config.case_sensitive:
                    lookup = f"{field}__exact"
                else:
                    lookup = f"{field}__iexact"
            else:
                if config.case_sensitive:
                    lookup = f"{field}__contains"
                else:
                    lookup = f"{field}__icontains"
            
            query_obj |= Q(**{lookup: config.query})
        
        self.queryset = self.queryset.filter(query_obj)
        return self
    
    def filter(self, filters: List[FilterConfig]) -> 'QueryBuilder':
        """添加过滤条件"""
        for filter_config in filters:
            filter_dict = filter_config.to_django_filter()
            
            if "exclude" in filter_dict:
                self.queryset = self.queryset.exclude(**filter_dict["exclude"])
            else:
                self.queryset = self.queryset.filter(**filter_dict)
        
        return self
    
    def order(self, orders: List[OrderConfig]) -> 'QueryBuilder':
        """添加排序条件"""
        if orders:
            order_fields = [order.to_django_order() for order in orders]
            self.queryset = self.queryset.order_by(*order_fields)
        
        return self
    
    def paginate(
        self,
        page: int = 1,
        page_size: int = 20,
        serializer: Optional[Callable] = None
    ) -> PaginationResult:
        """执行分页"""
        return PaginationResult.from_queryset(
            self.queryset,
            page=page,
            page_size=page_size,
            serializer=serializer
        )
    
    def build(self) -> QuerySet:
        """构建最终的QuerySet"""
        return self.queryset


def paginate_queryset(
    queryset: QuerySet,
    page: int = 1,
    page_size: int = 20,
    serializer: Optional[Callable] = None
) -> PaginationResult:
    """便捷函数：分页QuerySet"""
    return PaginationResult.from_queryset(queryset, page, page_size, serializer)


def paginate_list(
    data_list: List[Any],
    page: int = 1,
    page_size: int = 20,
    serializer: Optional[Callable] = None
) -> PaginationResult:
    """便捷函数：分页列表"""
    return PaginationResult.from_list(data_list, page, page_size, serializer)


def search_and_paginate(
    queryset: QuerySet,
    search_query: Optional[str] = None,
    search_fields: Optional[List[str]] = None,
    filters: Optional[List[FilterConfig]] = None,
    orders: Optional[List[OrderConfig]] = None,
    page: int = 1,
    page_size: int = 20,
    serializer: Optional[Callable] = None
) -> PaginationResult:
    """便捷函数：搜索、过滤、排序和分页"""
    builder = QueryBuilder(queryset)
    
    # 添加搜索
    if search_query and search_fields:
        search_config = SearchConfig(query=search_query, fields=search_fields)
        builder.search(search_config)
    
    # 添加过滤
    if filters:
        builder.filter(filters)
    
    # 添加排序
    if orders:
        builder.order(orders)
    
    # 执行分页
    return builder.paginate(page, page_size, serializer)


__all__ = [
    'PaginationResult',
    'SearchConfig',
    'OrderConfig',
    'FilterConfig',
    'QueryBuilder',
    'paginate_queryset',
    'paginate_list',
    'search_and_paginate',
]