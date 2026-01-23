from datetime import datetime
from typing import Any, Dict, List
import uuid
import traceback
from django.http import Http404, HttpRequest, JsonResponse
from django.conf import settings
from ninja import NinjaAPI
from ninja.errors import ValidationError as NinjaValidationError
from pydantic import ValidationError as PydanticValidationError
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
    PermissionDenied,
    ObjectDoesNotExist,
    MultipleObjectsReturned,
    SuspiciousOperation,
    DisallowedHost,
    RequestDataTooBig,
    TooManyFieldsSent,
)
from django.db import DatabaseError, IntegrityError, OperationalError, InternalError
from loguru import logger
from .constants import ApiErrorCode, ApiErrorMessage
from .exceptions import BaseApplicationException
from .schemas import ErrorResponseSchema
from .exception_utils import (
    exception_stats,
    SensitiveDataFilter,
    get_exception_info,
    categorize_exception,
    format_exception_for_logging,
)
from config.exception_config import (
    EXCEPTION_HANDLING_CONFIG,
    SENSITIVE_DATA_CONFIG,
    ALERT_CONFIG,
    LOG_FORMAT_CONFIG,
)

"""公共模块异常处理器

该模块定义了统一的异常处理逻辑，用于处理API请求中的各种异常情况。
遵循Django Ninja最佳实践和Google Python Style Guide。

设计原则：
- 统一性：所有异常都通过统一的处理器处理
- 安全性：敏感信息不会泄露给客户端
- 可观测性：详细的异常日志记录
- 用户友好：提供清晰的错误信息
- 健壮性：处理各种边界情况
- 智能化：集成异常统计、监控和告警
"""


def generate_request_id() -> str:
    """生成请求ID"""
    return str(uuid.uuid4())


