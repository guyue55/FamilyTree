"""
公共模块异常处理器

该模块定义了统一的API异常处理器，用于处理Django Ninja API的异常。
遵循Django Ninja最佳实践和Google Python Style Guide。
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.exceptions import PermissionDenied
from django.http import Http404
from ninja import NinjaAPI
from ninja.errors import ValidationError as NinjaValidationError
from pydantic import ValidationError as PydanticValidationError

from .constants import ApiErrorCode, ApiErrorMessage
from .exceptions import BaseApplicationException
from .schemas import ErrorResponseSchema

logger = logging.getLogger(__name__)


def generate_request_id() -> str:
    """生成请求ID"""
    return str(uuid.uuid4())


def format_validation_errors(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """格式化验证错误"""
    formatted_errors = []
    
    for error in errors:
        if isinstance(error, dict):
            formatted_errors.append({
                'field': error.get('loc', ['unknown'])[-1] if error.get('loc') else 'unknown',
                'message': error.get('msg', 'Validation error'),
                'code': error.get('type', 'validation_error'),
                'value': error.get('input')
            })
        else:
            formatted_errors.append({
                'field': 'unknown',
                'message': str(error),
                'code': 'validation_error',
                'value': None
            })
    
    return formatted_errors


def api_exception_handler(request, exc):
    """
    统一API异常处理器
    
    Args:
        request: HTTP请求对象
        exc: 异常对象
        
    Returns:
        ErrorResponseSchema: 标准化的错误响应
    """
    request_id = getattr(request, 'request_id', None) or generate_request_id()
    timestamp = datetime.now()
    
    # 记录异常信息
    logger.error(
        f"API Exception: {type(exc).__name__}: {str(exc)}, "
        f"Request ID: {request_id}, "
        f"Path: {request.path}, "
        f"Method: {request.method}"
    )
    
    # 处理自定义应用异常
    if isinstance(exc, BaseApplicationException):
        # 获取对应的API错误代码
        api_error_code = _map_exception_to_api_code(exc)
        api_error_message = ApiErrorMessage.get_message(api_error_code)
        
        return ErrorResponseSchema(
            code=api_error_code,
            message=api_error_message,
            data=exc.data,
            errors=exc.errors,
            timestamp=timestamp,
            request_id=request_id
        )
    
    # 处理Django验证错误
    if isinstance(exc, DjangoValidationError):
        errors = _format_django_validation_errors(exc)
        
        return ErrorResponseSchema(
            code=ApiErrorCode.VALIDATION_ERROR,
            message=ApiErrorMessage.get_message(ApiErrorCode.VALIDATION_ERROR),
            errors=errors,
            timestamp=timestamp,
            request_id=request_id
        )
    
    # 处理Ninja/Pydantic验证错误
    if isinstance(exc, (NinjaValidationError, PydanticValidationError)):
        errors = format_validation_errors(exc.errors if hasattr(exc, 'errors') else [])
        
        return ErrorResponseSchema(
            code=ApiErrorCode.VALIDATION_ERROR,
            message=ApiErrorMessage.get_message(ApiErrorCode.VALIDATION_ERROR),
            errors=errors,
            timestamp=timestamp,
            request_id=request_id
        )
    
    # 处理权限拒绝
    if isinstance(exc, PermissionDenied):
        return ErrorResponseSchema(
            code=ApiErrorCode.PERMISSION_DENIED,
            message=ApiErrorMessage.get_message(ApiErrorCode.PERMISSION_DENIED),
            timestamp=timestamp,
            request_id=request_id
        )
    
    # 处理404错误
    if isinstance(exc, Http404):
        return ErrorResponseSchema(
            code=ApiErrorCode.NOT_FOUND,
            message=ApiErrorMessage.get_message(ApiErrorCode.NOT_FOUND),
            timestamp=timestamp,
            request_id=request_id
        )
    
    # 处理其他未知异常
    logger.exception(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    
    return ErrorResponseSchema(
        code=ApiErrorCode.INTERNAL_SERVER_ERROR,
        message=ApiErrorMessage.get_message(ApiErrorCode.INTERNAL_SERVER_ERROR),
        timestamp=timestamp,
        request_id=request_id
    )


def _map_exception_to_api_code(exc: BaseApplicationException) -> str:
    """
    将自定义异常映射到API错误代码
    
    Args:
        exc: 自定义异常对象
        
    Returns:
        str: API错误代码
    """
    # 导入family异常类
    try:
        from apps.family.exceptions import (
            FamilyNotFoundError, FamilyPermissionError, FamilyValidationError,
            FamilyMembershipError, FamilyInvitationError, FamilyLimitExceededError,
            FamilyNameConflictError, FamilyMemberLimitError, FamilyInvitationExpiredError,
            FamilyInvitationUsedError
        )
        
        # Family模块异常映射
        if isinstance(exc, FamilyNotFoundError):
            return ApiErrorCode.FAMILY_NOT_FOUND
        elif isinstance(exc, FamilyPermissionError):
            return ApiErrorCode.FAMILY_PERMISSION_DENIED
        elif isinstance(exc, FamilyNameConflictError):
            return ApiErrorCode.FAMILY_ALREADY_EXISTS
        elif isinstance(exc, FamilyMemberLimitError):
            return ApiErrorCode.FAMILY_LIMIT_EXCEEDED
        elif isinstance(exc, FamilyInvitationExpiredError):
            return ApiErrorCode.FAMILY_INVITATION_EXPIRED
        elif isinstance(exc, FamilyInvitationUsedError):
            return ApiErrorCode.FAMILY_INVITATION_ALREADY_PROCESSED
        elif isinstance(exc, FamilyMembershipError):
            return ApiErrorCode.FAMILY_MEMBER_NOT_FOUND
        elif isinstance(exc, FamilyInvitationError):
            return ApiErrorCode.FAMILY_INVITATION_NOT_FOUND
        elif isinstance(exc, FamilyLimitExceededError):
            return ApiErrorCode.FAMILY_LIMIT_EXCEEDED
        elif isinstance(exc, FamilyValidationError):
            return ApiErrorCode.VALIDATION_ERROR
    except ImportError:
        pass
    
    # 通用异常映射
    from apps.common.exceptions import (
        ValidationError, PermissionError, NotFoundError, LimitExceededError,
        StatusError, ConfigurationError, OperationError, DataError,
        ServiceUnavailableError, RateLimitError, MaintenanceError
    )
    
    if isinstance(exc, ValidationError):
        return ApiErrorCode.VALIDATION_ERROR
    elif isinstance(exc, PermissionError):
        return ApiErrorCode.PERMISSION_DENIED
    elif isinstance(exc, NotFoundError):
        return ApiErrorCode.NOT_FOUND
    elif isinstance(exc, LimitExceededError):
        return ApiErrorCode.RATE_LIMIT_ERROR
    elif isinstance(exc, ServiceUnavailableError):
        return ApiErrorCode.SERVICE_UNAVAILABLE
    elif isinstance(exc, RateLimitError):
        return ApiErrorCode.RATE_LIMIT_ERROR
    elif isinstance(exc, MaintenanceError):
        return ApiErrorCode.MAINTENANCE_ERROR
    elif isinstance(exc, (StatusError, ConfigurationError, OperationError, DataError)):
        return ApiErrorCode.SYSTEM_ERROR
    
    # 默认返回系统错误
    return ApiErrorCode.SYSTEM_ERROR


def _format_django_validation_errors(exc: DjangoValidationError) -> List[Dict[str, Any]]:
    """
    格式化Django验证错误
    
    Args:
        exc: Django验证异常
        
    Returns:
        List[Dict[str, Any]]: 格式化的错误列表
    """
    errors = []
    
    if hasattr(exc, 'error_dict'):
        for field, field_errors in exc.error_dict.items():
            for error in field_errors:
                errors.append({
                    'field': field,
                    'message': str(error.message),
                    'code': error.code or 'validation_error',
                    'value': None
                })
    elif hasattr(exc, 'error_list'):
        for error in exc.error_list:
            errors.append({
                'field': 'non_field_errors',
                'message': str(error.message),
                'code': error.code or 'validation_error',
                'value': None
            })
    else:
        errors.append({
            'field': 'unknown',
            'message': str(exc),
            'code': 'validation_error',
            'value': None
        })
    
    return errors


def register_exception_handlers(api: NinjaAPI):
    """
    注册异常处理器到NinjaAPI实例
    
    Args:
        api: NinjaAPI实例
    """
    # 注册自定义异常处理器
    api.add_exception_handler(BaseApplicationException, api_exception_handler)
    api.add_exception_handler(DjangoValidationError, api_exception_handler)
    api.add_exception_handler(NinjaValidationError, api_exception_handler)
    api.add_exception_handler(PydanticValidationError, api_exception_handler)
    api.add_exception_handler(PermissionDenied, api_exception_handler)
    api.add_exception_handler(Http404, api_exception_handler)
    api.add_exception_handler(Exception, api_exception_handler)