"""
Users应用API接口定义

基于Django Ninja的API接口，提供用户管理相关的所有API服务。
遵循Django Ninja最佳实践和标准化架构设计。

设计原则：
1. 统一的API控制器模式 - 继承StandardCRUDController
2. 标准化的路由注册 - 分离CRUD和自定义路由
3. Schema驱动的数据处理 - 使用Pydantic Schema进行验证和序列化
4. 服务层分离 - 业务逻辑委托给Service层处理
5. 统一的异常处理 - 使用标准化异常类型
6. 一致的响应格式 - 使用通用响应Schema
7. 完整的权限控制 - 基于JWT的身份验证和授权
8. 标准化的日志记录 - 统一的错误日志格式
"""

# ============================================================================
# 导入模块
# ============================================================================

# 标准库导入
from typing import Optional, Dict, Any

# Django框架导入
from django.contrib.auth import get_user_model
from django.http import HttpRequest

# 第三方库导入
from ninja import Router, Query, Path
from loguru import logger

# 公共模块导入
from apps.common.authentication import JWTAuth, get_current_user, require_staff
from apps.common.exceptions import (
    OperationError,
    ValidationError,
    PermissionError,
    NotFoundError
)
from apps.common.schemas import (
    ApiResponseSchema,
    PaginatedApiResponseSchema
)
from apps.common.responses import (
    create_success_response,
    create_paginated_response,
    get_request_id
)
from apps.common.api import StandardCRUDController
from apps.common.utils.logging import RequestLogger, log_api_call, AuditLogger

# 本地应用导入
from .services import UserService
from .schemas import (
    UserCreateSchema,
    UserUpdateSchema,
    UserQuerySchema,
    PasswordChangeSchema,
    UserProfileSchema,
    UserResponseSchema,
    UserProfileResponseSchema
)

User = get_user_model()


# ============================================================================
# 用户管理API控制器
# ============================================================================


