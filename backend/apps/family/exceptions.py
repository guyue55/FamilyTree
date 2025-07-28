"""Family应用异常类

定义家族应用中使用的自定义异常类。
遵循Django Ninja最佳实践和Google Python Style Guide。"""

from typing import Dict, Any, Optional

from apps.common.exceptions import BaseApplicationException


class FamilyBaseException(BaseApplicationException):
    """家族应用基础异常"""
    
    def __init__(self, message: str = "家族操作失败", code: str = "FAMILY_ERROR", 
                 status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, status_code, details)


class FamilyValidationError(FamilyBaseException):
    """家族验证错误"""
    
    def __init__(self, message: str = "家族数据验证失败", field: str = None, 
                 details: Optional[Dict[str, Any]] = None):
        code = "FAMILY_VALIDATION_ERROR"
        if field:
            code = f"FAMILY_VALIDATION_ERROR_{field.upper()}"
        super().__init__(message, code, 400, details)


class FamilyNotFoundError(FamilyBaseException):
    """家族不存在错误"""
    
    def __init__(self, family_id: int = None):
        message = "家族不存在"
        if family_id:
            message = f"家族 {family_id} 不存在"
        super().__init__(message, "FAMILY_NOT_FOUND", 404)


class FamilyPermissionError(FamilyBaseException):
    """家族权限错误"""
    
    def __init__(self, message: str = "没有权限执行此操作", action: str = None):
        code = "FAMILY_PERMISSION_DENIED"
        if action:
            code = f"FAMILY_PERMISSION_DENIED_{action.upper()}"
        super().__init__(message, code, 403)


class FamilyMembershipError(FamilyBaseException):
    """家族成员关系错误"""
    
    def __init__(self, message: str = "家族成员关系错误"):
        super().__init__(message, "FAMILY_MEMBERSHIP_ERROR", 400)


class FamilyInvitationError(FamilyBaseException):
    """家族邀请错误"""
    
    def __init__(self, message: str = "家族邀请操作失败", invitation_code: str = None):
        code = "FAMILY_INVITATION_ERROR"
        if invitation_code:
            message = f"邀请码 {invitation_code} 操作失败: {message}"
        super().__init__(message, code, 400)


# 具体业务异常
class FamilyNameConflictError(FamilyValidationError):
    """家族名称冲突"""
    
    def __init__(self, name: str):
        super().__init__(f"家族名称 '{name}' 已存在", "name")


class FamilyMemberLimitError(FamilyMembershipError):
    """家族成员数量限制"""
    
    def __init__(self, limit: int):
        super().__init__(f"家族成员数量已达到上限 {limit}")


class FamilyInvitationExpiredError(FamilyInvitationError):
    """邀请已过期"""
    
    def __init__(self, invitation_code: str):
        super().__init__("邀请已过期", invitation_code)


class FamilyInvitationUsedError(FamilyInvitationError):
    """邀请已使用"""
    
    def __init__(self, invitation_code: str):
        super().__init__("邀请已被使用", invitation_code)


class FamilyInvitationNotFoundError(FamilyInvitationError):
    """邀请不存在"""
    
    def __init__(self, invitation_code: str):
        super().__init__("邀请不存在", invitation_code)


# 异常处理工具函数
def raise_family_not_found(family_id: int = None):
    """抛出家族不存在异常"""
    raise FamilyNotFoundError(family_id)


def raise_permission_denied(action: str = None):
    """抛出权限拒绝异常"""
    raise FamilyPermissionError(action=action)


def raise_validation_error(message: str, field: str = None):
    """抛出验证错误异常"""
    raise FamilyValidationError(message, field)