"""
API v1 路由配置

统一管理API版本和路由。
遵循Django Ninja最佳实践。
"""

from ninja import NinjaAPI
from apps.common.handlers import register_exception_handlers
from .api_config import api_config
from .api_docs import create_api_documentation


def create_api_v1() -> NinjaAPI:
    """创建API v1实例"""
    api = NinjaAPI(
        title=api_config.TITLE,
        version=api_config.VERSION,
        description=api_config.DESCRIPTION,
        docs_url="/docs",
        openapi_url="/openapi.json",
        csrf=False,  # 禁用CSRF，使用JWT认证
    )
    
    # 注册异常处理器
    register_exception_handlers(api)
    
    # 创建API文档生成器
    doc_generator = create_api_documentation(api)
    
    # 注册系统健康检查路由
    try:
        from apps.common.health import health_router
        api.add_router("/system", health_router, tags=["System"])
    except ImportError:
        pass
    
    # 注册路由
    try:
        from apps.auth.api import auth_router
        api.add_router("/auth", auth_router, tags=["Authentication"])
    except ImportError:
        pass  # 如果模块不存在，跳过
    
    try:
        from apps.users.api import router as users_router
        api.add_router("/users", users_router, tags=["Users"])
    except ImportError:
        pass
    
    try:
        from apps.family.api import router as family_router
        api.add_router("/family", family_router, tags=["Family"])
    except ImportError:
        pass
    
    try:
        from apps.members.api import router as members_router
        api.add_router("/members", members_router, tags=["Members"])
    except ImportError:
        pass
    
    try:
        from apps.relationships.api import router as relationships_router
        api.add_router("/relationships", relationships_router, tags=["Relationships"])
    except ImportError:
        pass
    
    try:
        from apps.media.api import router as media_router
        api.add_router("/media", media_router, tags=["Media"])
    except ImportError:
        pass
    
    return api


# 创建API实例
api_v1 = create_api_v1()