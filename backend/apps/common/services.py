"""
公共服务层

该文件定义了系统中使用的公共服务类。
遵循Django最佳实践和Google Python Style Guide。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Callable, Union
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import models, transaction
from django.db.models import QuerySet, Q
from loguru import logger
from .exceptions import raise_if_not_found

User = get_user_model()
ModelType = TypeVar("ModelType", bound=models.Model)


# 缓存超时时间常量
class CacheTimeout:
    """缓存超时时间常量"""

    SHORT = 300  # 5分钟
    MEDIUM = 1800  # 30分钟
    LONG = 3600  # 1小时


class BaseService(Generic[ModelType], ABC):
    """
    通用业务服务基类

    提供标准化的CRUD操作模式，适用于Django Ninja API服务。
    所有业务服务类都应继承此基类。
    """

    model: Type[ModelType] = None

    @classmethod
    def get_model(cls) -> Type[ModelType]:
        """
        获取模型类

        Returns:
            Type[ModelType]: 模型类

        Raises:
            NotImplementedError: 未设置model属性
        """
        if cls.model is None:
            raise NotImplementedError("必须设置model属性")
        return cls.model

    @classmethod
    def get_by_id(
        cls, obj_id: int, user: Optional[User] = None, check_permission: bool = True
    ) -> ModelType:
        """
        根据ID获取对象

        Args:
            obj_id: 对象ID
            user: 当前用户（可选）
            check_permission: 是否检查权限

        Returns:
            ModelType: 对象实例

        Raises:
            NotFoundError: 对象不存在
            PermissionError: 权限不足
        """
        try:
            obj = cls.get_model().objects.get(id=obj_id)

            if check_permission and user:
                cls.check_read_permission(obj, user)

            return obj
        except cls.get_model().DoesNotExist:
            raise_if_not_found(None, cls.get_model()._meta.verbose_name, obj_id)

    @classmethod
    def get_queryset(cls, user: Optional[User] = None) -> QuerySet[ModelType]:
        """
        获取基础查询集

        Args:
            user: 当前用户（可选）

        Returns:
            QuerySet: 查询集
        """
        queryset = cls.get_model().objects.all()

        if user:
            queryset = cls.filter_by_permission(queryset, user)

        return queryset

    @classmethod
    def search_objects(
        cls, query: str, user: Optional[User] = None
    ) -> QuerySet[ModelType]:
        """
        搜索对象

        Args:
            query: 搜索关键词
            user: 当前用户（可选）

        Returns:
            QuerySet: 搜索结果查询集
        """
        queryset = cls.get_queryset(user)

        if not query:
            return queryset

        search_fields = cls.get_search_fields()
        if not search_fields:
            return queryset

        # 构建搜索条件
        search_q = Q()
        for field in search_fields:
            search_q |= Q(**{f"{field}__icontains": query})

        return queryset.filter(search_q)

    @classmethod
    @transaction.atomic
    def create_object(cls, data: Dict[str, Any], user: User) -> ModelType:
        """
        创建对象

        Args:
            data: 创建数据
            user: 当前用户

        Returns:
            ModelType: 创建的对象

        Raises:
            PermissionError: 权限不足
            ValidationError: 数据验证失败
        """
        # 检查创建权限
        cls.check_create_permission(user)

        # 检查创建限制
        cls.check_create_limits(user, data)

        # 验证数据
        validated_data = cls.validate_create_data(data, user)

        # 创建对象
        obj = cls.get_model().objects.create(**validated_data)

        # 后处理
        cls.post_create(obj, user, data)

        # 清除相关缓存
        cls.clear_related_cache(obj)

        logger.info(f"Created {cls.get_model()._meta.verbose_name}: {obj.id}")

        return obj

    @classmethod
    @transaction.atomic
    def update_object(cls, obj_id: int, data: Dict[str, Any], user: User) -> ModelType:
        """
        更新对象

        Args:
            obj_id: 对象ID
            data: 更新数据
            user: 当前用户

        Returns:
            ModelType: 更新后的对象

        Raises:
            NotFoundError: 对象不存在
            PermissionError: 权限不足
            ValidationError: 数据验证失败
        """
        obj = cls.get_by_id(obj_id, user, check_permission=False)

        # 检查更新权限
        cls.check_update_permission(obj, user)

        # 验证数据
        validated_data = cls.validate_update_data(data, obj, user)

        # 更新对象
        for field, value in validated_data.items():
            setattr(obj, field, value)
        obj.save()

        # 后处理
        cls.post_update(obj, user, data)

        # 清除相关缓存
        cls.clear_related_cache(obj)

        logger.info(f"Updated {cls.get_model()._meta.verbose_name}: {obj.id}")

        return obj

    @classmethod
    @transaction.atomic
    def delete_object(cls, obj_id: int, user: User) -> None:
        """
        删除对象

        Args:
            obj_id: 对象ID
            user: 当前用户

        Raises:
            NotFoundError: 对象不存在
            PermissionError: 权限不足
        """
        obj = cls.get_by_id(obj_id, user, check_permission=False)

        # 检查删除权限
        cls.check_delete_permission(obj, user)

        # 前处理
        cls.pre_delete(obj, user)

        # 删除对象
        obj.delete()

        # 清除相关缓存
        cls.clear_related_cache(obj)

        logger.info(f"Deleted {cls.get_model()._meta.verbose_name}: {obj_id}")

    # 抽象方法 - 子类必须实现

    @classmethod
    @abstractmethod
    def get_search_fields(cls) -> List[str]:
        """
        获取搜索字段列表

        Returns:
            List[str]: 搜索字段列表
        """
        pass

    @classmethod
    @abstractmethod
    def validate_create_data(cls, data: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        验证创建数据

        Args:
            data: 原始数据
            user: 当前用户

        Returns:
            Dict[str, Any]: 验证后的数据

        Raises:
            ValidationError: 数据验证失败
        """
        pass

    @classmethod
    @abstractmethod
    def validate_update_data(
        cls, data: Dict[str, Any], obj: ModelType, user: User
    ) -> Dict[str, Any]:
        """
        验证更新数据

        Args:
            data: 原始数据
            obj: 要更新的对象
            user: 当前用户

        Returns:
            Dict[str, Any]: 验证后的数据

        Raises:
            ValidationError: 数据验证失败
        """
        pass

    # 权限检查方法 - 子类可重写

    @classmethod
    def filter_by_permission(
        cls, queryset: QuerySet[ModelType], user: User
    ) -> QuerySet[ModelType]:
        """
        根据权限过滤查询集

        Args:
            queryset: 原始查询集
            user: 当前用户

        Returns:
            QuerySet[ModelType]: 过滤后的查询集
        """
        return queryset

    @classmethod
    def check_read_permission(cls, obj: ModelType, user: User) -> None:
        """
        检查读取权限

        Args:
            obj: 对象实例
            user: 当前用户

        Raises:
            PermissionError: 权限不足
        """
        pass

    @classmethod
    def check_create_permission(cls, user: User) -> None:
        """
        检查创建权限

        Args:
            user: 当前用户

        Raises:
            PermissionError: 权限不足
        """
        if not user.is_authenticated:
            raise PermissionError("需要登录才能创建")

    @classmethod
    def check_update_permission(cls, obj: ModelType, user: User) -> None:
        """
        检查更新权限

        Args:
            obj: 对象实例
            user: 当前用户

        Raises:
            PermissionError: 权限不足
        """
        if not user.is_authenticated:
            raise PermissionError("需要登录才能更新")

    @classmethod
    def check_delete_permission(cls, obj: ModelType, user: User) -> None:
        """
        检查删除权限

        Args:
            obj: 对象实例
            user: 当前用户

        Raises:
            PermissionError: 权限不足
        """
        if not user.is_authenticated:
            raise PermissionError("需要登录才能删除")

    # 限制检查方法 - 子类可重写

    @classmethod
    def check_create_limits(cls, user: User, data: Dict[str, Any]) -> None:
        """
        检查创建限制

        Args:
            user: 当前用户
            data: 创建数据

        Raises:
            ValidationError: 超出限制
        """
        pass

    # 钩子方法 - 子类可重写

    @classmethod
    def post_create(cls, obj: ModelType, user: User, data: Dict[str, Any]) -> None:
        """
        创建后处理

        Args:
            obj: 创建的对象
            user: 当前用户
            data: 原始数据
        """
        pass

    @classmethod
    def post_update(cls, obj: ModelType, user: User, data: Dict[str, Any]) -> None:
        """
        更新后处理

        Args:
            obj: 更新的对象
            user: 当前用户
            data: 原始数据
        """
        pass

    @classmethod
    def pre_delete(cls, obj: ModelType, user: User) -> None:
        """
        删除前处理

        Args:
            obj: 要删除的对象
            user: 当前用户
        """
        pass

    # 缓存管理方法

    @classmethod
    def get_cache_key(cls, prefix: str, *args) -> str:
        """
        生成缓存键

        Args:
            prefix: 缓存前缀
            *args: 缓存键参数

        Returns:
            str: 缓存键
        """
        model_name = cls.get_model()._meta.label_lower.replace(".", "_")
        return f"{model_name}_{prefix}_{'_'.join(map(str, args))}"

    @classmethod
    def clear_related_cache(cls, obj: ModelType) -> None:
        """
        清除相关缓存

        Args:
            obj: 对象实例
        """
        # 清除详情缓存
        cache_key = cls.get_cache_key("detail", obj.id)
        cache.delete(cache_key)

        # 清除列表缓存
        cls.clear_list_cache()

    @classmethod
    def clear_list_cache(cls) -> None:
        """清除列表缓存"""
        # 子类可重写以实现特定的缓存清理逻辑
        pass


