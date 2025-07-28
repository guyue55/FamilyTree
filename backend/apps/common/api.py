"""
公共模块API基类

提供通用的API接口基类和装饰器。
遵循Django Ninja最佳实践和Google Python Style Guide。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from ninja import Router

from .schemas import (
    SuccessResponseSchema,
    PaginatedApiResponseSchema, BaseQuerySchema
)
from .services import BaseService, ModelType
from .utils import create_success_response, create_paginated_response, get_request_id
from .exceptions import BaseApplicationException

User = get_user_model()
ServiceType = TypeVar('ServiceType', bound=BaseService)


class BaseAPIController(Generic[ServiceType], ABC):
    """
    通用API控制器基类
    
    提供标准化的API接口模式和通用操作。
    """
    
    service_class: Type[ServiceType] = None
    router: Router = None
    
    def __init__(self):
        if self.router is None:
            self.router = Router()
        self.register_routes()
    
    @classmethod
    def get_service_class(cls) -> Type[ServiceType]:
        """获取服务类"""
        if cls.service_class is None:
            raise NotImplementedError("必须设置service_class属性")
        return cls.service_class
    
    @abstractmethod
    def register_routes(self) -> None:
        """注册路由 - 子类必须实现"""
        pass
    
    def get_current_user(self, request: HttpRequest) -> Optional[User]:
        """获取当前用户"""
        return getattr(request, 'user', None) if hasattr(request, 'user') else None
    
    def handle_list(self, request: HttpRequest, query: BaseQuerySchema) -> PaginatedApiResponseSchema:
        """
        处理列表请求
        
        Args:
            request: HTTP请求
            query: 查询参数
            
        Returns:
            PaginatedApiResponseSchema: 分页响应
        """
        user = self.get_current_user(request)
        service = self.get_service_class()
        
        result = service.list_objects(
            user=user,
            search=query.search,
            ordering=query.ordering,
            page=query.page,
            page_size=query.page_size
        )
        
        return create_paginated_response(
            data=result['items'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size'],
            request_id=get_request_id(request)
        )
    
    def handle_detail(self, request: HttpRequest, obj_id: int) -> SuccessResponseSchema:
        """
        处理详情请求
        
        Args:
            request: HTTP请求
            obj_id: 对象ID
            
        Returns:
            SuccessResponseSchema: 成功响应
        """
        user = self.get_current_user(request)
        service = self.get_service_class()
        
        obj = service.get_by_id(obj_id, user)
        data = self.serialize_object(obj, user)
        
        return create_success_response(
            data=data,
            message="获取成功",
            request_id=get_request_id(request)
        )
    
    def handle_create(self, request: HttpRequest, data: Dict[str, Any]) -> SuccessResponseSchema:
        """
        处理创建请求
        
        Args:
            request: HTTP请求
            data: 创建数据
            
        Returns:
            SuccessResponseSchema: 成功响应
        """
        user = self.get_current_user(request)
        service = self.get_service_class()
        
        obj = service.create_object(user, data)
        response_data = self.serialize_object(obj, user)
        
        return create_success_response(
            data=response_data,
            message="创建成功",
            request_id=get_request_id(request)
        )
    
    def handle_update(self, request: HttpRequest, obj_id: int, 
                     data: Dict[str, Any]) -> SuccessResponseSchema:
        """
        处理更新请求
        
        Args:
            request: HTTP请求
            obj_id: 对象ID
            data: 更新数据
            
        Returns:
            SuccessResponseSchema: 成功响应
        """
        user = self.get_current_user(request)
        service = self.get_service_class()
        
        obj = service.update_object(obj_id, user, data)
        response_data = self.serialize_object(obj, user)
        
        return create_success_response(
            data=response_data,
            message="更新成功",
            request_id=get_request_id(request)
        )
    
    def handle_delete(self, request: HttpRequest, obj_id: int) -> SuccessResponseSchema:
        """
        处理删除请求
        
        Args:
            request: HTTP请求
            obj_id: 对象ID
            
        Returns:
            SuccessResponseSchema: 成功响应
        """
        user = self.get_current_user(request)
        service = self.get_service_class()
        
        service.delete_object(obj_id, user)
        
        return create_success_response(
            message="删除成功",
            request_id=get_request_id(request)
        )
    
    @abstractmethod
    def serialize_object(self, obj: ModelType, user: Optional[User] = None) -> Dict[str, Any]:
        """序列化对象 - 子类必须实现"""
        pass


class StandardCRUDController(BaseAPIController[ServiceType]):
    """
    标准CRUD控制器
    
    提供标准的增删改查API接口。
    """
    
    # 路由配置
    list_route: str = "/"
    detail_route: str = "/{obj_id}"
    create_route: str = "/"
    update_route: str = "/{obj_id}"
    delete_route: str = "/{obj_id}"
    
    # Schema配置
    list_query_schema: Type = BaseQuerySchema
    create_schema: Type = None
    update_schema: Type = None
    
    def register_routes(self) -> None:
        """注册标准CRUD路由"""
        # 列表接口
        @self.router.get(
            self.list_route,
            response=PaginatedApiResponseSchema,
            summary="获取列表",
            tags=[self.get_tag_name()]
        )
        def list_objects(request: HttpRequest, query: self.list_query_schema = None):
            if query is None:
                query = self.list_query_schema()
            return self.handle_list(request, query)
        
        # 详情接口
        @self.router.get(
            self.detail_route,
            response=SuccessResponseSchema,
            summary="获取详情",
            tags=[self.get_tag_name()]
        )
        def get_object(request: HttpRequest, obj_id: int):
            return self.handle_detail(request, obj_id)
        
        # 创建接口
        if self.create_schema:
            @self.router.post(
                self.create_route,
                response=SuccessResponseSchema,
                summary="创建对象",
                tags=[self.get_tag_name()]
            )
            def create_object(request: HttpRequest, data: self.create_schema):
                return self.handle_create(request, data.dict())
        
        # 更新接口
        if self.update_schema:
            @self.router.put(
                self.update_route,
                response=SuccessResponseSchema,
                summary="更新对象",
                tags=[self.get_tag_name()]
            )
            def update_object(request: HttpRequest, obj_id: int, data: self.update_schema):
                return self.handle_update(request, obj_id, data.dict())
        
        # 删除接口
        @self.router.delete(
            self.delete_route,
            response=SuccessResponseSchema,
            summary="删除对象",
            tags=[self.get_tag_name()]
        )
        def delete_object(request: HttpRequest, obj_id: int):
            return self.handle_delete(request, obj_id)
    
    def get_tag_name(self) -> str:
        """获取API标签名称"""
        service_class = self.get_service_class()
        model = service_class.get_model()
        return model._meta.verbose_name_plural or model._meta.label


def api_endpoint(
    methods: List[str] = None,
    response_schema: Type = SuccessResponseSchema,
    summary: str = None,
    description: str = None,
    tags: List[str] = None
):
    """
    API端点装饰器
    
    提供统一的API端点配置和错误处理。
    
    Args:
        methods: HTTP方法列表
        response_schema: 响应Schema
        summary: API摘要
        description: API描述
        tags: API标签
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BaseApplicationException as e:
                # 自定义异常会被全局异常处理器处理
                raise
            except Exception as e:
                # 其他异常也会被全局异常处理器处理
                raise
        
        # 保留原函数的元数据
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__annotations__ = func.__annotations__
        
        # 添加API配置
        wrapper._api_config = {
            'methods': methods or ['GET'],
            'response_schema': response_schema,
            'summary': summary or func.__name__,
            'description': description or func.__doc__,
            'tags': tags or []
        }
        
        return wrapper
    return decorator


def require_permission(permission: str):
    """
    需要权限装饰器
    
    Args:
        permission: 所需权限
    """
    def decorator(func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            user = getattr(request, 'user', None)
            if not user or not user.is_authenticated:
                from .exceptions import PermissionError
                raise PermissionError("需要登录")
            
            if not user.has_perm(permission):
                from .exceptions import PermissionError
                raise PermissionError(f"需要 {permission} 权限")
            
            return func(request, *args, **kwargs)
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__annotations__ = func.__annotations__
        
        return wrapper
    return decorator


__all__ = [
    'BaseAPIController',
    'StandardCRUDController',
    'api_endpoint',
    'require_permission',
]