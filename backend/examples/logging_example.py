"""
Django Ninja API 日志使用示例

展示如何在Django Ninja框架中使用loguru和请求ID进行日志追踪。
包含API控制器、服务层、数据访问层的日志记录最佳实践。

设计原则：
- 统一的日志格式和结构
- 完整的请求生命周期追踪
- 性能监控和异常处理
- 安全审计和数据变更记录
"""

from typing import List, Optional
from datetime import datetime

from ninja import Router
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.common.utils.logging import (
    RequestLogger,
    log_function_call,
    log_database_query,
    log_operation,
    log_api_call,
    audit_logger,
)
from apps.common.schemas import StandardResponseSchema
from apps.common.exceptions import BusinessLogicException


# 示例路由器
example_router = Router(tags=["示例API"])


class UserService:
    """
    用户服务层示例

    展示如何在服务层使用日志记录。
    """

    @log_function_call(
        level="info",
        include_args=True,
        exclude_args=["password"],  # 排除敏感信息
    )
    def create_user(self, user_data: dict) -> dict:
        """创建用户"""
        RequestLogger.info("开始创建用户", user_email=user_data.get("email"))

        try:
            with log_operation("用户创建", user_email=user_data.get("email")):
                # 验证用户数据
                self._validate_user_data(user_data)

                # 检查用户是否已存在
                if self._user_exists(user_data["email"]):
                    raise BusinessLogicException("用户已存在")

                # 创建用户
                user = self._create_user_record(user_data)

                # 记录审计日志
                audit_logger.log_user_action(
                    action="create_user",
                    resource="user",
                    resource_id=user["id"],
                    details={"email": user_data.get("email")},
                )

                RequestLogger.info("用户创建成功", user_id=user["id"])
                return user

        except Exception as e:
            RequestLogger.error(
                f"用户创建失败: {str(e)}",
                user_email=user_data.get("email"),
                error_type=type(e).__name__,
            )
            raise

    @log_database_query("select")
    def _user_exists(self, email: str) -> bool:
        """检查用户是否存在"""
        # 模拟数据库查询
        RequestLogger.debug("检查用户是否存在", email=email)
        return False  # 示例返回值

    @log_database_query("insert")
    def _create_user_record(self, user_data: dict) -> dict:
        """创建用户记录"""
        # 模拟数据库插入
        user = {
            "id": 12345,
            "email": user_data["email"],
            "name": user_data["name"],
            "created_at": datetime.now(),
        }

        # 记录数据变更
        audit_logger.log_data_change(
            table="users", operation="insert", record_id=user["id"], new_values=user
        )

        return user

    def _validate_user_data(self, user_data: dict) -> None:
        """验证用户数据"""
        RequestLogger.debug("验证用户数据", fields=list(user_data.keys()))

        required_fields = ["email", "name"]
        for field in required_fields:
            if field not in user_data:
                raise ValidationError(f"缺少必需字段: {field}")


class FamilyService:
    """
    家族服务层示例

    展示复杂业务逻辑的日志记录。
    """

    @log_function_call(level="info", include_args=True, include_result=False)
    def add_family_member(self, family_id: int, member_data: dict) -> dict:
        """添加家族成员"""
        RequestLogger.info(
            "开始添加家族成员", family_id=family_id, member_name=member_data.get("name")
        )

        try:
            with transaction.atomic():
                with log_operation(
                    "添加家族成员",
                    family_id=family_id,
                    member_name=member_data.get("name"),
                ):
                    # 验证家族存在
                    family = self._get_family(family_id)
                    RequestLogger.debug("家族验证通过", family_name=family.get("name"))

                    # 创建成员记录
                    member = self._create_member_record(family_id, member_data)

                    # 更新家族统计
                    self._update_family_stats(family_id)

                    # 记录审计日志
                    audit_logger.log_user_action(
                        action="add_family_member",
                        resource="family_member",
                        resource_id=member["id"],
                        details={
                            "family_id": family_id,
                            "member_name": member_data.get("name"),
                        },
                    )

                    RequestLogger.info(
                        "家族成员添加成功", family_id=family_id, member_id=member["id"]
                    )

                    return member

        except Exception as e:
            RequestLogger.error(
                f"添加家族成员失败: {str(e)}",
                family_id=family_id,
                member_name=member_data.get("name"),
                error_type=type(e).__name__,
            )
            raise

    @log_database_query("select")
    def _get_family(self, family_id: int) -> dict:
        """获取家族信息"""
        # 模拟数据库查询
        return {"id": family_id, "name": "示例家族"}

    @log_database_query("insert")
    def _create_member_record(self, family_id: int, member_data: dict) -> dict:
        """创建成员记录"""
        member = {
            "id": 67890,
            "family_id": family_id,
            "name": member_data["name"],
            "created_at": datetime.now(),
        }

        audit_logger.log_data_change(
            table="family_members",
            operation="insert",
            record_id=member["id"],
            new_values=member,
        )

        return member

    @log_database_query("update")
    def _update_family_stats(self, family_id: int) -> None:
        """更新家族统计"""
        RequestLogger.debug("更新家族统计", family_id=family_id)

        # 模拟统计更新
        audit_logger.log_data_change(
            table="families",
            operation="update",
            record_id=family_id,
            old_values={"member_count": 5},
            new_values={"member_count": 6},
        )


