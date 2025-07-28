"""
系统健康检查API

提供系统状态检查功能。
遵循Django Ninja框架的API设计规范。
"""

from ninja import Router
from django.http import HttpRequest
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import time
from typing import Dict, Any

from apps.common.schemas import ApiResponseSchema
from apps.common.utils import create_success_response, create_error_response

health_router = Router()


@health_router.get("/health", response=ApiResponseSchema, tags=["System"])
def health_check(request: HttpRequest) -> Dict[str, Any]:
    """
    系统健康检查
    
    检查数据库连接、缓存状态等系统组件。
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": int(time.time()),
            "version": "1.0.0",
            "environment": getattr(settings, 'ENVIRONMENT', 'development'),
            "checks": {}
        }
        
        # 检查数据库连接
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status["checks"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful"
            }
        except Exception as e:
            health_status["checks"]["database"] = {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }
            health_status["status"] = "unhealthy"
        
        # 检查缓存
        try:
            cache_key = "health_check_test"
            cache.set(cache_key, "test", 10)
            cache_value = cache.get(cache_key)
            if cache_value == "test":
                health_status["checks"]["cache"] = {
                    "status": "healthy",
                    "message": "Cache is working"
                }
            else:
                health_status["checks"]["cache"] = {
                    "status": "unhealthy",
                    "message": "Cache test failed"
                }
                health_status["status"] = "unhealthy"
        except Exception as e:
            health_status["checks"]["cache"] = {
                "status": "unhealthy",
                "message": f"Cache error: {str(e)}"
            }
            health_status["status"] = "unhealthy"
        
        return create_success_response(
            data=health_status,
            message="Health check completed"
        )
        
    except Exception as e:
        return create_error_response(
            code=500,
            message="Health check failed",
            data={"error": str(e)}
        )


@health_router.get("/ping", response=ApiResponseSchema, tags=["System"])
def ping(request: HttpRequest) -> Dict[str, Any]:
    """
    简单的ping检查
    
    用于快速检查服务是否可用。
    """
    return create_success_response(
        data={
            "message": "pong",
            "timestamp": int(time.time())
        },
        message="Service is available"
    )


@health_router.get("/version", response=ApiResponseSchema, tags=["System"])
def version_info(request: HttpRequest) -> Dict[str, Any]:
    """
    获取版本信息
    
    返回API版本和系统信息。
    """
    import django
    import sys
    
    version_data = {
        "api_version": "1.0.0",
        "django_version": django.get_version(),
        "python_version": sys.version,
        "environment": getattr(settings, 'ENVIRONMENT', 'development'),
        "debug": settings.DEBUG,
        "timestamp": int(time.time())
    }
    
    return create_success_response(
        data=version_data,
        message="Version information retrieved"
    )