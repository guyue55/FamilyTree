"""
通用Mixin类

提供基础的Mixin类，专为Django Ninja API设计。
遵循Django最佳实践和Google Python Style Guide。
"""

from typing import Any, Dict
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest


class PermissionMixin:
    """权限Mixin - 适配Django Ninja API"""
    
    required_permissions: list = []
    permission_denied_message: str = "您没有执行此操作的权限"
    
    def check_permissions(self, request: HttpRequest) -> bool:
        """检查权限"""
        if not self.required_permissions:
            return True
        
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        
        return user.has_perms(self.required_permissions)
    
    def handle_no_permission(self):
        """处理无权限情况"""
        raise PermissionDenied(self.permission_denied_message)


class ValidationMixin:
    """验证Mixin"""
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> Dict[str, list]:
        """验证必填字段"""
        errors = {}
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                errors.setdefault(field, []).append(f"{field}是必填字段")
        
        return errors
    
    def validate_field_length(self, data: Dict[str, Any], field_limits: Dict[str, Dict[str, int]]) -> Dict[str, list]:
        """验证字段长度"""
        errors = {}
        
        for field, limits in field_limits.items():
            if field in data and data[field] is not None:
                value = str(data[field])
                min_length = limits.get('min', 0)
                max_length = limits.get('max', float('inf'))
                
                if len(value) < min_length:
                    errors.setdefault(field, []).append(f"{field}长度不能少于{min_length}个字符")
                
                if len(value) > max_length:
                    errors.setdefault(field, []).append(f"{field}长度不能超过{max_length}个字符")
        
        return errors