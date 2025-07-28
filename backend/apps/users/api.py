"""
用户管理API接口

基于Django Ninja的用户管理API接口。
专注于用户信息管理、权限控制和用户配置功能。
认证功能已迁移到 apps.auth 模块。
"""

from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from ninja import Router, Query, Path
from loguru import logger

from apps.common.api import StandardCRUDController
from apps.common.schemas import (
    ApiResponseSchema, PaginatedApiResponseSchema, SuccessResponseSchema
)
from apps.common.utils import (
    create_success_response, create_paginated_response, 
    get_request_id
)
from apps.common.authentication import get_current_user, require_staff
from apps.common.exceptions import (
    ValidationError, PermissionError, NotFoundError, OperationError
)
from .schemas import (
    UserCreateSchema, UserUpdateSchema, UserResponseSchema,
    UserQuerySchema, PasswordChangeSchema, UserProfileSchema, 
    UserProfileResponseSchema
)
from .services import UserService

User = get_user_model()


class UserController(StandardCRUDController):
    """
    用户管理API控制器
    
    提供用户信息管理、权限控制和用户配置相关的API接口。
    不包含认证功能（认证功能在 apps.auth 模块中）。
    """
    
    service_class = UserService
    
    def __init__(self):
        super().__init__()
        self.service = self.service_class()
    
    def serialize_object(self, obj: User, user: User = None) -> Dict[str, Any]:
        """
        序列化用户对象
        
        Args:
            obj: 用户对象
            user: 当前用户（用于权限控制）
            
        Returns:
            Dict[str, Any]: 序列化后的数据
        """
        # 基础信息（所有用户都可以看到）
        data = {
            "id": obj.id,
            "username": obj.username,
            "nickname": obj.nickname,
            "avatar": obj.avatar,
            "is_verified": obj.is_verified,
            "date_joined": obj.date_joined.isoformat(),
        }
        
        # 详细信息（仅本人或管理员可见）
        if user and (user.id == obj.id or user.is_staff):
            data.update({
                "email": obj.email,
                "phone": obj.phone,
                "gender": obj.gender,
                "birth_date": obj.birth_date.isoformat() if obj.birth_date else None,
                "bio": obj.bio,
                "is_premium": obj.is_premium,
                "is_active": obj.is_active,
                "last_login": obj.last_login.isoformat() if obj.last_login else None,
                "login_count": obj.login_count
            })
        
        return data
    
    def register_routes(self) -> None:
        """注册所有路由"""
        self.register_user_routes()
        self.register_profile_routes()
        self.register_admin_routes()
    
    
    def register_user_routes(self) -> None:
        """注册用户基本管理路由"""
        
        @self.router.get("/me", response=ApiResponseSchema, summary="获取当前用户信息")
        def get_current_user_info(request: HttpRequest):
            """获取当前用户信息"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)
                
                return create_success_response(
                    data=self.serialize_object(user, user),
                    message="获取用户信息成功",
                    request_id=request_id
                )
                
            except Exception as e:
                logger.error(f"Get current user error: {e}")
                raise OperationError("获取用户信息失败")
        
        @self.router.put("/me", response=ApiResponseSchema, summary="更新当前用户信息")
        def update_current_user(request: HttpRequest, data: UserUpdateSchema):
            """更新当前用户信息"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)
                
                updated_user = self.service.update_user(
                    user.id, data.dict(exclude_unset=True), user
                )
                
                return create_success_response(
                    data=self.serialize_object(updated_user, user),
                    message="更新用户信息成功",
                    request_id=request_id
                )
                
            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Update current user error: {e}")
                raise OperationError("更新用户信息失败")
        
        @self.router.post("/me/change-password", response=SuccessResponseSchema, summary="修改密码")
        def change_password(request: HttpRequest, data: PasswordChangeSchema):
            """修改当前用户密码"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)
                
                self.service.change_password(
                    user, data.old_password, data.new_password
                )
                
                return create_success_response(
                    message="密码修改成功",
                    request_id=request_id
                )
                
            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Change password error: {e}")
                raise OperationError("密码修改失败")
        
        @self.router.get("/{user_id}", response=ApiResponseSchema, summary="获取指定用户信息")
        def get_user_by_id(request: HttpRequest, user_id: int = Path(...)):
            """获取指定用户的公开信息"""
            try:
                current_user = get_current_user(request)
                request_id = get_request_id(request)
                
                user = self.service.get_user_by_id(user_id)
                if not user:
                    raise NotFoundError("用户不存在")
                
                return create_success_response(
                    data=self.serialize_object(user, current_user),
                    message="获取用户信息成功",
                    request_id=request_id
                )
                
            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get user by id error: {e}")
                raise OperationError("获取用户信息失败")
    
    def register_admin_routes(self) -> None:
        """注册管理员路由"""
        
        @self.router.get("/", response=PaginatedApiResponseSchema, summary="获取用户列表")
        def list_users(request: HttpRequest, query: UserQuerySchema = Query(...)):
            """获取用户列表（管理员功能）"""
            try:
                user = require_staff(request)  # 使用统一的权限检查
                request_id = get_request_id(request)
                
                filters = {
                    'keyword': query.search,
                    'is_active': query.is_active,
                    'is_verified': query.is_verified,
                    'ordering': query.ordering,
                    'page': query.page,
                    'page_size': query.page_size
                }
                
                users, total = self.service.list_users(**filters)
                
                data = [self.serialize_object(u, user) for u in users]
                
                return create_paginated_response(
                    data=data,
                    total=total,
                    page=query.page,
                    page_size=query.page_size,
                    message="获取用户列表成功",
                    request_id=request_id
                )
                
            except (PermissionError, ValidationError) as e:
                raise e
            except Exception as e:
                logger.error(f"List users error: {e}")
                raise OperationError("获取用户列表失败")
        
        @self.router.put("/{user_id}", response=ApiResponseSchema, summary="更新指定用户信息")
        def update_user_by_id(request: HttpRequest, user_id: int = Path(...), data: UserUpdateSchema = None):
            """更新指定用户信息（管理员功能）"""
            try:
                admin_user = require_staff(request)
                request_id = get_request_id(request)
                
                updated_user = self.service.update_user(
                    user_id, data.dict(exclude_unset=True), admin_user
                )
                
                return create_success_response(
                    data=self.serialize_object(updated_user, admin_user),
                    message="更新用户信息成功",
                    request_id=request_id
                )
                
            except (ValidationError, PermissionError, NotFoundError) as e:
                raise e
            except Exception as e:
                logger.error(f"Update user by id error: {e}")
                raise OperationError("更新用户信息失败")
        
        @self.router.delete("/{user_id}", response=SuccessResponseSchema, summary="删除用户")
        def delete_user(request: HttpRequest, user_id: int = Path(...)):
            """删除用户（管理员功能）"""
            try:
                admin_user = require_staff(request)
                request_id = get_request_id(request)
                
                self.service.delete_user(user_id, admin_user)
                
                return create_success_response(
                    message="删除用户成功",
                    request_id=request_id
                )
                
            except (PermissionError, NotFoundError) as e:
                raise e
            except Exception as e:
                logger.error(f"Delete user error: {e}")
                raise OperationError("删除用户失败")
    
    def register_profile_routes(self) -> None:
        """注册用户配置路由"""
        
        @self.router.get("/me/profile", response=ApiResponseSchema, summary="获取用户配置")
        def get_user_profile(request: HttpRequest):
            """获取用户配置"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)
                
                profile = self.service.get_user_profile(user)
                
                data = {
                    "id": profile.id,
                    "user_id": profile.user_id,
                    "privacy_level": profile.privacy_level,
                    "email_notifications": profile.email_notifications,
                    "sms_notifications": profile.sms_notifications,
                    "theme": profile.theme,
                    "language": profile.language,
                    "auto_save": profile.auto_save,
                    "show_tips": profile.show_tips,
                    "created_at": profile.created_at.isoformat(),
                    "updated_at": profile.updated_at.isoformat()
                }
                
                return create_success_response(
                    data=data,
                    message="获取用户配置成功",
                    request_id=request_id
                )
                
            except Exception as e:
                logger.error(f"Get user profile error: {e}")
                raise OperationError("获取用户配置失败")
        
        @self.router.put("/me/profile", response=ApiResponseSchema, summary="更新用户配置")
        def update_user_profile(request: HttpRequest, data: UserProfileSchema):
            """更新用户配置"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)
                
                profile = self.service.update_user_profile(
                    user, data.dict(exclude_unset=True)
                )
                
                data = {
                    "id": profile.id,
                    "user_id": profile.user_id,
                    "privacy_level": profile.privacy_level,
                    "email_notifications": profile.email_notifications,
                    "sms_notifications": profile.sms_notifications,
                    "theme": profile.theme,
                    "language": profile.language,
                    "auto_save": profile.auto_save,
                    "show_tips": profile.show_tips,
                    "created_at": profile.created_at.isoformat(),
                    "updated_at": profile.updated_at.isoformat()
                }
                
                return create_success_response(
                    data=data,
                    message="更新用户配置成功",
                    request_id=request_id
                )
                
            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Update user profile error: {e}")
                raise OperationError("更新用户配置失败")


# 创建控制器实例
user_controller = UserController()
router = user_controller.router


# ==================== 导出 ====================

__all__ = [
    'UserController',
    'router',
    'UserCreateSchema',
    'UserUpdateSchema',
    'UserQuerySchema',
    'PasswordChangeSchema',
    'UserProfileSchema'
]