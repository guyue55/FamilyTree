"""
统一的JWT认证模块

基于Django Ninja的JWT认证系统，提供完整的认证功能。
遵循Django Ninja最佳实践和安全标准。
"""

import jwt
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.http import HttpRequest
from ninja.security import HttpBearer
from ninja import Schema
from loguru import logger

from .exceptions import AuthenticationError, PermissionError

User = get_user_model()


class JWTAuth(HttpBearer):
    """
    Django Ninja JWT认证类
    
    继承自HttpBearer，实现JWT token验证
    """
    
    def authenticate(self, request: HttpRequest, token: str) -> Optional[User]:
        """
        验证JWT token
        
        Args:
            request: HTTP请求对象
            token: JWT token字符串
            
        Returns:
            用户对象或None
        """
        try:
            # 获取JWT配置
            secret_key = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
            algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')
            
            # 解码JWT token
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            
            # 检查token类型
            if payload.get('type') != 'access':
                logger.warning("Invalid token type")
                return None
            
            # 获取用户
            user_id = payload.get('user_id')
            if not user_id:
                logger.warning("JWT token missing user_id")
                return None
                
            user = User.objects.get(id=user_id, is_active=True)
            
            # 将用户信息添加到请求中
            request.user = user
            return user
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except User.DoesNotExist:
            logger.warning(f"User not found for token user_id: {user_id}")
            return None
        except Exception as e:
            logger.error(f"JWT authentication error: {e}")
            return None


class TokenResponseSchema(Schema):
    """JWT Token响应Schema"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class RefreshTokenSchema(Schema):
    """刷新Token请求Schema"""
    refresh_token: str


def generate_jwt_tokens(user: User) -> Dict[str, Any]:
    """
    生成JWT访问令牌和刷新令牌
    
    Args:
        user: 用户对象
        
    Returns:
        包含访问令牌和刷新令牌的字典
    """
    now = datetime.now()
    
    # 获取JWT配置
    secret_key = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
    algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')
    access_lifetime = getattr(settings, 'JWT_ACCESS_TOKEN_LIFETIME', 3600)  # 1小时
    refresh_lifetime = getattr(settings, 'JWT_REFRESH_TOKEN_LIFETIME', 604800)  # 7天
    
    # 访问令牌payload
    access_payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'iat': now,
        'exp': now + timedelta(seconds=access_lifetime),
        'type': 'access'
    }
    
    # 刷新令牌payload
    refresh_payload = {
        'user_id': user.id,
        'iat': now,
        'exp': now + timedelta(seconds=refresh_lifetime),
        'type': 'refresh'
    }
    
    # 生成令牌
    access_token = jwt.encode(access_payload, secret_key, algorithm=algorithm)
    refresh_token = jwt.encode(refresh_payload, secret_key, algorithm=algorithm)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': access_lifetime
    }


def refresh_access_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    """
    使用刷新令牌生成新的访问令牌
    
    Args:
        refresh_token: 刷新令牌
        
    Returns:
        新的令牌字典或None
    """
    try:
        # 获取JWT配置
        secret_key = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
        algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')
        
        # 解码刷新令牌
        payload = jwt.decode(refresh_token, secret_key, algorithms=[algorithm])
        
        # 检查令牌类型
        if payload.get('type') != 'refresh':
            logger.warning("Invalid token type for refresh")
            return None
        
        # 获取用户
        user_id = payload.get('user_id')
        user = User.objects.get(id=user_id, is_active=True)
        
        # 生成新的令牌
        return generate_jwt_tokens(user)
        
    except jwt.ExpiredSignatureError:
        logger.warning("Refresh token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid refresh token: {e}")
        return None
    except User.DoesNotExist:
        logger.warning(f"User not found for refresh token user_id: {user_id}")
        return None
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return None


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    验证用户凭据
    
    Args:
        username: 用户名或邮箱
        password: 密码
        
    Returns:
        用户对象或None
    """
    try:
        # 尝试用户名认证
        user = authenticate(username=username, password=password)
        if user:
            return user
        
        # 尝试邮箱认证
        try:
            user_by_email = User.objects.get(email=username, is_active=True)
            user = authenticate(username=user_by_email.username, password=password)
            if user:
                return user
        except User.DoesNotExist:
            pass
        
        return None
        
    except Exception as e:
        logger.error(f"User authentication error: {e}")
        return None


def get_current_user(request: HttpRequest) -> User:
    """
    从请求中获取当前认证用户
    
    Args:
        request: HTTP请求对象
        
    Returns:
        用户对象
        
    Raises:
        AuthenticationError: 如果用户未认证
    """
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        raise AuthenticationError("认证失败，请先登录")
    return user


def require_auth(request: HttpRequest) -> User:
    """
    要求认证的装饰器辅助函数
    
    Args:
        request: HTTP请求对象
        
    Returns:
        用户对象
        
    Raises:
        AuthenticationError: 如果用户未认证
    """
    return get_current_user(request)


def require_staff(request: HttpRequest) -> User:
    """
    要求管理员权限的装饰器辅助函数
    
    Args:
        request: HTTP请求对象
        
    Returns:
        用户对象
        
    Raises:
        AuthenticationError: 如果用户未认证
        PermissionError: 如果用户不是管理员
    """
    user = get_current_user(request)
    if not user.is_staff:
        raise PermissionError("需要管理员权限")
    return user


def require_superuser(request: HttpRequest) -> User:
    """
    要求超级用户权限的装饰器辅助函数
    
    Args:
        request: HTTP请求对象
        
    Returns:
        用户对象
        
    Raises:
        AuthenticationError: 如果用户未认证
        PermissionError: 如果用户不是超级用户
    """
    user = get_current_user(request)
    if not user.is_superuser:
        raise PermissionError("需要超级用户权限")
    return user


# 创建全局认证实例
jwt_auth = JWTAuth()


# ==================== 导出 ====================

__all__ = [
    'JWTAuth',
    'jwt_auth',
    'TokenResponseSchema',
    'RefreshTokenSchema',
    'generate_jwt_tokens',
    'refresh_access_token',
    'authenticate_user',
    'get_current_user',
    'require_auth',
    'require_staff',
    'require_superuser'
]