class UserController(StandardCRUDController):
    """
    用户API控制器
    
    基于Django Ninja框架的标准化API控制器。
    遵循架构设计原则：
    1. 仅处理HTTP请求和响应
    2. 业务逻辑委托给Service层
    3. 使用Schema进行数据序列化
    4. 统一的异常处理和日志记录
    """
    
    service_class = UserService
    
    # Schema配置
    list_query_schema = UserQuerySchema
    create_schema = UserCreateSchema
    update_schema = UserUpdateSchema
    
    def serialize_object(self, obj, user=None) -> Dict[str, Any]:
        """
        序列化用户对象
        
        Args:
            obj: 用户对象
            user: 当前用户（用于权限控制）
            
        Returns:
            Dict[str, Any]: 序列化后的数据
        """
        return {
            "id": obj.id,
            "username": obj.username,
            "email": obj.email if user and (user.id == obj.id or user.is_staff) else None,
            "phone": obj.phone if user and (user.id == obj.id or user.is_staff) else None,
            "nickname": obj.nickname,
            "gender": obj.gender,
            "birth_date": obj.birth_date.isoformat() if obj.birth_date else None,
            "bio": obj.bio,
            "avatar": obj.avatar,
            "is_verified": obj.is_verified,
            "is_premium": obj.is_premium if user and (user.id == obj.id or user.is_staff) else None,
            "is_active": obj.is_active if user and (user.id == obj.id or user.is_staff) else None,
            "date_joined": obj.date_joined.isoformat() if obj.date_joined else None,
            "last_login": obj.last_login.isoformat() if obj.last_login and user and (user.id == obj.id or user.is_staff) else None,
            "login_count": obj.login_count if user and (user.id == obj.id or user.is_staff) else None,
        }
    
    def __init__(self):
        super().__init__()
        self.router = Router(auth=JWTAuth())
        self.register_routes()
    
    def register_routes(self) -> None:
        """注册所有路由"""
        self.register_crud_routes()
        self.register_custom_routes()
    
    def register_crud_routes(self) -> None:
        """注册标准CRUD路由"""
        
        @self.router.get("/", response=PaginatedApiResponseSchema, tags=["用户管理"], summary="获取用户列表")
        @log_api_call("获取用户列表", include_request_data=True)
        def list_users(request: HttpRequest, query: UserQuerySchema = Query(...)):
            """获取用户列表（管理员功能）"""
            try:
                user = require_staff(request)
                RequestLogger.info("管理员获取用户列表", admin_id=user.id, query_params=query.dict())
                
                # 利用Schema的数据构建过滤条件
                filters = query.dict(exclude_unset=True)
                
                users, total = self.service_class.list_users(user, **filters)
                RequestLogger.info("用户列表查询完成", total_count=total, page=query.page)
                
                # 使用Schema序列化数据
                def serialize_user(user_obj):
                    """序列化用户对象"""
                    return UserResponseSchema.from_orm(user_obj).dict()
                
                data = [serialize_user(user_obj) for user_obj in users]
                
                # 记录审计日志
                AuditLogger.log_user_action(
                    user_id=user.id,
                    action="list_users",
                    resource_type="user",
                    details={"total_count": total, "page": query.page}
                )
                
                return create_paginated_response(
                    data=data,
                    total=total,
                    page=query.page,
                    page_size=query.page_size,
                    message="获取用户列表成功",
                    request_id=get_request_id(request)
                )
                
            except Exception as e:
                RequestLogger.error("获取用户列表失败", error=str(e), admin_id=getattr(user, 'id', None))
                raise OperationError("获取用户列表失败")
        
        @self.router.post("/", response=ApiResponseSchema, tags=["用户管理"], summary="创建用户")
        @log_api_call("创建用户", include_request_data=True, exclude_fields=['password'])
        def create_user(request: HttpRequest, user_data: UserCreateSchema):
            """创建新用户（管理员功能）"""
            try:
                current_user = require_staff(request)
                RequestLogger.info("管理员创建用户", admin_id=current_user.id, target_username=user_data.username)
                
                # 使用Schema的dict方法获取数据
                user = self.service_class.create_user(user_data.dict(), current_user)
                
                # 使用Schema序列化响应数据
                data = UserResponseSchema.from_orm(user).dict()
                
                # 记录审计日志
                AuditLogger.log_user_action(
                    user_id=current_user.id,
                    action="create_user",
                    resource_type="user",
                    resource_id=user.id,
                    details={"created_username": user.username}
                )
                
                RequestLogger.info("用户创建成功", admin_id=current_user.id, created_user_id=user.id)
                
                return create_success_response(
                    data=data,
                    message="创建用户成功",
                    request_id=get_request_id(request)
                )
                
            except (ValidationError, PermissionError) as e:
                RequestLogger.warning("用户创建失败", admin_id=getattr(current_user, 'id', None), error=str(e))
                raise e
            except Exception as e:
                RequestLogger.error("用户创建异常", admin_id=getattr(current_user, 'id', None), error=str(e))
                raise OperationError("创建用户失败")
        
        @self.router.get("/{user_id}", response=ApiResponseSchema, tags=["用户管理"], summary="获取用户详情")
        @log_api_call("获取用户详情")
        def get_user(request: HttpRequest, user_id: int = Path(...)):
            """获取用户详细信息"""
            try:
                current_user = get_current_user(request)
                RequestLogger.info("获取用户详情", current_user_id=current_user.id, target_user_id=user_id)
                
                user = self.service_class.get_user_detail(user_id, current_user)
                
                # 使用Schema序列化响应数据
                data = UserResponseSchema.from_orm(user).dict()
                
                RequestLogger.info("用户详情获取成功", current_user_id=current_user.id, target_user_id=user_id)
                
                return create_success_response(
                    data=data,
                    message="获取用户信息成功",
                    request_id=get_request_id(request)
                )
                
            except (NotFoundError, PermissionError) as e:
                RequestLogger.warning("获取用户详情失败", current_user_id=getattr(current_user, 'id', None), target_user_id=user_id, error=str(e))
                raise e
            except Exception as e:
                RequestLogger.error("获取用户详情异常", current_user_id=getattr(current_user, 'id', None), target_user_id=user_id, error=str(e))
                raise OperationError("获取用户信息失败")
        
        @self.router.put("/{user_id}", response=ApiResponseSchema, tags=["用户管理"], summary="更新用户信息")
        @log_api_call("更新用户信息", include_request_data=True, exclude_fields=['password'])
        def update_user(request: HttpRequest, user_data: UserUpdateSchema, user_id: int = Path(...)):
            """更新用户信息"""
            try:
                current_user = get_current_user(request)
                RequestLogger.info("更新用户信息", current_user_id=current_user.id, target_user_id=user_id)
                
                # 使用Schema的exclude_unset功能，只更新提供的字段
                update_data = user_data.dict(exclude_unset=True)
                user = self.service_class.update_user(user_id, update_data, current_user)
                
                # 使用Schema序列化响应数据
                data = UserResponseSchema.from_orm(user).dict()
                
                # 记录审计日志
                AuditLogger.log_data_change(
                    user_id=current_user.id,
                    action="update_user",
                    resource_type="user",
                    resource_id=user_id,
                    changes=update_data
                )
                
                RequestLogger.info("用户信息更新成功", current_user_id=current_user.id, target_user_id=user_id)
                
                return create_success_response(
                    data=data,
                    message="更新用户信息成功",
                    request_id=get_request_id(request)
                )
                
            except (ValidationError, PermissionError, NotFoundError) as e:
                RequestLogger.warning("更新用户信息失败", current_user_id=getattr(current_user, 'id', None), target_user_id=user_id, error=str(e))
                raise e
            except Exception as e:
                RequestLogger.error("更新用户信息异常", current_user_id=getattr(current_user, 'id', None), target_user_id=user_id, error=str(e))
                raise OperationError("更新用户信息失败")
        
        @self.router.delete("/{user_id}", response=ApiResponseSchema, tags=["用户管理"], summary="删除用户")
        @log_api_call("删除用户")
        def delete_user(request: HttpRequest, user_id: int = Path(...)):
            """删除用户（管理员功能）"""
            try:
                current_user = require_staff(request)
                RequestLogger.info("管理员删除用户", admin_id=current_user.id, target_user_id=user_id)
                
                self.service_class.delete_user(user_id, current_user)
                
                # 记录审计日志
                AuditLogger.log_user_action(
                    user_id=current_user.id,
                    action="delete_user",
                    resource_type="user",
                    resource_id=user_id,
                    details={"deleted_user_id": user_id}
                )
                
                RequestLogger.info("用户删除成功", admin_id=current_user.id, target_user_id=user_id)
                
                return create_success_response(
                    message="删除用户成功",
                    request_id=get_request_id(request)
                )
                
            except (PermissionError, NotFoundError) as e:
                RequestLogger.warning("删除用户失败", admin_id=getattr(current_user, 'id', None), target_user_id=user_id, error=str(e))
                raise e
            except Exception as e:
                RequestLogger.error("删除用户异常", admin_id=getattr(current_user, 'id', None), target_user_id=user_id, error=str(e))
                raise OperationError("删除用户失败")
    
    def register_custom_routes(self) -> None:
        """注册自定义路由"""
        
        @self.router.get("/me", response=ApiResponseSchema, tags=["用户管理"], summary="获取当前用户信息")
        @log_api_call("获取当前用户信息")
        def get_current_user_info(request: HttpRequest):
            """获取当前用户信息"""
            try:
                user = get_current_user(request)
                RequestLogger.info("获取当前用户信息", user_id=user.id)
                
                # 使用Schema序列化响应数据
                data = UserResponseSchema.from_orm(user).dict()
                
                return create_success_response(
                    data=data,
                    message="获取用户信息成功",
                    request_id=get_request_id(request)
                )
                
            except Exception as e:
                RequestLogger.error("获取当前用户信息失败", user_id=getattr(user, 'id', None), error=str(e))
                raise OperationError("获取用户信息失败")
        
        @self.router.put("/me", response=ApiResponseSchema, tags=["用户管理"], summary="更新当前用户信息")
        @log_api_call("更新当前用户信息", include_request_data=True, exclude_fields=['password'])
        def update_current_user(request: HttpRequest, data: UserUpdateSchema):
            """更新当前用户信息"""
            try:
                user = get_current_user(request)
                RequestLogger.info("更新当前用户信息", user_id=user.id)
                
                updated_user = self.service_class.update_user(
                    user.id, data.dict(exclude_unset=True), user
                )
                
                # 使用Schema序列化响应数据
                response_data = UserResponseSchema.from_orm(updated_user).dict()
                
                # 记录审计日志
                AuditLogger.log_data_change(
                    user_id=user.id,
                    action="update_profile",
                    resource_type="user",
                    resource_id=user.id,
                    changes=data.dict(exclude_unset=True)
                )
                
                RequestLogger.info("当前用户信息更新成功", user_id=user.id)
                
                return create_success_response(
                    data=response_data,
                    message="更新用户信息成功",
                    request_id=get_request_id(request)
                )
                
            except (ValidationError, PermissionError) as e:
                RequestLogger.warning("更新当前用户信息失败", user_id=getattr(user, 'id', None), error=str(e))
                raise e
            except Exception as e:
                RequestLogger.error("更新当前用户信息异常", user_id=getattr(user, 'id', None), error=str(e))
                raise OperationError("更新用户信息失败")
        
        @self.router.post("/me/change-password", response=ApiResponseSchema, tags=["用户管理"], summary="修改密码")
        @log_api_call("修改密码", exclude_fields=['old_password', 'new_password'])
        def change_password(request: HttpRequest, data: PasswordChangeSchema):
            """修改当前用户密码"""
            try:
                user = get_current_user(request)
                RequestLogger.info("用户修改密码", user_id=user.id)
                
                self.service_class.change_password(
                    user, data.old_password, data.new_password
                )
                
                # 记录安全审计日志
                AuditLogger.log_security_event(
                    user_id=user.id,
                    event_type="password_change",
                    details={"user_id": user.id}
                )
                
                RequestLogger.info("密码修改成功", user_id=user.id)
                
                return create_success_response(
                    message="密码修改成功",
                    request_id=get_request_id(request)
                )
                
            except (ValidationError, PermissionError) as e:
                RequestLogger.warning("密码修改失败", user_id=getattr(user, 'id', None), error=str(e))
                raise e
            except Exception as e:
                RequestLogger.error("密码修改异常", user_id=getattr(user, 'id', None), error=str(e))
                raise OperationError("密码修改失败")

        @self.router.get("/me/profile", response=ApiResponseSchema, tags=["用户配置"], summary="获取用户配置")
        @log_api_call("获取用户配置")
        def get_user_profile(request: HttpRequest):
            """获取当前用户配置"""
            try:
                user = get_current_user(request)
                RequestLogger.info("获取用户配置", user_id=user.id)
                
                profile = self.service_class.get_user_profile(user)
                
                # 使用Schema序列化响应数据
                data = UserProfileResponseSchema.from_orm(profile).dict()
                
                return create_success_response(
                    data=data,
                    message="获取用户配置成功",
                    request_id=get_request_id(request)
                )
                
            except Exception as e:
                RequestLogger.error("获取用户配置失败", user_id=getattr(user, 'id', None), error=str(e))
                raise OperationError("获取用户配置失败")
        
        @self.router.put("/me/profile", response=ApiResponseSchema, tags=["用户配置"], summary="更新用户配置")
        @log_api_call("更新用户配置", include_request_data=True)
        def update_user_profile(request: HttpRequest, data: UserProfileSchema):
            """更新当前用户配置"""
            try:
                user = get_current_user(request)
                RequestLogger.info("更新用户配置", user_id=user.id)
                
                profile = self.service_class.update_user_profile(
                    user, data.dict(exclude_unset=True)
                )
                
                # 使用Schema序列化响应数据
                response_data = UserProfileResponseSchema.from_orm(profile).dict()
                
                # 记录审计日志
                AuditLogger.log_data_change(
                    user_id=user.id,
                    action="update_profile_settings",
                    resource_type="user_profile",
                    resource_id=user.id,
                    changes=data.dict(exclude_unset=True)
                )
                
                RequestLogger.info("用户配置更新成功", user_id=user.id)
                
                return create_success_response(
                    data=response_data,
                    message="更新用户配置成功",
                    request_id=get_request_id(request)
                )
                
            except (ValidationError, PermissionError) as e:
                RequestLogger.warning("更新用户配置失败", user_id=getattr(user, 'id', None), error=str(e))
                raise e
            except Exception as e:
                RequestLogger.error("更新用户配置异常", user_id=getattr(user, 'id', None), error=str(e))
                raise OperationError("更新用户配置失败")


# ============================================================================
# 导出
# ============================================================================

user_controller = UserController()
router = user_controller.router
users_router = router  # 为了兼容性添加别名

__all__ = [
    "UserController",
    "user_controller",
    "router",
    "users_router"
]