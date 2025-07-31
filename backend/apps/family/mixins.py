"""
Family相关的Mixin类

该文件定义了Family应用中使用的Mixin类。
遵循Django最佳实践和Google Python Style Guide。
"""

from typing import Optional
from apps.family.exceptions import FamilyNotFoundError, FamilyPermissionError
from apps.family.models import Family, FamilyMember

class FamilyPermissionMixin:
    """家庭权限检查Mixin"""

    def check_family_membership(self, user_id: int, family_id: int) -> bool:
        """检查用户是否为家庭成员"""
        try:
            return FamilyMember.objects.filter(
                user_id=user_id,
                family_id=family_id,
                is_active=True
            ).exists()
        except Exception:
            return False

    def get_family_member(self, user_id: int, family_id: int) -> Optional[FamilyMember]:
        """获取家庭成员对象"""
        try:
            return FamilyMember.objects.get(
                user_id=user_id,
                family_id=family_id,
                is_active=True
            )
        except FamilyMember.DoesNotExist:
            return None

class FamilyValidationMixin:
    """家庭验证Mixin"""

    def validate_family_access(self, user_id: int, family_id: int) -> Family:
        """验证用户对家庭的访问权限"""
        try:
            family = Family.objects.get(id=family_id, is_active=True)
        except Family.DoesNotExist:
            raise FamilyNotFoundError(f"Family with id {family_id} not found")

        if not FamilyMember.objects.filter(
            user_id=user_id,
            family_id=family_id,
            is_active=True
        ).exists():
            raise FamilyPermissionError("You don't have permission to access this family")

        return family