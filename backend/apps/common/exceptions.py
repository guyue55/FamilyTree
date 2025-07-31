"""
公共异常类定义

该文件定义了系统中使用的所有自定义异常类。
遵循Django最佳实践和Google Python Style Guide。
"""

from typing import Dict, Any
from django.core.exceptions import ValidationError as DjangoValidationError, PermissionDenied
from django.http import Http404

class BaseApplicationException(Exception):
    """应用基础异常类"""

    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error': self.message,
            'code': self.code,
            'details': self.details,
        }

class ValidationError(BaseApplicationException):
    """数据验证异常"""

class PermissionError(BaseApplicationException):
    """权限异常"""

class AuthenticationError(BaseApplicationException):
    """认证异常"""

class NotFoundError(BaseApplicationException):
    """资源不存在异常"""

class LimitExceededError(BaseApplicationException):
    """限制超出异常"""

class StatusError(BaseApplicationException):
    """状态异常"""

class ConfigurationError(BaseApplicationException):
    """配置异常"""

class OperationError(BaseApplicationException):
    """操作异常"""

class DataError(BaseApplicationException):
    """数据异常"""

class ServiceUnavailableError(BaseApplicationException):
    """服务不可用异常"""

class RateLimitError(BaseApplicationException):
    """限流异常"""

class MaintenanceError(BaseApplicationException):
    """维护模式异常"""

# 异常处理工具函数
def handle_exception(exception: Exception) -> Dict[str, Any]:
    """
    处理异常，返回标准化的错误响应

    Args:
        exception: 异常对象

    Returns:
        标准化的错误响应字典
    """
    if isinstance(exception, BaseApplicationException):
        return exception.to_dict()

    # 处理Django内置异常

    if isinstance(exception, DjangoValidationError):
        return {
            'error': '数据验证失败',
            'code': 'VALIDATION_ERROR',
            'details': {'messages': exception.messages if hasattr(exception, 'messages') else [str(exception)]},
        }

    if isinstance(exception, PermissionDenied):
        return {
            'error': '权限不足',
            'code': 'PERMISSION_DENIED',
            'details': {},
        }

    if isinstance(exception, Http404):
        return {
            'error': '资源不存在',
            'code': 'NOT_FOUND',
            'details': {},
        }

    # 其他异常
    return {
        'error': '服务器内部错误',
        'code': 'INTERNAL_ERROR',
        'details': {'message': str(exception)},
    }

def raise_if_not_found(resource, resource_type: str = None, resource_id: Any = None):
    """
    如果资源不存在则抛出异常

    Args:
        resource: 资源对象
        resource_type: 资源类型
        resource_id: 资源ID
    """
    if not resource:
        message = f'{resource_type}不存在' if resource_type else '资源不存在'
        raise NotFoundError(message, resource_type, resource_id)

def raise_if_permission_denied(has_permission: bool, required_permission: str,
                              user_role: str = None):
    """
    如果权限不足则抛出异常

    Args:
        has_permission: 是否有权限
        required_permission: 所需权限
        user_role: 用户角色
    """
    if not has_permission:
        raise PermissionError(
            f'需要 {required_permission} 权限',
            required_permission,
            user_role
        )

def raise_if_limit_exceeded(current_value: int, max_value: int,
                           limit_type: str):
    """
    如果超出限制则抛出异常

    Args:
        current_value: 当前值
        max_value: 最大值
        limit_type: 限制类型
    """
    if current_value >= max_value:
        raise LimitExceededError(
            f'{limit_type}已达上限 ({current_value}/{max_value})',
            limit_type,
            current_value,
            max_value
        )

__all__ = [
    'BaseApplicationException',
    'ValidationError',
    'PermissionError',
    'NotFoundError',
    'LimitExceededError',
    'StatusError',
    'ConfigurationError',
    'OperationError',
    'DataError',
    'ServiceUnavailableError',
    'RateLimitError',
    'MaintenanceError',
    'handle_exception',
    'raise_if_not_found',
    'raise_if_permission_denied',
    'raise_if_limit_exceeded',
]