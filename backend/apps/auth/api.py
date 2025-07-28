"""认证API接口

基于Django Ninja的认证系统API接口。
提供用户注册、登录、令牌刷新等核心认证功能。
遵循Django Ninja最佳实践和RESTful API设计原则。
"""

from typing import Optional
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from ninja import Router, Schema
from loguru import logger

from apps.common.exceptions import ValidationError, AuthenticationError, OperationError
from apps.common.schemas import SuccessResponseSchema, ApiResponseSchema
from apps.common.utils import get_request_id, create_success_response
from apps.common.authentication import (
    generate_jwt_tokens,
    refresh_access_token,
    authenticate_user,
    TokenResponseSchema,
    RefreshTokenSchema,
    get_current_user
)

User = get_user_model()


# ==================== Schemas ====================

class UserRegisterSchema(Schema):
    """用户注册请求Schema"""
    username: str
    email: str
    password: str
    confirm_password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLoginSchema(Schema):
    """用户登录请求Schema"""
    username: str
    password: str
    remember_me: bool = False


class UserInfoSchema(Schema):
    """用户基本信息Schema"""
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    date_joined: str


class LoginResponseSchema(Schema):
    """登录成功响应Schema"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserInfoSchema


class RegisterResponseSchema(Schema):
    """注册成功响应Schema"""
    user: UserInfoSchema
    message: str


# ==================== Router ====================

# 创建认证路由器
auth_router = Router(tags=["认证"])


# ==================== API Endpoints ====================

@auth_router.post("/register", response=RegisterResponseSchema, summary="用户注册")
def register(request: HttpRequest, data: UserRegisterSchema):
    """
    用户注册
    
    创建新用户账户，包含基本信息验证和密码加密。
    """
    try:
        # 验证密码确认
        if data.password != data.confirm_password:
            raise ValidationError("密码确认不匹配")
        
        # 检查用户名是否已存在
        if User.objects.filter(username=data.username).exists():
            raise ValidationError("用户名已存在")
        
        # 检查邮箱是否已存在
        if User.objects.filter(email=data.email).exists():
            raise ValidationError("邮箱已被注册")
        
        # 创建用户
        with transaction.atomic():
            user = User.objects.create(
                username=data.username,
                email=data.email,
                password=make_password(data.password),
                first_name=data.first_name or "",
                last_name=data.last_name or "",
                is_active=True
            )
        
        # 序列化用户信息
        user_info = UserInfoSchema(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            date_joined=user.date_joined.isoformat()
        )
        
        return RegisterResponseSchema(
            user=user_info,
            message="注册成功"
        )
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"User registration error: {e}")
        raise OperationError("注册失败，请稍后重试")


@auth_router.post("/login", response=LoginResponseSchema, summary="用户登录")
def login(request: HttpRequest, data: UserLoginSchema):
    """
    用户登录
    
    验证用户凭据并返回JWT令牌。
    """
    try:
        # 验证用户凭据
        user = authenticate_user(data.username, data.password)
        if not user:
            raise AuthenticationError("用户名或密码错误")
        
        if not user.is_active:
            raise AuthenticationError("账户已被禁用")
        
        # 生成JWT令牌
        tokens = generate_jwt_tokens(user)
        
        # 序列化用户信息
        user_info = UserInfoSchema(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            date_joined=user.date_joined.isoformat()
        )
        
        return LoginResponseSchema(
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            token_type=tokens['token_type'],
            expires_in=tokens['expires_in'],
            user=user_info
        )
        
    except (ValidationError, AuthenticationError):
        raise
    except Exception as e:
        logger.error(f"User login error: {e}")
        raise OperationError("登录失败，请稍后重试")


@auth_router.post("/refresh", response=TokenResponseSchema, summary="刷新访问令牌")
def refresh_token(request: HttpRequest, data: RefreshTokenSchema):
    """
    刷新访问令牌
    
    使用刷新令牌获取新的访问令牌。
    """
    try:
        # 刷新令牌
        tokens = refresh_access_token(data.refresh_token)
        if not tokens:
            raise AuthenticationError("刷新令牌无效或已过期")
        
        return TokenResponseSchema(**tokens)
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise OperationError("令牌刷新失败")


@auth_router.post("/logout", response=SuccessResponseSchema, summary="用户登出")
def logout(request: HttpRequest):
    """
    用户登出
    
    注销当前用户会话。
    注意：由于使用JWT，实际的令牌失效需要在客户端处理。
    """
    try:
        # 验证用户认证状态
        user = get_current_user(request)
        request_id = get_request_id(request)
        
        logger.info(f"User {user.username} logged out")
        
        return create_success_response(
            message="登出成功",
            request_id=request_id
        )
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"User logout error: {e}")
        raise OperationError("登出失败")


@auth_router.get("/me", response=ApiResponseSchema, summary="获取当前用户信息")
def get_current_user_info(request: HttpRequest):
    """
    获取当前认证用户的基本信息
    """
    try:
        user = get_current_user(request)
        request_id = get_request_id(request)
        
        user_info = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "date_joined": user.date_joined.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
        return create_success_response(
            data=user_info,
            message="获取用户信息成功",
            request_id=request_id
        )
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise OperationError("获取用户信息失败")


# 导出路由
router = auth_router


# ==================== 导出 ====================

__all__ = [
    'auth_router',
    'router',
    'UserRegisterSchema',
    'UserLoginSchema',
    'UserInfoSchema',
    'LoginResponseSchema',
    'RegisterResponseSchema'
]