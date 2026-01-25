"""
Django Ninja API v1 配置

该文件负责创建和配置API v1实例，包括路由注册、异常处理等。
遵循Django Ninja最佳实践和Google Python Style Guide。
"""

from ninja import NinjaAPI

from .api_config import api_config
from .api_docs import create_api_documentation
from apps.common.handlers import register_exception_handlers
from apps.common.schemas import PaginatedApiResponseSchema

# 全局变量存储API实例
_api_v1_instance = None
_api_v1_lock = None
_test_namespace = None


def _get_lock():
    """获取线程锁"""
    global _api_v1_lock
    if _api_v1_lock is None:
        import threading

        _api_v1_lock = threading.Lock()
    return _api_v1_lock


def _get_test_namespace():
    """获取测试环境的唯一命名空间"""
    import os
    import time
    import uuid

    # 每次调用都生成新的命名空间，确保唯一性
    timestamp = int(time.time() * 1000000)  # 微秒级时间戳
    random_id = str(uuid.uuid4())[:8]
    pid = os.getpid()
    return f"api-v1-test-{pid}-{timestamp}-{random_id}"


def create_api_v1() -> NinjaAPI:
    """创建API v1实例"""
    global _api_v1_instance

    # 使用线程锁确保线程安全
    with _get_lock():
        # 如果已经创建过实例，直接返回
        if _api_v1_instance is not None:
            return _api_v1_instance

        # 在测试环境中使用唯一的命名空间
        import os

        namespace = "api-v1"
        if "test" in os.environ.get("DJANGO_SETTINGS_MODULE", "").lower():
            # 使用全局唯一的测试命名空间
            namespace = _get_test_namespace()

        api = NinjaAPI(
            title=api_config.TITLE,
            version=api_config.VERSION,
            description=api_config.DESCRIPTION,
            docs_url="/docs",
            openapi_url="/openapi.json",
            csrf=False,  # 禁用CSRF，使用JWT认证
            urls_namespace=namespace,  # 使用动态命名空间
        )

        # 注册异常处理器
        register_exception_handlers(api)

        # 注册系统健康检查路由
        try:
            from apps.common.health import health_router

            api.add_router("/system", health_router, tags=["System"])
        except (ImportError, Exception):
            pass

        # 注册路由
        try:
            from apps.auth.api import auth_controller

            api.add_router("/auth", auth_controller.router, tags=["Authentication"])
        except (ImportError, Exception):
            pass  # 如果模块不存在，跳过

        try:
            from apps.users.api import user_controller

            api.add_router("/users", user_controller.router, tags=["Users"])
        except (ImportError, Exception):
            pass

        try:
            from apps.family.api import family_controller

            api.add_router("/family", family_controller.router, tags=["Family"])
        except (ImportError, Exception):
            pass

        try:
            from apps.members.api import member_controller

            api.add_router("/members", member_controller.router, tags=["Members"])
        except (ImportError, Exception):
            pass

        try:
            from apps.relationships.api import relationship_controller

            api.add_router(
                "/relationships", relationship_controller.router, tags=["Relationships"]
            )
        except (ImportError, Exception):
            pass

        try:
            from apps.kinship.api import router as kinship_router

            api.add_router("/kinship", kinship_router, tags=["Kinship"])
        except (ImportError, Exception):
            pass

        try:
            from apps.media.api import media_controller

            api.add_router("/media", media_controller.router, tags=["Media"])
        except (ImportError, Exception):
            pass

        # 存储实例
        _api_v1_instance = api

        # 为公开家族搜索添加无认证的直挂路由，确保匿名可访问
        try:
            from ninja import Query
            from apps.family.schemas import (
                PublicFamilyQuerySchema,
                FamilyResponseSchema,
            )
            from apps.family.services import FamilyService
            from apps.common import utils as common_utils

            @api.get(
                "/family/public",
                response=PaginatedApiResponseSchema,
                auth=None,
                tags=["Family"],
            )
            def public_search_families(
                request, query: PublicFamilyQuerySchema = Query(...)
            ):
                filters = query.dict(exclude_unset=True)
                items, total = FamilyService.search_public_families(**filters)
                from apps.members.models import Member

                data = []
                for f in items:
                    obj = FamilyResponseSchema.from_orm(f).dict()
                    qs = Member.objects.filter(family_id=f.id)
                    obj["member_count"] = qs.count()
                    obj["generation_count"] = (
                        qs.order_by("-generation")
                        .values_list("generation", flat=True)
                        .first()
                        or 0
                    )
                    data.append(obj)
                return common_utils.create_paginated_response(
                    data=data,
                    total=total,
                    page=query.page,
                    page_size=query.page_size,
                    message="搜索公开家族成功",
                    request_id=common_utils.get_request_id(request),
                )
        except Exception:
            pass
        return api


def get_api_v1() -> NinjaAPI:
    """获取API v1实例（单例模式）"""
    global _api_v1_instance
    if _api_v1_instance is None:
        _api_v1_instance = create_api_v1()
    return _api_v1_instance


# 不在导入时创建API实例，避免冲突
# api_v1 = get_api_v1()