class CacheableService:
    """
    可缓存服务混入类

    提供通用的缓存操作方法，适用于需要缓存的服务类。
    """

    @classmethod
    def get_cached_data(
        cls, cache_key: str, fetch_func: Callable, timeout: int = CacheTimeout.MEDIUM
    ) -> Any:
        """
        获取缓存数据

        Args:
            cache_key: 缓存键
            fetch_func: 数据获取函数
            timeout: 缓存超时时间（秒）

        Returns:
            Any: 缓存的数据
        """
        data = cache.get(cache_key)
        if data is None:
            data = fetch_func()
            if data is not None:
                cache.set(cache_key, data, timeout)
        return data

    @classmethod
    def get_from_cache(cls, cache_key: str) -> Any:
        """
        从缓存获取数据

        Args:
            cache_key: 缓存键

        Returns:
            Any: 缓存的数据，如果不存在则返回None
        """
        return cache.get(cache_key)

    @classmethod
    def set_cache(cls, cache_key: str, data: Any, timeout: int = None) -> None:
        """
        设置缓存数据

        Args:
            cache_key: 缓存键
            data: 要缓存的数据
            timeout: 缓存超时时间（秒），如果为None则使用默认超时时间
        """
        if timeout is None:
            timeout = getattr(cls, "cache_timeout", CacheTimeout.MEDIUM)
        cache.set(cache_key, data, timeout)

    @classmethod
    def clear_cache(cls, cache_key: str) -> None:
        """
        清除指定缓存

        Args:
            cache_key: 缓存键
        """
        cache.delete(cache_key)

    @classmethod
    def clear_cache_pattern(cls, pattern: str) -> None:
        """
        清除匹配模式的缓存

        Args:
            pattern: 缓存键模式
        """
        try:
            cache.delete_pattern(pattern)
        except AttributeError:
            # 如果缓存后端不支持模式删除，则忽略
            logger.warning(
                f"Cache backend does not support pattern deletion: {pattern}"
            )

    @classmethod
    def invalidate_cache(cls, cache_key: str) -> None:
        """
        使缓存失效

        Args:
            cache_key: 缓存键
        """
        cache.delete(cache_key)

    @classmethod
    def invalidate_cache_pattern(cls, pattern: str) -> None:
        """
        使匹配模式的缓存失效

        Args:
            pattern: 缓存键模式

        Note:
            需要Redis后端支持pattern删除功能
        """
        try:
            cache.delete_pattern(pattern)
        except AttributeError:
            # 如果缓存后端不支持模式删除，则忽略
            logger.warning(
                f"Cache backend does not support pattern deletion: {pattern}"
            )


class SimpleService:
    """
    简单服务基类

    提供基础的工具方法，适用于不需要完整CRUD操作的服务类。
    """

    @staticmethod
    @staticmethod
    def clear_cache_pattern(pattern: str) -> None:
        """
        清除匹配模式的缓存

        Args:
            pattern: 缓存键模式
        """
        try:
            cache.delete_pattern(pattern)
        except AttributeError:
            # 如果缓存后端不支持模式删除，则忽略
            logger.warning(
                f"Cache backend does not support pattern deletion: {pattern}"
            )


__all__ = [
    "BaseService",
    "CacheableService",
    "SimpleService",
    "CacheTimeout",
    "ModelType",
]
