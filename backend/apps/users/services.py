"""
用户模块服务层

提供用户管理相关的业务逻辑处理。
遵循Django最佳实践和Google Python Style Guide。
"""

from typing import Dict, Any, List, Optional, Tuple
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils import timezone
from loguru import logger

from apps.common.services import BaseService, CacheableService
from apps.common.exceptions import (
    ValidationError, PermissionError, NotFoundError, OperationError
)
from .models import UserProfile

User = get_user_model()


class UserService(BaseService, CacheableService):
    """
    用户服务类
    
    提供用户管理相关的所有业务逻辑，包括用户认证、信息管理、配置管理等。
    """
    
    model = User
    
    def get_search_fields(self) -> List[str]:
        """定义可搜索的字段"""
        return ['username', 'email', 'phone', 'nickname']
    
    def validate_create_data(self, data: Dict[str, Any], user=None) -> Dict[str, Any]:
        """验证用户创建数据"""
        # 检查用户名是否已存在
        if User.objects.filter(username=data.get('username')).exists():
            raise ValidationError("用户名已存在")
        
        # 检查邮箱是否已存在
        if data.get('email') and User.objects.filter(email=data.get('email')).exists():
            raise ValidationError("邮箱已存在")
        
        # 检查手机号是否已存在
        if data.get('phone') and User.objects.filter(phone=data.get('phone')).exists():
            raise ValidationError("手机号已存在")
        
        return data
    
    def validate_update_data(self, obj, data: Dict[str, Any], user=None) -> Dict[str, Any]:
        """验证用户更新数据"""
        # 检查邮箱是否被其他用户使用
        if data.get('email') and User.objects.filter(
            email=data.get('email')
        ).exclude(id=obj.id).exists():
            raise ValidationError("邮箱已被其他用户使用")
        
        # 检查手机号是否被其他用户使用
        if data.get('phone') and User.objects.filter(
            phone=data.get('phone')
        ).exclude(id=obj.id).exists():
            raise ValidationError("手机号已被其他用户使用")
        
        return data
    
    def check_permissions(self, obj, user, action: str) -> bool:
        """检查用户权限"""
        if action in ['view', 'update']:
            # 用户只能查看和修改自己的信息，或者管理员可以操作所有用户
            return obj.id == user.id or user.is_staff
        elif action in ['delete']:
            # 只有管理员可以删除用户
            return user.is_staff
        return False
    
    @transaction.atomic
    def create_user(self, data: Dict[str, Any]) -> User:
        """创建用户"""
        try:
            # 验证数据
            validated_data = self.validate_create_data(data)
            
            # 提取密码
            password = validated_data.pop('password', None)
            if not password:
                raise ValidationError("密码不能为空")
            
            # 创建用户
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data.get('email'),
                password=password,
                **{k: v for k, v in validated_data.items() 
                   if k not in ['username', 'email', 'password']}
            )
            
            # 创建用户配置
            UserProfile.objects.create(user=user)
            
            logger.info(f"User created: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"Create user error: {e}")
            raise OperationError("创建用户失败")
    
    def logout_user(self, user: User) -> None:
        """用户登出"""
        try:
            # 这里可以添加token失效逻辑
            # 例如将token加入黑名单等
            logger.info(f"User logged out: {user.username}")
            
        except Exception as e:
            logger.error(f"Logout user error: {e}")
            raise OperationError("登出失败")
    
    def change_password(self, user: User, old_password: str, new_password: str) -> None:
        """修改密码"""
        try:
            if not check_password(old_password, user.password):
                raise ValidationError("原密码错误")
            
            user.set_password(new_password)
            user.save(update_fields=['password'])
            
            logger.info(f"Password changed for user: {user.username}")
            
        except ValidationError as e:
            raise e
        except Exception as e:
            logger.error(f"Change password error: {e}")
            raise OperationError("修改密码失败")
    
    def list_users(self, keyword: str = None, is_active: bool = None, 
                   is_verified: bool = None, ordering: str = None,
                   page: int = 1, page_size: int = 20) -> Tuple[List[User], int]:
        """获取用户列表"""
        try:
            queryset = self.get_queryset()
            
            # 搜索过滤
            if keyword:
                search_q = Q()
                for field in self.get_search_fields():
                    search_q |= Q(**{f"{field}__icontains": keyword})
                queryset = queryset.filter(search_q)
            
            # 状态过滤
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active)
            
            if is_verified is not None:
                queryset = queryset.filter(is_verified=is_verified)
            
            # 排序
            if ordering:
                queryset = queryset.order_by(ordering)
            else:
                queryset = queryset.order_by('-date_joined')
            
            # 分页
            total = queryset.count()
            start = (page - 1) * page_size
            end = start + page_size
            users = list(queryset[start:end])
            
            return users, total
            
        except Exception as e:
            logger.error(f"List users error: {e}")
            raise OperationError("获取用户列表失败")
    
    def get_user_profile(self, user: User) -> UserProfile:
        """获取用户配置"""
        try:
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                logger.info(f"User profile created for: {user.username}")
            return profile
            
        except Exception as e:
            logger.error(f"Get user profile error: {e}")
            raise OperationError("获取用户配置失败")
    
    def update_user_profile(self, user: User, data: Dict[str, Any]) -> UserProfile:
        """更新用户配置"""
        try:
            profile = self.get_user_profile(user)
            
            for key, value in data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            profile.save()
            
            logger.info(f"User profile updated for: {user.username}")
            return profile
            
        except Exception as e:
            logger.error(f"Update user profile error: {e}")
            raise OperationError("更新用户配置失败")


# ==================== 导出 ====================

__all__ = [
    'UserService'
]