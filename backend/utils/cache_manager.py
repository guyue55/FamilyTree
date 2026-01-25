"""
缓存管理工具类

提供缓存操作相关功能。
遵循Django最佳实践和Google Python Style Guide。
"""

import json
import hashlib
from typing import Any, Optional, Union, List, Dict
from django.core.cache import cache
from django.conf import settings


class CacheManager:
    """缓存管理器"""

    # 默认缓存时间（秒）
    DEFAULT_TIMEOUT = 3600  # 1小时

    @staticmethod
    def generate_cache_key(*args, prefix: str = "", **kwargs) -> str:
        """
        生成缓存键

        Args:
            *args: 位置参数
            prefix: 键前缀
            **kwargs: 关键字参数

        Returns:
            str: 缓存键
        """
        # 构建键的组成部分
        key_parts = []

        if prefix:
            key_parts.append(prefix)

        # 添加位置参数
        for arg in args:
            if isinstance(arg, (dict, list)):
                key_parts.append(json.dumps(arg, sort_keys=True))
            else:
                key_parts.append(str(arg))

        # 添加关键字参数
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.append(json.dumps(sorted_kwargs))

        # 生成最终键
        key_string = ":".join(key_parts)

        # 如果键太长，使用哈希
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:{key_hash}" if prefix else key_hash

        return key_string

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        获取缓存值

        Args:
            key: 缓存键
            default: 默认值

        Returns:
            Any: 缓存值
        """
        try:
            return cache.get(key, default)
        except Exception:
            return default

    @staticmethod
    def set(key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            timeout: 过期时间（秒）

        Returns:
            bool: 是否成功
        """
        if timeout is None:
            timeout = CacheManager.DEFAULT_TIMEOUT

        try:
            cache.set(key, value, timeout)
            return True
        except Exception:
            return False

    @staticmethod
    def delete(key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            bool: 是否成功
        """
        try:
            cache.delete(key)
            return True
        except Exception:
            return False

    @staticmethod
    def delete_pattern(pattern: str) -> int:
        """
        删除匹配模式的缓存

        Args:
            pattern: 模式字符串

        Returns:
            int: 删除的数量
        """
        try:
            if hasattr(cache, "delete_pattern"):
                return cache.delete_pattern(pattern)
            else:
                # 如果缓存后端不支持模式删除，返回0
                return 0
        except Exception:
            return 0

    @staticmethod
    def get_or_set(
        key: str, callable_func, timeout: Optional[int] = None, *args, **kwargs
    ) -> Any:
        """
        获取缓存值，如果不存在则设置

        Args:
            key: 缓存键
            callable_func: 可调用函数
            timeout: 过期时间
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            Any: 缓存值
        """
        if timeout is None:
            timeout = CacheManager.DEFAULT_TIMEOUT

        try:
            return cache.get_or_set(
                key, lambda: callable_func(*args, **kwargs), timeout
            )
        except Exception:
            # 如果缓存失败，直接调用函数
            return callable_func(*args, **kwargs)

    @staticmethod
    def increment(key: str, delta: int = 1) -> Optional[int]:
        """
        增加缓存值

        Args:
            key: 缓存键
            delta: 增量

        Returns:
            Optional[int]: 新值
        """
        try:
            return cache.incr(key, delta)
        except Exception:
            return None

    @staticmethod
    def decrement(key: str, delta: int = 1) -> Optional[int]:
        """
        减少缓存值

        Args:
            key: 缓存键
            delta: 减量

        Returns:
            Optional[int]: 新值
        """
        try:
            return cache.decr(key, delta)
        except Exception:
            return None

    @staticmethod
    def get_many(keys: List[str]) -> Dict[str, Any]:
        """
        批量获取缓存值

        Args:
            keys: 缓存键列表

        Returns:
            Dict[str, Any]: 键值对字典
        """
        try:
            return cache.get_many(keys)
        except Exception:
            return {}

    @staticmethod
    def set_many(data: Dict[str, Any], timeout: Optional[int] = None) -> bool:
        """
        批量设置缓存值

        Args:
            data: 键值对字典
            timeout: 过期时间

        Returns:
            bool: 是否成功
        """
        if timeout is None:
            timeout = CacheManager.DEFAULT_TIMEOUT

        try:
            cache.set_many(data, timeout)
            return True
        except Exception:
            return False

    @staticmethod
    def clear() -> bool:
        """
        清空所有缓存

        Returns:
            bool: 是否成功
        """
        try:
            cache.clear()
            return True
        except Exception:
            return False

    @staticmethod
    def touch(key: str, timeout: Optional[int] = None) -> bool:
        """
        更新缓存过期时间

        Args:
            key: 缓存键
            timeout: 新的过期时间

        Returns:
            bool: 是否成功
        """
        if timeout is None:
            timeout = CacheManager.DEFAULT_TIMEOUT

        try:
            return cache.touch(key, timeout)
        except Exception:
            return False


class CacheKeyBuilder:
    """缓存键构建器"""

    @staticmethod
    def user_cache_key(user_id: int, action: str = "") -> str:
        """构建用户缓存键"""
        return CacheManager.generate_cache_key("user", user_id, action, prefix="cache")

    @staticmethod
    def model_cache_key(model_name: str, instance_id: int, action: str = "") -> str:
        """构建模型缓存键"""
        return CacheManager.generate_cache_key(
            model_name, instance_id, action, prefix="model"
        )

    @staticmethod
    def query_cache_key(model_name: str, filters: Dict[str, Any]) -> str:
        """构建查询缓存键"""
        return CacheManager.generate_cache_key(
            "query", model_name, filters, prefix="query"
        )

    @staticmethod
    def api_cache_key(endpoint: str, params: Dict[str, Any]) -> str:
        """构建API缓存键"""
        return CacheManager.generate_cache_key("api", endpoint, params, prefix="api")

    @staticmethod
    def session_cache_key(session_id: str, key: str) -> str:
        """构建会话缓存键"""
        return CacheManager.generate_cache_key(
            "session", session_id, key, prefix="session"
        )
