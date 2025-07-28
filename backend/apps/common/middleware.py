"""
公共模块中间件

该模块定义了通用的中间件，用于处理请求ID、CORS、限流等功能。
遵循Django最佳实践和Google Python Style Guide。
"""

import time
import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings

from .constants import RateLimitDefaults, ApiErrorCode, ApiErrorMessage


class RequestIdMiddleware(MiddlewareMixin):
    """请求ID中间件"""
    
    def process_request(self, request: HttpRequest) -> None:
        """为每个请求生成唯一ID"""
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        request.request_id = request_id
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """在响应头中添加请求ID"""
        if hasattr(request, 'request_id'):
            response['X-Request-ID'] = request.request_id
        return response


class CorsMiddleware(MiddlewareMixin):
    """CORS中间件"""
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """添加CORS头"""
        # 允许的源
        allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', ['http://localhost:3000'])
        origin = request.headers.get('Origin')
        
        if origin in allowed_origins:
            response['Access-Control-Allow-Origin'] = origin
        
        # 允许的方法
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        
        # 允许的头
        response['Access-Control-Allow-Headers'] = (
            'Accept, Accept-Language, Content-Language, Content-Type, '
            'Authorization, X-Request-ID, X-CSRFToken'
        )
        
        # 允许凭证
        response['Access-Control-Allow-Credentials'] = 'true'
        
        # 预检请求缓存时间
        response['Access-Control-Max-Age'] = '86400'
        
        return response
    
    def process_request(self, request: HttpRequest) -> HttpResponse:
        """处理预检请求"""
        if request.method == 'OPTIONS':
            response = HttpResponse()
            return self.process_response(request, response)
        return None


class RateLimitMiddleware(MiddlewareMixin):
    """限流中间件"""
    
    def __init__(self, get_response: Callable = None):
        super().__init__(get_response)
        self.rate_limit_enabled = getattr(settings, 'RATE_LIMIT_ENABLED', True)
        self.rate_limit_requests = getattr(
            settings, 
            'RATE_LIMIT_REQUESTS', 
            RateLimitDefaults.DEFAULT_REQUESTS
        )
        self.rate_limit_window = getattr(
            settings, 
            'RATE_LIMIT_WINDOW', 
            RateLimitDefaults.DEFAULT_WINDOW
        )
    
    def get_client_ip(self, request: HttpRequest) -> str:
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_cache_key(self, request: HttpRequest) -> str:
        """生成缓存键"""
        ip = self.get_client_ip(request)
        return f"rate_limit:{ip}"
    
    def process_request(self, request: HttpRequest) -> HttpResponse:
        """处理限流逻辑"""
        if not self.rate_limit_enabled:
            return None
        
        # 跳过某些路径
        skip_paths = ['/admin/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        cache_key = self.get_cache_key(request)
        current_time = int(time.time())
        window_start = current_time - self.rate_limit_window
        
        # 获取当前窗口内的请求记录
        requests = cache.get(cache_key, [])
        
        # 清理过期的请求记录
        requests = [req_time for req_time in requests if req_time > window_start]
        
        # 检查是否超过限制
        if len(requests) >= self.rate_limit_requests:
            return JsonResponse({
                'code': ApiErrorCode.RATE_LIMIT_EXCEEDED,
                'message': ApiErrorMessage.RATE_LIMIT_EXCEEDED,
                'data': {
                    'limit': self.rate_limit_requests,
                    'window': self.rate_limit_window,
                    'retry_after': self.rate_limit_window
                },
                'timestamp': current_time,
                'request_id': getattr(request, 'request_id', None)
            }, status=429)
        
        # 记录当前请求
        requests.append(current_time)
        cache.set(cache_key, requests, self.rate_limit_window)
        
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """在响应头中添加限流信息"""
        if not self.rate_limit_enabled:
            return response
        
        cache_key = self.get_cache_key(request)
        current_time = int(time.time())
        window_start = current_time - self.rate_limit_window
        
        # 获取当前窗口内的请求记录
        requests = cache.get(cache_key, [])
        requests = [req_time for req_time in requests if req_time > window_start]
        
        # 添加限流头
        response['X-RateLimit-Limit'] = str(self.rate_limit_requests)
        response['X-RateLimit-Remaining'] = str(max(0, self.rate_limit_requests - len(requests)))
        response['X-RateLimit-Reset'] = str(current_time + self.rate_limit_window)
        
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """安全头中间件"""
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """添加安全头"""
        # 防止点击劫持
        response['X-Frame-Options'] = 'DENY'
        
        # 防止MIME类型嗅探
        response['X-Content-Type-Options'] = 'nosniff'
        
        # XSS保护
        response['X-XSS-Protection'] = '1; mode=block'
        
        # 引用策略
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # 内容安全策略（根据需要调整）
        if not response.get('Content-Security-Policy'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none';"
            )
        
        return response