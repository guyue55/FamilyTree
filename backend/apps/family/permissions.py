"""
Family权限管理

该文件定义了Family应用的权限管理功能。
遵循Django最佳实践和Google Python Style Guide。
"""

from typing import Optional, List
from django.contrib.auth import get_user_model
from enum import Enum
from loguru import logger
from ninja import Schema
from apps.common.exceptions import PermissionError
from apps.family.models import Family

User = get_user_model()


def raise_permission_denied(message: str = "权限不足"):
    """抛出权限拒绝异常"""
    raise PermissionError(message)


# 延迟导入避免循环依赖
def get_family_membership_model():
    """延迟导入FamilyMembership模型"""
    try:
        from apps.members.models import FamilyMembership

        return FamilyMembership
    except ImportError:
        return None


class FamilyRole(str, Enum):
    """家族角色枚举"""

    OWNER = "owner"  # 族长
    ADMIN = "admin"  # 管理员
    MODERATOR = "moderator"  # 协管员
    MEMBER = "member"  # 普通成员


class FamilyPermission(str, Enum):
    """家族权限枚举"""

    # 家族管理权限
    MANAGE_FAMILY = "manage_family"  # 管理家族基本信息
    DELETE_FAMILY = "delete_family"  # 删除家族
    MANAGE_SETTINGS = "manage_settings"  # 管理家族设置

    # 成员管理权限
    INVITE_MEMBERS = "invite_members"  # 邀请成员
    MANAGE_INVITATIONS = "manage_invitations"  # 管理邀请
    REMOVE_MEMBERS = "remove_members"  # 移除成员
    MANAGE_ROLES = "manage_roles"  # 管理成员角色
    APPROVE_MEMBERS = "approve_members"  # 审批成员申请

    # 内容管理权限
    MANAGE_TREE = "manage_tree"  # 管理族谱树
    ADD_MEMBERS = "add_members"  # 添加族谱成员
    EDIT_MEMBERS = "edit_members"  # 编辑族谱成员
    DELETE_MEMBERS = "delete_members"  # 删除族谱成员
    MANAGE_RELATIONSHIPS = "manage_relationships"  # 管理关系

    # 媒体管理权限
    UPLOAD_MEDIA = "upload_media"  # 上传媒体文件
    MANAGE_MEDIA = "manage_media"  # 管理媒体文件

    # 查看权限
    VIEW_FAMILY = "view_family"  # 查看家族信息
    VIEW_TREE = "view_tree"  # 查看族谱树
    VIEW_MEMBERS = "view_members"  # 查看成员信息


# 角色权限映射
ROLE_PERMISSIONS = {
    FamilyRole.OWNER: [
        # 拥有所有权限
        FamilyPermission.MANAGE_FAMILY,
        FamilyPermission.DELETE_FAMILY,
        FamilyPermission.MANAGE_SETTINGS,
        FamilyPermission.INVITE_MEMBERS,
        FamilyPermission.MANAGE_INVITATIONS,
        FamilyPermission.REMOVE_MEMBERS,
        FamilyPermission.MANAGE_ROLES,
        FamilyPermission.APPROVE_MEMBERS,
        FamilyPermission.MANAGE_TREE,
        FamilyPermission.ADD_MEMBERS,
        FamilyPermission.EDIT_MEMBERS,
        FamilyPermission.DELETE_MEMBERS,
        FamilyPermission.MANAGE_RELATIONSHIPS,
        FamilyPermission.UPLOAD_MEDIA,
        FamilyPermission.MANAGE_MEDIA,
        FamilyPermission.VIEW_FAMILY,
        FamilyPermission.VIEW_TREE,
        FamilyPermission.VIEW_MEMBERS,
    ],
    FamilyRole.ADMIN: [
        # 管理员权限（除了删除家族）
        FamilyPermission.MANAGE_FAMILY,
        FamilyPermission.MANAGE_SETTINGS,
        FamilyPermission.INVITE_MEMBERS,
        FamilyPermission.MANAGE_INVITATIONS,
        FamilyPermission.REMOVE_MEMBERS,
        FamilyPermission.APPROVE_MEMBERS,
        FamilyPermission.MANAGE_TREE,
        FamilyPermission.ADD_MEMBERS,
        FamilyPermission.EDIT_MEMBERS,
        FamilyPermission.DELETE_MEMBERS,
        FamilyPermission.MANAGE_RELATIONSHIPS,
        FamilyPermission.UPLOAD_MEDIA,
        FamilyPermission.MANAGE_MEDIA,
        FamilyPermission.VIEW_FAMILY,
        FamilyPermission.VIEW_TREE,
        FamilyPermission.VIEW_MEMBERS,
    ],
    FamilyRole.MODERATOR: [
        # 协管员权限
        FamilyPermission.INVITE_MEMBERS,
        FamilyPermission.APPROVE_MEMBERS,
        FamilyPermission.ADD_MEMBERS,
        FamilyPermission.EDIT_MEMBERS,
        FamilyPermission.MANAGE_RELATIONSHIPS,
        FamilyPermission.UPLOAD_MEDIA,
        FamilyPermission.VIEW_FAMILY,
        FamilyPermission.VIEW_TREE,
        FamilyPermission.VIEW_MEMBERS,
    ],
    FamilyRole.MEMBER: [
        # 普通成员权限
        FamilyPermission.UPLOAD_MEDIA,
        FamilyPermission.VIEW_FAMILY,
        FamilyPermission.VIEW_TREE,
        FamilyPermission.VIEW_MEMBERS,
    ],
}