class EnhancedExceptionHandler:
    """
    增强的异常处理器

    功能：
    - 处理各种类型的异常
    - 提供详细的错误信息
    - 记录异常日志
    - 保护敏感信息
    - 支持异常监控和告警
    - 集成异常统计和分析
    """

    def __init__(self):
        self.sensitive_filter = SensitiveDataFilter()
        self.critical_exceptions = {
            DatabaseError,
            OperationalError,
            InternalError,
            SuspiciousOperation,
            DisallowedHost,
        }

    def handle_exception(
        self, request: HttpRequest, exception: Exception
    ) -> Dict[str, Any]:
        """
        统一异常处理入口

        Args:
            request: HTTP请求对象
            exception: 异常实例

        Returns:
            Dict: 标准化的错误响应数据
        """
        # 确保request_id是字符串类型
        request_id = getattr(request, "request_id", None)
        if not isinstance(request_id, str):
            request_id = generate_request_id()

        timestamp = datetime.now()

        # 记录异常统计
        self._record_exception_stats(exception, request)

        # 记录异常日志
        self._log_exception(request, exception, request_id)

        # 检查是否为关键异常
        if type(exception) in self.critical_exceptions:
            self._handle_critical_exception(request, exception, request_id)

        # 生成错误响应
        error_response = self._create_error_response(exception, request_id, timestamp)

        return {
            "response_data": error_response.dict(),
            "status_code": self._get_http_status_code(exception),
            "headers": self._get_response_headers(exception),
        }

    def _record_exception_stats(
        self, exception: Exception, request: HttpRequest
    ) -> None:
        """记录异常统计信息"""
        try:
            user_id = (
                getattr(request.user, "id", None) if hasattr(request, "user") else None
            )
            exception_stats.record_exception(
                exception_type=type(exception).__name__,
                path=request.path,
                user_id=str(user_id) if user_id else None,
            )
        except Exception as e:
            logger.warning(f"Failed to record exception statistics: {e}")

    def _log_exception(
        self, request: HttpRequest, exception: Exception, request_id: str
    ) -> None:
        """记录异常详细信息"""
        try:
            # 收集请求数据
            request_data = self._collect_request_data(request)

            # 获取用户信息
            user_id = (
                getattr(request.user, "id", None) if hasattr(request, "user") else None
            )

            # 格式化异常信息
            log_data = format_exception_for_logging(
                exception=exception,
                request_data=request_data,
                user_id=str(user_id) if user_id else None,
                request_id=request_id,
            )

            # 根据异常类型选择日志级别
            log_level = self._get_log_level(exception)

            # 格式化日志消息
            log_message = LOG_FORMAT_CONFIG["EXCEPTION_LOG_FORMAT"].format(
                timestamp=log_data["timestamp"],
                level=log_level.upper(),
                request_id=request_id,
                method=request.method,
                path=request.path,
                exception_type=log_data["exception_info"]["type"],
                exception_message=log_data["exception_info"]["message"],
                user_id=user_id or "anonymous",
                client_ip=request.META.get("REMOTE_ADDR", "unknown"),
                duration=getattr(request, "_processing_time", 0),
            )

            # 记录日志 - 使用loguru的方式
            if log_level.lower() == "critical":
                logger.critical(log_message)
            elif log_level.lower() == "error":
                logger.error(log_message)
            elif log_level.lower() == "warning":
                logger.warning(log_message)
            elif log_level.lower() == "info":
                logger.info(log_message)
            else:
                logger.debug(log_message)

        except Exception as e:
            logger.error(f"Failed to log exception: {e}")

    def _collect_request_data(self, request: HttpRequest) -> Dict[str, Any]:
        """收集请求数据"""
        request_data = {
            "method": request.method,
            "path": request.path,
            "query_params": dict(request.GET),
            "headers": dict(request.META),
            "content_type": request.META.get("CONTENT_TYPE", ""),
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "remote_addr": request.META.get("REMOTE_ADDR", ""),
        }

        # 添加POST数据（如果配置允许）
        if (
            request.method in ["POST", "PUT", "PATCH"]
            and EXCEPTION_HANDLING_CONFIG["LOG_REQUEST_BODY"]
        ):
            try:
                post_data = dict(request.POST)
                request_data["post_data"] = self.sensitive_filter.filter_dict(post_data)
            except Exception:
                request_data["post_data"] = "[ERROR_READING_POST_DATA]"

        # 过滤敏感头部信息
        request_data["headers"] = self.sensitive_filter.filter_headers(
            request_data["headers"]
        )

        return request_data

    def _get_log_level(self, exception: Exception) -> str:
        """获取异常的日志级别"""
        if isinstance(exception, BaseApplicationException):
            return getattr(exception, "log_level", "WARNING").lower()
        elif isinstance(exception, (DatabaseError, OperationalError, InternalError)):
            return "error"
        elif isinstance(exception, (SuspiciousOperation, DisallowedHost)):
            return "critical"
        elif isinstance(
            exception,
            (DjangoValidationError, NinjaValidationError, PydanticValidationError),
        ):
            return "info"
        else:
            return "error"

    def _handle_critical_exception(
        self, request: HttpRequest, exception: Exception, request_id: str
    ) -> None:
        """处理关键异常"""
        try:
            # 记录关键异常
            logger.critical(
                f"CRITICAL EXCEPTION DETECTED: {type(exception).__name__}",
                extra={
                    "request_id": request_id,
                    "exception_type": type(exception).__name__,
                    "exception_message": str(exception),
                    "path": request.path,
                    "method": request.method,
                    "user_id": getattr(request.user, "id", None)
                    if hasattr(request, "user")
                    else None,
                    "traceback": traceback.format_exc()
                    if EXCEPTION_HANDLING_CONFIG["ENABLE_DETAILED_ERRORS"]
                    else None,
                },
            )

            # 触发告警（如果启用）
            if ALERT_CONFIG["ENABLE_EXCEPTION_ALERTS"]:
                self._trigger_alert(exception, request, request_id)

        except Exception as e:
            logger.error(f"Failed to handle critical exception: {e}")

    def _trigger_alert(
        self, exception: Exception, request: HttpRequest, request_id: str
    ) -> None:
        """触发异常告警"""
        try:
            alert_message = (
                f"Critical Exception Alert\n"
                f"Request ID: {request_id}\n"
                f"Exception: {type(exception).__name__}: {str(exception)}\n"
                f"Path: {request.method} {request.path}\n"
                f"Time: {datetime.now().isoformat()}\n"
                f"User: {getattr(request.user, 'id', 'anonymous') if hasattr(request, 'user') else 'anonymous'}\n"
                f"IP: {request.META.get('REMOTE_ADDR', 'unknown')}"
            )

            # 这里可以集成邮件、短信、钉钉等告警方式
            logger.critical(f"ALERT TRIGGERED: {alert_message}")

        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")

    def _create_error_response(
        self, exception: Exception, request_id: str, timestamp: datetime
    ) -> ErrorResponseSchema:
        """创建标准化错误响应"""
        # 处理自定义应用异常
        if isinstance(exception, BaseApplicationException):
            api_code = _map_exception_to_api_code(exception)

            return ErrorResponseSchema(
                code=self._get_http_status_code(exception),
                message=str(exception),
                data={
                    "api_code": getattr(exception, "code", ApiErrorCode.SYSTEM_ERROR),
                    "detail": str(exception),
                    **(getattr(exception, "data", None) or {}),
                },
                errors=getattr(exception, "errors", None),
                timestamp=timestamp,
                request_id=request_id,
            )

        # 处理数据库相关异常
        if isinstance(exception, IntegrityError):
            return ErrorResponseSchema(
                code=409,
                message=ApiErrorMessage.get_message(ApiErrorCode.VALIDATION_ERROR),
                data={
                    "api_code": ApiErrorCode.VALIDATION_ERROR,
                    "detail": "数据完整性约束违反",
                    "type": "integrity_error",
                },
                timestamp=timestamp,
                request_id=request_id,
            )

        if isinstance(exception, OperationalError):
            return ErrorResponseSchema(
                code=503,
                message=ApiErrorMessage.get_message(ApiErrorCode.SERVICE_UNAVAILABLE),
                data={
                    "api_code": ApiErrorCode.SERVICE_UNAVAILABLE,
                    "detail": "数据库操作错误",
                    "type": "operational_error",
                },
                timestamp=timestamp,
                request_id=request_id,
            )

        if isinstance(exception, DatabaseError):
            return ErrorResponseSchema(
                code=503,
                message=ApiErrorMessage.get_message(ApiErrorCode.SERVICE_UNAVAILABLE),
                data={
                    "api_code": ApiErrorCode.SERVICE_UNAVAILABLE,
                    "detail": "数据库服务异常",
                    "type": "database_error",
                },
                timestamp=timestamp,
                request_id=request_id,
            )

        # 处理Django核心异常
        if isinstance(exception, Http404):
            return ErrorResponseSchema(
                code=404,
                message=ApiErrorMessage.get_message(ApiErrorCode.NOT_FOUND),
                data={"api_code": ApiErrorCode.NOT_FOUND, "detail": "请求的资源不存在"},
                timestamp=timestamp,
                request_id=request_id,
            )

        if isinstance(exception, PermissionDenied):
            return ErrorResponseSchema(
                code=403,
                message=ApiErrorMessage.get_message(ApiErrorCode.PERMISSION_DENIED),
                data={"api_code": ApiErrorCode.PERMISSION_DENIED, "detail": "权限不足"},
                timestamp=timestamp,
                request_id=request_id,
            )

        if isinstance(exception, ObjectDoesNotExist):
            return ErrorResponseSchema(
                code=404,
                message=ApiErrorMessage.get_message(ApiErrorCode.NOT_FOUND),
                data={"api_code": ApiErrorCode.NOT_FOUND, "detail": "对象不存在"},
                timestamp=timestamp,
                request_id=request_id,
            )

        if isinstance(exception, MultipleObjectsReturned):
            return ErrorResponseSchema(
                code=409,
                message=ApiErrorMessage.get_message(ApiErrorCode.VALIDATION_ERROR),
                data={
                    "api_code": ApiErrorCode.VALIDATION_ERROR,
                    "detail": "查询返回多个对象，期望唯一结果",
                },
                timestamp=timestamp,
                request_id=request_id,
            )

        # 处理安全相关异常
        if isinstance(exception, SuspiciousOperation):
            return ErrorResponseSchema(
                code=403,
                message=ApiErrorMessage.get_message(ApiErrorCode.FORBIDDEN),
                data={"api_code": ApiErrorCode.FORBIDDEN, "detail": "检测到可疑操作"},
                timestamp=timestamp,
                request_id=request_id,
            )

        if isinstance(exception, DisallowedHost):
            return ErrorResponseSchema(
                code=403,
                message=ApiErrorMessage.get_message(ApiErrorCode.FORBIDDEN),
                data={"api_code": ApiErrorCode.FORBIDDEN, "detail": "不允许的主机"},
                timestamp=timestamp,
                request_id=request_id,
            )

        # 处理请求数据异常
        if isinstance(exception, RequestDataTooBig):
            return ErrorResponseSchema(
                code=413,
                message=ApiErrorMessage.get_message(ApiErrorCode.VALIDATION_ERROR),
                data={
                    "api_code": ApiErrorCode.VALIDATION_ERROR,
                    "detail": "请求数据过大",
                },
                timestamp=timestamp,
                request_id=request_id,
            )

        if isinstance(exception, TooManyFieldsSent):
            return ErrorResponseSchema(
                code=400,
                message=ApiErrorMessage.get_message(ApiErrorCode.VALIDATION_ERROR),
                data={
                    "api_code": ApiErrorCode.VALIDATION_ERROR,
                    "detail": "请求字段过多",
                },
                timestamp=timestamp,
                request_id=request_id,
            )

        # 处理验证异常
        if isinstance(exception, DjangoValidationError):
            return self._handle_django_validation_error(
                exception, request_id, timestamp
            )

        if isinstance(exception, NinjaValidationError):
            return self._handle_ninja_validation_error(exception, request_id, timestamp)

        if isinstance(exception, PydanticValidationError):
            return self._handle_pydantic_validation_error(
                exception, request_id, timestamp
            )

        # 处理其他未知异常
        return self._handle_unknown_exception(exception, request_id, timestamp)

    def _handle_django_validation_error(
        self, exception: DjangoValidationError, request_id: str, timestamp: datetime
    ) -> ErrorResponseSchema:
        """处理Django验证异常"""
        errors = []

        if hasattr(exception, "error_dict"):
            # 字段级验证错误
            for field, error_list in exception.error_dict.items():
                for error in error_list:
                    errors.append(
                        {
                            "field": field,
                            "message": str(error),
                            "code": "validation_error",
                            "value": None,
                        }
                    )
        elif hasattr(exception, "error_list"):
            # 非字段级验证错误
            for error in exception.error_list:
                errors.append(
                    {
                        "field": "non_field_errors",
                        "message": str(error),
                        "code": "validation_error",
                        "value": None,
                    }
                )
        else:
            errors.append(
                {
                    "field": "unknown",
                    "message": str(exception),
                    "code": "validation_error",
                    "value": None,
                }
            )

        return ErrorResponseSchema(
            code=400,
            message=ApiErrorMessage.get_message(ApiErrorCode.VALIDATION_ERROR),
            data={"api_code": ApiErrorCode.VALIDATION_ERROR, "detail": "数据验证失败"},
            errors=errors,
            timestamp=timestamp,
            request_id=request_id,
        )

    def _handle_ninja_validation_error(
        self, exception: NinjaValidationError, request_id: str, timestamp: datetime
    ) -> ErrorResponseSchema:
        """处理Ninja验证异常"""
        errors = []
        for error in exception.errors:
            error_info = {
                "field": ".".join(str(loc) for loc in error.get("loc", [])),
                "message": error.get("msg", ""),
                "type": error.get("type", ""),
                "input": error.get("input", ""),
            }
            errors.append(error_info)

        return ErrorResponseSchema(
            code=400,
            message=ApiErrorMessage.get_message(ApiErrorCode.VALIDATION_ERROR),
            data={
                "api_code": ApiErrorCode.VALIDATION_ERROR,
                "detail": "API参数验证失败",
            },
            errors=errors,
            timestamp=timestamp,
            request_id=request_id,
        )

    def _handle_pydantic_validation_error(
        self, exception: PydanticValidationError, request_id: str, timestamp: datetime
    ) -> ErrorResponseSchema:
        """处理Pydantic验证异常"""
        errors = []
        for error in exception.errors():
            error_info = {
                "field": ".".join(str(loc) for loc in error.get("loc", [])),
                "message": error.get("msg", ""),
                "type": error.get("type", ""),
                "input": str(error.get("input", "")),
            }
            errors.append(error_info)

        return ErrorResponseSchema(
            code=400,
            message=ApiErrorMessage.get_message(ApiErrorCode.VALIDATION_ERROR),
            data={
                "api_code": ApiErrorCode.VALIDATION_ERROR,
                "detail": "数据模型验证失败",
            },
            errors=errors,
            timestamp=timestamp,
            request_id=request_id,
        )

    def _handle_unknown_exception(
        self, exception: Exception, request_id: str, timestamp: datetime
    ) -> ErrorResponseSchema:
        """处理未知异常"""
        if settings.DEBUG:
            # 开发环境显示详细错误信息
            return ErrorResponseSchema(
                code=500,
                message=f"Internal Server Error: {str(exception)}",
                data={
                    "api_code": ApiErrorCode.INTERNAL_SERVER_ERROR,
                    "exception_type": type(exception).__name__,
                    "traceback": traceback.format_exc().split("\n"),
                },
                timestamp=timestamp,
                request_id=request_id,
            )
        else:
            # 生产环境隐藏敏感信息
            return ErrorResponseSchema(
                code=500,
                message=ApiErrorMessage.get_message(ApiErrorCode.INTERNAL_SERVER_ERROR),
                data={
                    "api_code": ApiErrorCode.INTERNAL_SERVER_ERROR,
                    "detail": "服务器内部错误",
                },
                timestamp=timestamp,
                request_id=request_id,
            )

    def _get_http_status_code(self, exception: Exception) -> int:
        """获取HTTP状态码"""
        status_code_mapping = {
            BaseApplicationException: lambda e: getattr(e, "status_code", 500),
            Http404: 404,
            ObjectDoesNotExist: 404,
            PermissionDenied: 403,
            SuspiciousOperation: 403,
            DisallowedHost: 403,
            DjangoValidationError: 400,
            NinjaValidationError: 400,
            PydanticValidationError: 400,
            RequestDataTooBig: 413,
            TooManyFieldsSent: 400,
            IntegrityError: 409,
            OperationalError: 503,
            DatabaseError: 503,
            MultipleObjectsReturned: 409,
        }

        for exc_type, status_code in status_code_mapping.items():
            if isinstance(exception, exc_type):
                if callable(status_code):
                    return status_code(exception)
                return status_code

        return 500

    def _get_response_headers(self, exception: Exception) -> Dict[str, str]:
        """获取响应头"""
        headers = {
            "Content-Type": "application/json",
            "X-Exception-Type": type(exception).__name__,
        }

        # 为特定异常添加特殊头部
        if isinstance(exception, RequestDataTooBig):
            headers["X-Max-Request-Size"] = str(
                getattr(settings, "DATA_UPLOAD_MAX_MEMORY_SIZE", 2621440)
            )

        return headers


