"""
公共中间件

该文件定义了系统中使用的公共中间件。
遵循Django最佳实践和Google Python Style Guide。
"""

from datetime import datetime
from typing import Callable, Optional
import threading
import time
import uuid
import traceback

from config.logging_config import get_request_logger
from django.conf import settings
from django.core.cache import cache
from django.db import DatabaseError, IntegrityError, connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from loguru import logger

from .constants import ApiErrorCode, ApiErrorMessage
from .exceptions import BaseApplicationException
from .schemas import ErrorResponseSchema

_request_local = threading.local()

def get_current_request_id() -> Optional[str]:
    """获取当前请求ID"""
    return getattr(_request_local, 'request_id', None)

def get_current_user_id() -> Optional[int]:
    """获取当前用户ID"""
    return getattr(_request_local, 'user_id', None)

def get_current_endpoint() -> Optional[str]:
    """获取当前API端点"""
    return getattr(_request_local, 'endpoint', None)

class RequestTrackingMiddleware(MiddlewareMixin):
    """
    请求跟踪中间件

    功能：
    - 为每个请求生成唯一ID
    - 记录请求开始和结束时间
    - 计算请求处理时长
    - 记录请求基本信息
    - 设置线程本地存储的请求上下文
    """

    def process_request(self, request: HttpRequest) -> None:
        """处理请求开始"""
        # 生成或获取请求ID
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        request.request_id = request_id
        request.start_time = time.time()
        request.timestamp = datetime.now()

        # 设置线程本地存储
        _request_local.request_id = request_id
        _request_local.endpoint = f"{request.method} {request.path}"

        # 获取用户信息（如果已认证）
        user_id = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = request.user.id
            _request_local.user_id = user_id

        # 创建请求上下文日志记录器
        request.logger = get_request_logger(
            request_id=request_id,
            user_id=user_id,
            endpoint=_request_local.endpoint
        )

        # 记录请求开始
        request.logger.info(
            f"Request started: {request.method} {request.path}",
            method=request.method,
            path=request.path,
            query_params=dict(request.GET),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            remote_addr=self._get_client_ip(request),
            content_type=request.content_type
        )

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """处理响应"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time

            # 记录请求完成
            if hasattr(request, 'logger'):
                request.logger.info(
                    f"Request completed: {request.method} {request.path} - "
                    f"Status: {response.status_code}, Duration: {duration:.3f}s",
                    status_code=response.status_code,
                    duration=duration,
                    response_size=len(response.content) if hasattr(response, 'content') else 0
                )
            else:
                logger.info(
                    f"Request completed: {request.method} {request.path} - "
                    f"Status: {response.status_code}, Duration: {duration:.3f}s",
                    extra={
                        'request_id': getattr(request, 'request_id', 'unknown'),
                        'method': request.method,
                        'path': request.path,
                        'status_code': response.status_code,
                        'duration': duration,
                        'response_size': len(response.content) if hasattr(response, 'content') else 0
                    }
                )

            # 添加响应头
            response['X-Request-ID'] = getattr(request, 'request_id', 'unknown')
            response['X-Response-Time'] = f"{duration:.3f}s"

        # 清理线程本地存储
        self._cleanup_request_local()

        return response

    def process_exception(self, request: HttpRequest, exception: Exception) -> Optional[HttpResponse]:
        """处理请求异常"""
        if hasattr(request, 'logger'):
            request.logger.error(
                f"Request failed: {request.method} {request.path}",
                exception_type=type(exception).__name__,
                exception_message=str(exception),
                traceback=traceback.format_exc()
            )
        elif hasattr(request, 'request_id'):
            logger.error(
                f"Request failed: {request.method} {request.path}",
                extra={
                    'request_id': request.request_id,
                    'exception_type': type(exception).__name__,
                    'exception_message': str(exception),
                    'traceback': traceback.format_exc()
                }
            )

        # 清理线程本地存储
        self._cleanup_request_local()

        return None

    def _get_client_ip(self, request: HttpRequest) -> str:
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'

    def _cleanup_request_local(self) -> None:
        """清理线程本地存储"""
        for attr in ['request_id', 'user_id', 'endpoint']:
            if hasattr(_request_local, attr):
                delattr(_request_local, attr)

class ExceptionHandlingMiddleware(MiddlewareMixin):
    """
    异常处理中间件

    功能：
    - 捕获所有未处理的异常
    - 提供统一的错误响应格式
    - 记录详细的异常信息
    - 区分不同类型的异常
    - 保护敏感信息不泄露
    - 利用请求上下文进行日志追踪
    """

    def _log_exception(self, request: HttpRequest, exception: Exception, request_id: str) -> None:
        """记录异常信息"""
        # 优先使用请求上下文日志记录器
        request_logger = getattr(request, 'logger', None)
        if request_logger:
            # 使用请求上下文日志记录器，自动包含请求ID等上下文信息
            if isinstance(exception, BaseApplicationException):
                request_logger.warning(
                    f"Application exception: {type(exception).__name__}: {str(exception)}",
                    exception_type=type(exception).__name__,
                    exception_message=str(exception),
                    traceback=traceback.format_exc()
                )
            elif isinstance(exception, (DatabaseError, IntegrityError)):
                request_logger.error(
                    f"Database exception: {type(exception).__name__}: {str(exception)}",
                    exception_type=type(exception).__name__,
                    exception_message=str(exception),
                    traceback=traceback.format_exc()
                )
            else:
                request_logger.error(
                    f"Unhandled exception: {type(exception).__name__}: {str(exception)}",
                    exception_type=type(exception).__name__,
                    exception_message=str(exception),
                    traceback=traceback.format_exc()
                )
        else:
            # 回退到传统日志记录方式
            exception_info = {
                'request_id': request_id,
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'method': request.method,
                'path': request.path,
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'remote_addr': request.META.get('REMOTE_ADDR', ''),
                'traceback': traceback.format_exc()
            }

            # 根据异常类型选择日志级别
            if isinstance(exception, BaseApplicationException):
                logger.warning(
                    f"Application exception: {type(exception).__name__}: {str(exception)}",
                    extra=exception_info
                )
            elif isinstance(exception, (DatabaseError, IntegrityError)):
                logger.error(
                    f"Database exception: {type(exception).__name__}: {str(exception)}",
                    extra=exception_info
                )
            else:
                logger.error(
                    f"Unhandled exception: {type(exception).__name__}: {str(exception)}",
                    extra=exception_info
                )

    def _create_error_response(self, exception: Exception, request_id: str, timestamp: datetime) -> ErrorResponseSchema:
        """创建错误响应"""
        # 处理自定义应用异常
        if isinstance(exception, BaseApplicationException):
            return ErrorResponseSchema(
                code=getattr(exception, 'code', ApiErrorCode.SYSTEM_ERROR),
                message=str(exception),
                data=getattr(exception, 'data', None),
                errors=getattr(exception, 'errors', None),
                timestamp=timestamp,
                request_id=request_id
            )

        # 处理数据库异常
        if isinstance(exception, IntegrityError):
            return ErrorResponseSchema(
                code=ApiErrorCode.VALIDATION_ERROR,
                message=ApiErrorMessage.get_message(ApiErrorCode.VALIDATION_ERROR),
                data={'detail': '数据完整性约束违反'},
                timestamp=timestamp,
                request_id=request_id
            )

        if isinstance(exception, DatabaseError):
            return ErrorResponseSchema(
                code=ApiErrorCode.SERVICE_UNAVAILABLE,
                message=ApiErrorMessage.get_message(ApiErrorCode.SERVICE_UNAVAILABLE),
                data={'detail': '数据库服务暂时不可用'},
                timestamp=timestamp,
                request_id=request_id
            )

        # 处理Django验证异常
        from django.core.exceptions import ValidationError as DjangoValidationError
        if isinstance(exception, DjangoValidationError):
            return ErrorResponseSchema(
                code=ApiErrorCode.VALIDATION_ERROR,
                message=ApiErrorMessage.get_message(ApiErrorCode.VALIDATION_ERROR),
                data={'detail': str(exception)},
                timestamp=timestamp,
                request_id=request_id
            )

        # 处理其他未知异常
        if settings.DEBUG:
            # 开发环境显示详细错误信息
            return ErrorResponseSchema(
                code=ApiErrorCode.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {str(exception)}",
                data={'traceback': traceback.format_exc()},
                timestamp=timestamp,
                request_id=request_id
            )
        else:
            # 生产环境隐藏敏感信息
            return ErrorResponseSchema(
                code=ApiErrorCode.INTERNAL_SERVER_ERROR,
                message=ApiErrorMessage.get_message(ApiErrorCode.INTERNAL_SERVER_ERROR),
                timestamp=timestamp,
                request_id=request_id
            )

    def _get_http_status_code(self, exception: Exception) -> int:
        """获取HTTP状态码"""
        if isinstance(exception, BaseApplicationException):
            return getattr(exception, 'status_code', 500)
        elif isinstance(exception, DjangoValidationError):
            return 400
        elif isinstance(exception, (DatabaseError, IntegrityError)):
            return 503
        else:
            return 500

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    性能监控中间件

    功能：
    - 监控API响应时间
    - 记录慢查询
    - 统计API调用频率
    - 检测性能异常
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        self.slow_request_threshold = getattr(settings, 'SLOW_REQUEST_THRESHOLD', 1.0)  # 1秒
        super().__init__(get_response)

    def process_request(self, request: HttpRequest) -> None:
        """记录请求开始时间"""
        request._performance_start_time = time.time()

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """记录性能指标"""
        if hasattr(request, '_performance_start_time'):
            duration = time.time() - request._performance_start_time
            self._record_performance_metrics(request, response, duration)
            
            # 如果是慢请求，记录警告
            if duration > self.slow_request_threshold:
                logger.warning(
                    f"Slow request detected: {request.method} {request.path} - {duration:.3f}s",
                    extra={
                        'endpoint': f"{request.method} {request.path}",
                        'duration': duration,
                        'threshold': self.slow_request_threshold
                    }
                )
        
        return response

    def _record_performance_metrics(self, request: HttpRequest, response: HttpResponse, duration: float) -> None:
        """记录性能指标"""
        # 优先使用请求上下文日志记录器
        request_logger = getattr(request, 'logger', None)
        if request_logger:
            request_logger.info(
                f"Performance metrics: {request.method} {request.path} - "
                f"Status: {response.status_code}, Duration: {duration:.3f}s",
                endpoint=f"{request.method} {request.path}",
                status_code=response.status_code,
                duration=duration,
                timestamp=time.time()
            )
        else:
            metrics = {
                'endpoint': f"{request.method} {request.path}",
                'status_code': response.status_code,
                'duration': duration,
                'timestamp': time.time()
            }

            # 记录到日志（实际应用中可以发送到监控系统）
            logger.info(
                f"Performance metrics: {metrics['endpoint']} - "
                f"Status: {metrics['status_code']}, Duration: {duration:.3f}s",
                extra=metrics
            )

class CorsMiddleware(MiddlewareMixin):
    """
    CORS中间件

    功能：
    - 处理跨域请求
    - 支持预检请求
    - 配置允许的域名、方法和头部
    - 增强安全性检查
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        self.allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        self.allowed_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
        self.allowed_headers = ['Accept', 'Authorization', 'Content-Type', 'X-Requested-With']
        super().__init__(get_response)

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """处理预检请求"""
        if request.method == 'OPTIONS':
            origin = request.META.get('HTTP_ORIGIN')
            if origin and self._is_origin_allowed(origin):
                response = HttpResponse()
                self._add_cors_headers(response, origin)
                response['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
                response['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
                response['Access-Control-Max-Age'] = '86400'  # 24小时
                return response
        
        return None

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """为响应添加CORS头部"""
        origin = request.META.get('HTTP_ORIGIN')
        if origin and self._is_origin_allowed(origin):
            self._add_cors_headers(response, origin)
        
        return response

    def _is_origin_allowed(self, origin: Optional[str]) -> bool:
        """检查源是否被允许"""
        if not origin:
            return False

        if '*' in self.allowed_origins:
            return True

        return origin in self.allowed_origins

    def _add_cors_headers(self, response: HttpResponse, origin: str) -> None:
        """添加CORS头部"""
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Vary'] = 'Origin'

class RateLimitMiddleware(MiddlewareMixin):
    """
    限流中间件

    功能：
    - 基于IP地址的请求限流
    - 支持不同端点的不同限制
    - 提供限流状态信息
    - 记录限流事件
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        self.default_limit = getattr(settings, 'RATE_LIMIT_DEFAULT', 100)  # 每分钟100次
        self.window_size = 60  # 1分钟窗口
        super().__init__(get_response)

    def get_client_ip(self, request: HttpRequest) -> str:
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'

    def get_cache_key(self, request: HttpRequest) -> str:
        """生成缓存键"""
        ip = self.get_client_ip(request)
        return f"rate_limit:{ip}"

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """检查请求限制"""
        cache_key = self.get_cache_key(request)
        
        # 获取当前计数
        current_count = cache.get(cache_key, 0)
        
        if current_count >= self.default_limit:
            # 超过限制，返回429错误
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': f'Too many requests. Limit: {self.default_limit} per minute'
            }, status=429)
        
        # 增加计数
        cache.set(cache_key, current_count + 1, self.window_size)
        
        return None

class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    安全头部中间件

    功能：
    - 添加安全相关的HTTP头部
    - 防止常见的安全攻击
    - 提供内容安全策略
    - 增强API安全性
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        super().__init__(get_response)

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """添加安全头部"""
        # 防止XSS攻击
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # 内容安全策略
        response['Content-Security-Policy'] = "default-src 'self'"
        
        # 严格传输安全
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # 推荐人策略
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response

class HealthCheckMiddleware(MiddlewareMixin):
    """
    健康检查中间件

    功能：
    - 提供系统健康状态检查
    - 监控关键组件状态
    - 支持负载均衡器健康检查
    - 记录系统状态指标
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """处理健康检查请求"""
        if request.path == '/health/' and request.method == 'GET':
            health_data = self._check_system_health()
            status_code = 200 if health_data['status'] == 'healthy' else 503
            return JsonResponse(health_data, status=status_code)
        
        return None

    def _check_system_health(self) -> dict:
        """检查系统健康状态"""
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': getattr(settings, 'API_VERSION', '1.0'),
            'checks': {}
        }

        # 检查数据库连接
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_data['checks']['database'] = {'status': 'healthy'}
        except Exception as e:
            health_data['checks']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_data['status'] = 'unhealthy'

        # 检查缓存
        try:
            cache.set('health_check', 'ok', 10)
            cache_value = cache.get('health_check')
            if cache_value == 'ok':
                health_data['checks']['cache'] = {'status': 'healthy'}
            else:
                health_data['checks']['cache'] = {'status': 'unhealthy', 'error': 'Cache test failed'}
                health_data['status'] = 'unhealthy'
        except Exception as e:
            health_data['checks']['cache'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_data['status'] = 'unhealthy'

        return health_data

# 向后兼容性别名
RequestIdMiddleware = RequestTrackingMiddleware

class NinjaResponseFormatterMiddleware(MiddlewareMixin):
    """
    Django Ninja响应格式化中间件

    功能：
    - 拦截Django Ninja的默认响应并转换为统一格式
    - 特别处理认证失败等默认响应
    - 保持响应格式的一致性
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        super().__init__(get_response)

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """处理响应格式化"""
        # 只处理API路径的响应
        if not request.path.startswith('/api/'):
            return response
        
        # 如果是JSON响应且状态码表示错误，尝试格式化
        if (response.get('Content-Type', '').startswith('application/json') and 
            response.status_code >= 400):
            try:
                import json
                content = json.loads(response.content.decode('utf-8'))
                
                # 如果不是我们的标准格式，转换为标准格式
                if not isinstance(content, dict) or 'code' not in content:
                    formatted_content = {
                        'code': response.status_code,
                        'message': content.get('detail', str(content)) if isinstance(content, dict) else str(content),
                        'data': None,
                        'timestamp': datetime.now().isoformat(),
                        'request_id': getattr(request, 'request_id', None)
                    }
                    response.content = json.dumps(formatted_content, ensure_ascii=False)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        
        return response