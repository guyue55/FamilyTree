from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar, Generic
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.db import models
from ninja import Router
from .services import BaseService
from .exceptions import BaseApplicationException
from .utils.logging import RequestLogger
from .schemas import (
    SuccessResponseSchema,
    PaginatedApiResponseSchema, 
    BaseQuerySchema
)
from . import utils as common_utils

"""
公共模块API基类

提供通用的API接口基类和装饰器。
遵循Django Ninja最佳实践和Google Python Style Guide。
"""

User = get_user_model()
ServiceType = TypeVar('ServiceType', bound=BaseService)
ModelType = TypeVar('ModelType', bound=models.Model)

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

        RequestLogger.info("处理列表请求",
                          user_id=getattr(user, 'id', None),
                          service_name=service.__name__,
                          query_params=query.dict(exclude_unset=True))

        result = service.list_objects(
            user=user,
            search=query.search,
            ordering=query.ordering,
            page=query.page,
            page_size=query.page_size
        )

        RequestLogger.info("列表查询完成",
                          user_id=getattr(user, 'id', None),
                          total_count=result['total'],
                          page=result['page'],
                          page_size=result['page_size'])

        return common_utils.create_paginated_response(
            data=result['items'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size'],
            request_id=common_utils.get_request_id(request)
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

        RequestLogger.info("处理详情请求",
                          user_id=getattr(user, 'id', None),
                          service_name=service.__name__,
                          object_id=obj_id)

        obj = service.get_by_id(obj_id, user)
        data = self.serialize_object(obj, user)

        RequestLogger.info("详情查询完成",
                          user_id=getattr(user, 'id', None),
                          object_id=obj_id)

        return common_utils.create_success_response(
            data=data,
            message="获取成功",
            request_id=common_utils.get_request_id(request)
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

        RequestLogger.info("处理创建请求",
                          user_id=getattr(user, 'id', None),
                          service_name=service.__name__)

        obj = service.create_object(user, data)
        response_data = self.serialize_object(obj, user)

        RequestLogger.info("对象创建完成",
                          user_id=getattr(user, 'id', None),
                          object_id=getattr(obj, 'id', None))

        return common_utils.create_success_response(
            data=response_data,
            message="创建成功",
            request_id=common_utils.get_request_id(request)
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

        RequestLogger.info("处理更新请求",
                          user_id=getattr(user, 'id', None),
                          service_name=service.__name__,
                          object_id=obj_id)

        obj = service.update_object(obj_id, user, data)
        response_data = self.serialize_object(obj, user)

        RequestLogger.info("对象更新完成",
                          user_id=getattr(user, 'id', None),
                          object_id=obj_id)

        return common_utils.create_success_response(
            data=response_data,
            message="更新成功",
            request_id=common_utils.get_request_id(request)
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

        RequestLogger.info("处理删除请求",
                          user_id=getattr(user, 'id', None),
                          service_name=service.__name__,
                          object_id=obj_id)

        service.delete_object(obj_id, user)

        RequestLogger.info("对象删除完成",
                          user_id=getattr(user, 'id', None),
                          object_id=obj_id)

        return common_utils.create_success_response(
            data=None,
            message="删除成功",
            request_id=common_utils.get_request_id(request)
        )

    @abstractmethod
    def serialize_object(self, obj: ModelType, user: Optional[User] = None) -> Dict[str, Any]:
        """
        序列化对象 - 子类必须实现

        Args:
            obj: 要序列化的对象
            user: 当前用户

        Returns:
            Dict[str, Any]: 序列化后的数据
        """
        pass

class StandardCRUDController(BaseAPIController[ServiceType]):
    """
    标准CRUD控制器

    提供标准的增删改查操作。
    """

# 装饰器
def api_exception_handler(func):
    """API异常处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseApplicationException as e:
            RequestLogger.error(f"业务异常: {e.message}",
                              error_code=e.error_code,
                              details=e.details)
            return common_utils.create_error_response(
                message=e.message,
                error_code=e.error_code,
                details=e.details
            )
        except Exception as e:
            RequestLogger.error(f"系统异常: {str(e)}")
            return common_utils.create_error_response(
                message="系统内部错误",
                error_code="INTERNAL_ERROR"
            )
    return wrapper

def require_authentication(func):
    """认证装饰器"""
    return wrapper

def log_api_request(func):
    """API请求日志装饰器"""
    return wrapper