# 全局异常处理器实例
exception_handler = EnhancedExceptionHandler()


def api_exception_handler(request: HttpRequest, exception: Exception):
    """
    API异常处理器入口函数

    Args:
        request: HTTP请求对象
        exception: 异常实例

    Returns:
        HttpResponse: Django HTTP响应对象
    """

    # 获取异常处理结果
    result = exception_handler.handle_exception(request, exception)

    # 提取响应数据、状态码和头部
    response_data = result["response_data"]
    status_code = result["status_code"]
    headers = result.get("headers", {})

    # 创建JSON响应
    response = JsonResponse(response_data, status=status_code, safe=False)

    # 添加自定义头部
    for key, value in headers.items():
        response[key] = value

    return response


def format_validation_errors(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """格式化验证错误"""
    formatted_errors = []

    for error in errors:
        if isinstance(error, dict):
            formatted_errors.append(
                {
                    "field": error.get("loc", ["unknown"])[-1]
                    if error.get("loc")
                    else "unknown",
                    "message": error.get("msg", "Validation error"),
                    "code": error.get("type", "validation_error"),
                    "value": error.get("input"),
                }
            )
        else:
            formatted_errors.append(
                {
                    "field": "unknown",
                    "message": str(error),
                    "code": "validation_error",
                    "value": None,
                }
            )

    return formatted_errors


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
            FamilyNotFoundError,
            FamilyPermissionError,
            FamilyValidationError,
            FamilyMembershipError,
            FamilyInvitationError,
            FamilyLimitExceededError,
            FamilyNameConflictError,
            FamilyMemberLimitError,
            FamilyInvitationExpiredError,
            FamilyInvitationUsedError,
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
        ValidationError,
        PermissionError,
        NotFoundError,
        LimitExceededError,
        StatusError,
        ConfigurationError,
        OperationError,
        DataError,
        ServiceUnavailableError,
        RateLimitError,
        MaintenanceError,
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


def _format_django_validation_errors(
    exc: DjangoValidationError,
) -> List[Dict[str, Any]]:
    """
    格式化Django验证错误

    Args:
        exc: Django验证异常

    Returns:
        List[Dict[str, Any]]: 格式化的错误列表
    """
    errors = []

    if hasattr(exc, "error_dict"):
        for field, field_errors in exc.error_dict.items():
            for error in field_errors:
                errors.append(
                    {
                        "field": field,
                        "message": str(error.message),
                        "code": error.code or "validation_error",
                        "value": None,
                    }
                )
    elif hasattr(exc, "error_list"):
        for error in exc.error_list:
            errors.append(
                {
                    "field": "non_field_errors",
                    "message": str(error.message),
                    "code": error.code or "validation_error",
                    "value": None,
                }
            )
    else:
        errors.append(
            {
                "field": "unknown",
                "message": str(exc),
                "code": "validation_error",
                "value": None,
            }
        )

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