class FamilyPermissionChecker:
    """家族权限检查器"""

    def __init__(self, user: User, family: Family):
        self.user = user
        self.family = family
        self._role = None
        self._permissions = None

    @property
    def role(self) -> Optional[FamilyRole]:
        """获取用户在家族中的角色"""
        if self._role is None:
            # 检查是否是家族创建者
            if (
                hasattr(self.family, "created_by_id")
                and self.family.created_by_id == self.user.id
            ):
                self._role = FamilyRole.OWNER
            elif (
                hasattr(self.family, "creator_id")
                and self.family.creator_id == self.user.id
            ):
                self._role = FamilyRole.OWNER
            else:
                # 从成员关系中获取角色
                FamilyMembership = get_family_membership_model()
                if FamilyMembership:
                    try:
                        membership = FamilyMembership.objects.get(
                            family_id=self.family.id,
                            user_id=self.user.id,
                            status="active",
                        )
                        # 根据成员角色映射到权限角色
                        role_mapping = {
                            "admin": FamilyRole.ADMIN,
                            "moderator": FamilyRole.MODERATOR,
                            "member": FamilyRole.MEMBER,
                        }
                        self._role = role_mapping.get(
                            membership.role, FamilyRole.MEMBER
                        )
                    except:
                        # 不是成员，检查是否可以作为访客查看
                        self._role = None
                else:
                    # 如果没有成员模型，只检查创建者
                    self._role = None
        return self._role

    @property
    def permissions(self) -> List[FamilyPermission]:
        """获取用户在家族中的权限列表"""
        if self._permissions is None:
            role = self.role
            if role:
                self._permissions = ROLE_PERMISSIONS.get(role, [])
            else:
                # 检查是否是公开家族的访客权限
                if self.family.visibility == "public":
                    self._permissions = [
                        FamilyPermission.VIEW_FAMILY,
                        FamilyPermission.VIEW_TREE,
                        FamilyPermission.VIEW_MEMBERS,
                    ]
                else:
                    self._permissions = []
        return self._permissions

    def has_permission(self, permission: FamilyPermission) -> bool:
        """检查是否有指定权限"""
        return permission in self.permissions

    def require_permission(self, permission: FamilyPermission, message: str = None):
        """要求指定权限，没有权限则抛出异常"""
        if not self.has_permission(permission):
            error_message = message or f"需要权限: {permission.value}"
            logger.warning(
                f"Permission denied: user_id={self.user.id}, family_id={self.family.id}, permission={permission.value}"
            )
            raise_permission_denied(error_message)

    def is_member(self) -> bool:
        """检查是否是家族成员"""
        return self.role is not None

    def is_admin_or_above(self) -> bool:
        """检查是否是管理员或以上角色"""
        return self.role in [FamilyRole.OWNER, FamilyRole.ADMIN]

    def is_owner(self) -> bool:
        """检查是否是族长"""
        return self.role == FamilyRole.OWNER

    def can_view(self) -> bool:
        """检查是否可以查看家族信息"""
        return self.has_permission(FamilyPermission.VIEW_FAMILY)

    def get_permissions(self) -> List[str]:
        """获取权限列表的字符串形式"""
        return [permission.value for permission in self.permissions]

    def can_manage_member(self, target_user: User) -> bool:
        """检查是否可以管理指定成员"""
        if not self.has_permission(FamilyPermission.MANAGE_ROLES):
            return False

        # 族长可以管理所有人
        if self.is_owner():
            return True

        # 管理员不能管理族长和其他管理员
        if self.role == FamilyRole.ADMIN:
            target_checker = FamilyPermissionChecker(target_user, self.family)
            target_role = target_checker.role
            return target_role not in [FamilyRole.OWNER, FamilyRole.ADMIN]

        return False


def get_family_permission_checker(
    user: User, family_id: int
) -> FamilyPermissionChecker:
    """获取家族权限检查器"""
    try:
        family = Family.objects.get(id=family_id, is_active=True)
        return FamilyPermissionChecker(user, family)
    except Family.DoesNotExist:
        raise PermissionError("家族不存在或已被删除")


def require_family_permission(
    user: User, family_id: int, permission: FamilyPermission, message: str = None
):
    """要求家族权限的装饰器辅助函数"""
    checker = get_family_permission_checker(user, family_id)
    checker.require_permission(permission, message)
    return checker


def check_invitation_permission(user: User, invitation) -> bool:
    """检查邀请权限"""
    # 只有邀请者和被邀请者可以查看邀请
    return user.id in [invitation.inviter_id, invitation.invitee_id]


class PermissionSchema(Schema):
    """权限信息Schema"""

    role: Optional[str]
    permissions: List[str]
    is_member: bool
    is_admin: bool
    is_owner: bool


def get_user_family_permissions(user: User, family: Family) -> PermissionSchema:
    """获取用户在家族中的权限信息"""
    checker = FamilyPermissionChecker(user, family)

    return PermissionSchema(
        role=checker.role.value if checker.role else None,
        permissions=[p.value for p in checker.permissions],
        is_member=checker.is_member(),
        is_admin=checker.is_admin_or_above(),
        is_owner=checker.is_owner(),
    )