# API控制器示例
@example_router.post("/users", response=StandardResponseSchema)
@log_api_call("创建用户", include_request_data=True, exclude_fields=["password"])
def create_user(request, user_data: dict):
    """
    创建用户API

    展示如何在API层使用日志记录。
    """
    RequestLogger.info("收到创建用户请求", user_email=user_data.get("email"))

    try:
        # 记录安全事件（如果需要）
        if not request.user.is_authenticated:
            audit_logger.log_security_event(
                event_type="anonymous_user_creation",
                severity="info",
                details={"email": user_data.get("email")},
            )

        # 调用服务层
        user_service = UserService()
        user = user_service.create_user(user_data)

        RequestLogger.info(
            "用户创建API成功", user_id=user["id"], user_email=user["email"]
        )

        return StandardResponseSchema(success=True, message="用户创建成功", data=user)

    except BusinessLogicException as e:
        RequestLogger.warning(
            f"业务逻辑异常: {str(e)}", user_email=user_data.get("email")
        )
        return StandardResponseSchema(
            success=False, message=str(e), code="BUSINESS_ERROR"
        )

    except Exception as e:
        RequestLogger.error(
            f"创建用户API失败: {str(e)}",
            user_email=user_data.get("email"),
            error_type=type(e).__name__,
        )
        raise


@example_router.post("/families/{family_id}/members", response=StandardResponseSchema)
@log_api_call("添加家族成员", include_request_data=True)
def add_family_member(request, family_id: int, member_data: dict):
    """
    添加家族成员API

    展示复杂业务逻辑的API日志记录。
    """
    RequestLogger.info(
        "收到添加家族成员请求", family_id=family_id, member_name=member_data.get("name")
    )

    try:
        # 权限检查
        if not request.user.has_perm("family.add_member"):
            audit_logger.log_security_event(
                event_type="unauthorized_family_member_addition",
                severity="warning",
                details={"family_id": family_id, "user_id": request.user.id},
            )
            raise PermissionError("无权限添加家族成员")

        # 调用服务层
        family_service = FamilyService()
        member = family_service.add_family_member(family_id, member_data)

        RequestLogger.info(
            "添加家族成员API成功", family_id=family_id, member_id=member["id"]
        )

        return StandardResponseSchema(
            success=True, message="家族成员添加成功", data=member
        )

    except PermissionError as e:
        RequestLogger.warning(
            f"权限错误: {str(e)}", family_id=family_id, user_id=request.user.id
        )
        return StandardResponseSchema(
            success=False, message="权限不足", code="PERMISSION_DENIED"
        )

    except Exception as e:
        RequestLogger.error(
            f"添加家族成员API失败: {str(e)}",
            family_id=family_id,
            error_type=type(e).__name__,
        )
        raise


@example_router.get("/health")
def health_check(request):
    """
    健康检查API

    展示简单API的日志记录。
    """
    RequestLogger.debug("健康检查请求")

    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# 中间件集成示例
class LoggingMiddleware:
    """
    自定义日志中间件示例

    展示如何在中间件中集成日志记录。
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 请求开始时的日志记录
        RequestLogger.info(
            "API请求开始",
            method=request.method,
            path=request.path,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        # 处理请求
        response = self.get_response(request)

        # 请求结束时的日志记录
        RequestLogger.info(
            "API请求完成",
            method=request.method,
            path=request.path,
            status_code=response.status_code,
        )

        return response


# 异常处理示例
def handle_api_exception(request, exception):
    """
    API异常处理示例

    展示如何在异常处理中使用日志记录。
    """
    RequestLogger.error(
        f"API异常: {type(exception).__name__}: {str(exception)}",
        exception_type=type(exception).__name__,
        exception_message=str(exception),
        method=request.method,
        path=request.path,
    )

    # 记录安全相关异常
    if isinstance(exception, PermissionError):
        audit_logger.log_security_event(
            event_type="permission_denied",
            severity="warning",
            details={
                "path": request.path,
                "user_id": getattr(request.user, "id", None),
            },
        )

    return {"success": False, "message": "服务器内部错误", "code": "INTERNAL_ERROR"}


# 性能监控示例
class PerformanceMonitor:
    """
    性能监控示例

    展示如何监控API性能并记录日志。
    """

    @staticmethod
    def monitor_slow_queries():
        """监控慢查询"""
        # 这里可以集成数据库查询监控
        # 当检测到慢查询时记录日志
        RequestLogger.warning(
            "检测到慢查询", query_time=2.5, query_type="SELECT", table="users"
        )

    @staticmethod
    def monitor_memory_usage():
        """监控内存使用"""
        import psutil

        memory_percent = psutil.virtual_memory().percent

        if memory_percent > 80:
            RequestLogger.warning("内存使用率过高", memory_percent=memory_percent)

    @staticmethod
    def monitor_api_response_time(endpoint: str, duration: float):
        """监控API响应时间"""
        if duration > 1.0:  # 超过1秒的请求
            RequestLogger.warning(
                "API响应时间过长", endpoint=endpoint, duration=duration
            )
        else:
            RequestLogger.debug("API响应时间正常", endpoint=endpoint, duration=duration)
