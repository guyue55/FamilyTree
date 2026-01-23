from typing import Dict, Any, Optional
from apps.common.exceptions import BaseApplicationException

"""Family应用异常类

定义家族应用中使用的自定义异常类。
遵循Django Ninja最佳实践和Google Python Style Guide。"""


class FamilyBaseException(BaseApplicationException):
    """家族应用基础异常"""

    def __init__(
        self,
        message: str = "家族操作失败",
        code: str = "FAMILY_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        super().__init__(message, code, details)


class FamilyValidationError(FamilyBaseException):
    """家族验证错误"""


class FamilyNotFoundError(FamilyBaseException):
    """家族不存在错误"""


class FamilyPermissionError(FamilyBaseException):
    """家族权限错误"""


class FamilyMembershipError(FamilyBaseException):
    """家族成员关系错误"""


class FamilyInvitationError(FamilyBaseException):
    """家族邀请错误"""


# 具体业务异常
class FamilyNameConflictError(FamilyValidationError):
    """家族名称冲突"""


class FamilyMemberLimitError(FamilyMembershipError):
    """家族成员数量限制"""


class FamilyInvitationExpiredError(FamilyInvitationError):
    """邀请已过期"""


class FamilyInvitationUsedError(FamilyInvitationError):
    """邀请已使用"""


class FamilyInvitationNotFoundError(FamilyInvitationError):
    """邀请不存在"""


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
