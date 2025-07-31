"""
Family应用工具类

提供家族应用中使用的核心工具函数，包括验证、格式化、生成等功能。
遵循Django Ninja最佳实践和Google Python Style Guide。
"""

import re
import secrets
import string
from datetime import datetime
from typing import Tuple, List
from urllib.parse import urljoin
from django.conf import settings
from django.utils import timezone
from .constants import (
    INVITATION_CODE_LENGTH,
    ERROR_MESSAGES,
    ROLE_WEIGHTS
)

class FamilyCodeGenerator:
    """家族相关代码生成器"""

    @staticmethod
    def generate_invitation_code() -> str:
        """
        生成邀请码

        Returns:
            str: 32位邀请码
        """

        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(INVITATION_CODE_LENGTH))

    @staticmethod
    def generate_family_slug(name: str) -> str:
        """
        生成家族slug

        Args:
            name: 家族名称

        Returns:
            str: 家族slug
        """

        # 清理名称
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)

        # 添加随机后缀
        suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        return f"{slug}-{suffix}"

class FamilyValidator:
    """家族相关验证器"""

    @staticmethod
    def validate_family_name(name: str) -> bool:
        """
        验证家族名称

        Args:
            name: 家族名称

        Returns:
            bool: 是否有效
        """
        if not name or not isinstance(name, str):
            return False

        name = name.strip()
        return 2 <= len(name) <= 100

    @staticmethod
    def validate_email_or_phone(contact: str) -> Tuple[bool, str]:
        """
        验证邮箱或手机号

        Args:
            contact: 联系方式

        Returns:
            Tuple[bool, str]: (是否有效, 类型)
        """

        if not contact or not isinstance(contact, str):
            return False, 'invalid'

        contact = contact.strip()

        # 邮箱验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, contact):
            return True, 'email'

        # 手机号验证（简单版本）
        phone_pattern = r'^1[3-9]\d{9}$'
        if re.match(phone_pattern, contact):
            return True, 'phone'

        return False, 'invalid'

    @staticmethod
    def validate_invitation_code(code: str) -> bool:
        """
        验证邀请码格式

        Args:
            code: 邀请码

        Returns:
            bool: 是否有效
        """
        if not code or not isinstance(code, str):
            return False

        return len(code) == INVITATION_CODE_LENGTH and code.isalnum()

class FamilyFormatter:
    """家族相关格式化器"""

    @staticmethod
    def format_member_count(count: int) -> str:
        """
        格式化成员数量

        Args:
            count: 成员数量

        Returns:
            str: 格式化后的数量
        """
        if count < 1000:
            return str(count)
        elif count < 1000000:
            return f"{count / 1000:.1f}K"
        else:
            return f"{count / 1000000:.1f}M"

    @staticmethod
    def format_time_ago(dt: datetime) -> str:
        """
        格式化时间差

        Args:
            dt: 时间

        Returns:
            str: 时间差描述
        """
        now = timezone.now()
        diff = now - dt

        if diff.days > 365:
            years = diff.days // 365
            return f"{years}年前"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months}个月前"
        elif diff.days > 0:
            return f"{diff.days}天前"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}小时前"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"

    @staticmethod
    def format_privacy_level(level: str) -> str:
        """
        格式化隐私级别

        Args:
            level: 隐私级别

        Returns:
            str: 格式化后的级别
        """
        level_map = {
            'public': '🌍 公开',
            'members': '👥 成员可见',
            'family': '🏠 家族可见',
            'private': '🔒 私有',
        }
        return level_map.get(level, level)

class FamilyUrlBuilder:
    """家族URL构建器"""

    @staticmethod
    def build_family_url(family_id: int, path: str = '') -> str:
        """
        构建家族URL

        Args:
            family_id: 家族ID
            path: 路径

        Returns:
            str: 完整URL
        """
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        family_path = f"/family/{family_id}"

        if path:
            family_path += f"/{path.lstrip('/')}"

        return urljoin(base_url, family_path)

    @staticmethod
    def build_invitation_url(invitation_code: str) -> str:
        """
        构建邀请URL

        Args:
            invitation_code: 邀请码

        Returns:
            str: 邀请URL
        """
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        invitation_path = f"/invitation/{invitation_code}"

        return urljoin(base_url, invitation_path)

class FamilyPermissionHelper:
    """家族权限辅助器"""

    @staticmethod
    def can_user_perform_action(user_permissions: List[str], required_permission: str) -> bool:
        """
        检查用户是否有执行某个操作的权限

        Args:
            user_permissions: 用户权限列表
            required_permission: 需要的权限

        Returns:
            bool: 是否有权限
        """
        return required_permission in user_permissions

    @staticmethod
    def get_highest_role(roles: List[str]) -> str:
        """
        获取最高角色

        Args:
            roles: 角色列表

        Returns:
            str: 最高角色
        """

        if not roles:
            return 'guest'

        return max(roles, key=lambda role: ROLE_WEIGHTS.get(role, 0))

# 工具函数快捷方式
generate_invitation_code = FamilyCodeGenerator.generate_invitation_code
validate_family_name = FamilyValidator.validate_family_name
format_member_count = FamilyFormatter.format_member_count
build_family_url = FamilyUrlBuilder.build_family_url