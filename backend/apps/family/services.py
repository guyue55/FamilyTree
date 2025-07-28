"""
Family应用服务层

基于通用服务基类的家族服务实现，整合了原有功能和V2重构功能。
遵循Django最佳实践和Google Python Style Guide。
"""

from typing import List, Dict, Any, Tuple
from django.db import transaction
from django.db.models import Q, QuerySet
from django.contrib.auth import get_user_model
from loguru import logger

from apps.common.services import BaseService, CacheableService
from apps.common.constants import BusinessLimits
from apps.common.exceptions import LimitExceededError
from apps.common.utils import paginate_queryset
from .models import Family, FamilySettings, FamilyInvitation
from apps.members.models import FamilyMembership
from .permissions import FamilyPermissionChecker, FamilyPermission, check_invitation_permission
from .exceptions import (
    FamilyNotFoundError,
    FamilyPermissionError,
    FamilyValidationError,
    FamilyNameConflictError,
    FamilyMemberLimitError
)

User = get_user_model()


class FamilyService(BaseService, CacheableService):
    """
    家族服务类
    
    整合了原有功能和V2重构功能，提供统一的家族管理服务。
    继承自BaseService和CacheableService，具备通用服务能力和缓存功能。
    """
    
    model = Family
    cache_prefix = "family"
    cache_timeout = 3600  # 1小时缓存
    
    # 搜索字段配置
    search_fields = ['name', 'description', 'tags', 'origin_location']
    filter_fields = ['visibility', 'is_active', 'allow_join']
    ordering_fields = ['created_at', 'updated_at', 'name', 'member_count']
    
    @classmethod
    def get_search_fields(cls) -> List[str]:
        """获取搜索字段列表"""
        return cls.search_fields
    
    @classmethod
    def get_filter_fields(cls) -> List[str]:
        """获取过滤字段列表"""
        return cls.filter_fields
    
    @classmethod
    def get_ordering_fields(cls) -> List[str]:
        """获取排序字段列表"""
        return cls.ordering_fields
    
    @classmethod
    def get_queryset(cls, user: User = None) -> QuerySet:
        """
        获取基础查询集
        
        Args:
            user: 当前用户
            
        Returns:
            QuerySet: 家族查询集
        """
        queryset = cls.model.objects.select_related('creator').prefetch_related('members')
        
        if user and not user.is_superuser:
            # 非超级用户只能看到有权限的家族
            queryset = cls._filter_by_permission(queryset, user)
        
        return queryset
    
    @classmethod
    def _filter_by_permission(cls, queryset: QuerySet, user: User) -> QuerySet:
        """
        根据权限过滤查询集
        
        Args:
            queryset: 原始查询集
            user: 当前用户
            
        Returns:
            QuerySet: 过滤后的查询集
        """
        return queryset.filter(
            Q(visibility='public') |
            Q(creator=user) |
            Q(members=user)
        ).distinct()
    
    @classmethod
    def validate_create_data(cls, data: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        验证创建数据
        
        Args:
            data: 创建数据
            user: 当前用户
            
        Returns:
            Dict[str, Any]: 验证后的数据
            
        Raises:
            FamilyValidationError: 验证失败
            FamilyNameConflictError: 名称冲突
            LimitExceededError: 超出限制
        """
        # 检查用户创建家族数量限制
        user_family_count = cls.model.objects.filter(creator=user).count()
        if user_family_count >= BusinessLimits.MAX_FAMILIES_PER_USER:
            raise LimitExceededError(f"用户最多只能创建{BusinessLimits.MAX_FAMILIES_PER_USER}个家族")
        
        # 检查家族名称是否重复
        name = data.get('name', '').strip()
        if not name:
            raise FamilyValidationError("家族名称不能为空")
        
        if cls.model.objects.filter(name=name).exists():
            raise FamilyNameConflictError(f"家族名称'{name}'已存在")
        
        # 设置创建者
        data['creator'] = user
        
        return data
    
    @classmethod
    def validate_update_data(cls, instance: Family, data: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        验证更新数据
        
        Args:
            instance: 家族实例
            data: 更新数据
            user: 当前用户
            
        Returns:
            Dict[str, Any]: 验证后的数据
            
        Raises:
            FamilyPermissionError: 权限不足
            FamilyNameConflictError: 名称冲突
        """
        # 检查权限
        if not FamilyPermissionChecker.check_permission(user, instance, FamilyPermission.EDIT):
            raise FamilyPermissionError("没有编辑家族的权限")
        
        # 检查名称冲突
        name = data.get('name')
        if name and name != instance.name:
            if cls.model.objects.filter(name=name).exclude(id=instance.id).exists():
                raise FamilyNameConflictError(f"家族名称'{name}'已存在")
        
        return data
    
    @classmethod
    @transaction.atomic
    def create_family(cls, data: Dict[str, Any], user: User) -> Family:
        """
        创建家族
        
        Args:
            data: 家族数据
            user: 创建者
            
        Returns:
            Family: 创建的家族实例
            
        Raises:
            FamilyValidationError: 验证失败
            FamilyNameConflictError: 名称冲突
        """
        # 验证数据
        validated_data = cls.validate_create_data(data, user)
        
        # 创建家族
        family = cls.create(validated_data)
        
        # 创建默认设置
        FamilySettings.objects.create(
            family=family,
            tree_layout='vertical',
            show_photos=True,
            show_birth_death_dates=True,
            privacy_level='family'
        )
        
        # 清除相关缓存
        cls.clear_cache_pattern(f"{cls.cache_prefix}:list:*")
        
        logger.info(f"用户 {user.username} 创建了家族 {family.name}")
        
        return family
    
    @classmethod
    def get_family_detail(cls, family_id: int, user: User = None) -> Family:
        """
        获取家族详情
        
        Args:
            family_id: 家族ID
            user: 当前用户
            
        Returns:
            Family: 家族实例
            
        Raises:
            FamilyNotFoundError: 家族不存在
            FamilyPermissionError: 权限不足
        """
        cache_key = f"{cls.cache_prefix}:detail:{family_id}"
        
        # 尝试从缓存获取
        family = cls.get_from_cache(cache_key)
        if family is None:
            try:
                family = cls.model.objects.select_related('creator').get(id=family_id)
                cls.set_cache(cache_key, family)
            except cls.model.DoesNotExist:
                raise FamilyNotFoundError(f"家族 {family_id} 不存在")
        
        # 检查权限
        if user and not FamilyPermissionChecker.check_permission(user, family, FamilyPermission.VIEW):
            raise FamilyPermissionError("没有查看家族的权限")
        
        return family
    
    @classmethod
    def list_families(cls, user: User = None, **filters) -> Tuple[List[Family], int]:
        """
        获取家族列表
        
        Args:
            user: 当前用户
            **filters: 过滤条件
            
        Returns:
            Tuple[List[Family], int]: (家族列表, 总数)
        """
        queryset = cls.get_queryset(user)
        
        # 应用过滤条件
        queryset = cls.apply_filters(queryset, filters)
        
        # 应用搜索
        keyword = filters.get('keyword')
        if keyword:
            queryset = cls.apply_search(queryset, keyword)
        
        # 应用排序
        ordering = filters.get('ordering', '-created_at')
        queryset = cls.apply_ordering(queryset, ordering)
        
        # 分页
        page = filters.get('page', 1)
        page_size = filters.get('page_size', 20)
        
        return paginate_queryset(queryset, page, page_size)
    
    @classmethod
    @transaction.atomic
    def update_family(cls, family_id: int, data: Dict[str, Any], user: User) -> Family:
        """
        更新家族信息
        
        Args:
            family_id: 家族ID
            data: 更新数据
            user: 当前用户
            
        Returns:
            Family: 更新后的家族实例
        """
        family = cls.get_family_detail(family_id, user)
        
        # 验证数据
        validated_data = cls.validate_update_data(family, data, user)
        
        # 更新家族
        updated_family = cls.update(family.id, validated_data)
        
        # 清除缓存
        cls.clear_cache(f"{cls.cache_prefix}:detail:{family_id}")
        cls.clear_cache_pattern(f"{cls.cache_prefix}:list:*")
        
        logger.info(f"用户 {user.username} 更新了家族 {family.name}")
        
        return updated_family
    
    @classmethod
    @transaction.atomic
    def delete_family(cls, family_id: int, user: User) -> bool:
        """
        删除家族
        
        Args:
            family_id: 家族ID
            user: 当前用户
            
        Returns:
            bool: 是否删除成功
        """
        family = cls.get_family_detail(family_id, user)
        
        # 检查权限
        if not FamilyPermissionChecker.check_permission(user, family, FamilyPermission.DELETE):
            raise FamilyPermissionError("没有删除家族的权限")
        
        # 删除家族
        family_name = family.name
        cls.delete(family_id)
        
        # 清除缓存
        cls.clear_cache(f"{cls.cache_prefix}:detail:{family_id}")
        cls.clear_cache_pattern(f"{cls.cache_prefix}:list:*")
        
        logger.info(f"用户 {user.username} 删除了家族 {family_name}")
        
        return True
    
    @classmethod
    def get_family_statistics(cls, family_id: int, user: User) -> Dict[str, Any]:
        """
        获取家族统计信息
        
        Args:
            family_id: 家族ID
            user: 当前用户
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        family = cls.get_family_detail(family_id, user)
        
        cache_key = f"{cls.cache_prefix}:stats:{family_id}"
        stats = cls.get_from_cache(cache_key)
        
        if stats is None:
            stats = {
                'member_count': family.member_count,
                'generation_count': family.generation_count,
                'active_members': family.members.filter(is_active=True).count(),
                'recent_activities': family.get_recent_activities_count(),
                'created_at': family.created_at,
                'last_updated': family.updated_at
            }
            cls.set_cache(cache_key, stats, timeout=1800)  # 30分钟缓存
        
        return stats
    
    @classmethod
    def search_public_families(cls, keyword: str = None, **filters) -> Tuple[List[Family], int]:
        """
        搜索公开家族
        
        Args:
            keyword: 搜索关键词
            **filters: 过滤条件
            
        Returns:
            Tuple[List[Family], int]: (家族列表, 总数)
        """
        queryset = cls.model.objects.filter(
            visibility='public',
            is_active=True
        ).select_related('creator')
        
        # 应用搜索
        if keyword:
            queryset = cls.apply_search(queryset, keyword)
        
        # 应用过滤条件
        queryset = cls.apply_filters(queryset, filters)
        
        # 排序
        ordering = filters.get('ordering', '-member_count')
        queryset = cls.apply_ordering(queryset, ordering)
        
        # 分页
        page = filters.get('page', 1)
        page_size = filters.get('page_size', 20)
        
        return paginate_queryset(queryset, page, page_size)
    
    @classmethod
    @transaction.atomic
    def join_family(cls, family_id: int, user: User) -> bool:
        """
        加入家族
        
        Args:
            family_id: 家族ID
            user: 用户
            
        Returns:
            bool: 是否加入成功
        """
        family = cls.get_family_detail(family_id)
        
        # 检查是否允许加入
        if not family.allow_join:
            raise FamilyPermissionError("该家族不允许直接加入")
        
        # 检查是否已经是成员
        if family.members.filter(id=user.id).exists():
            raise FamilyValidationError("您已经是该家族的成员")
        
        # 检查成员数量限制
        if family.member_count >= BusinessLimits.MAX_MEMBERS_PER_FAMILY:
            raise FamilyMemberLimitError(f"家族成员数量已达上限({BusinessLimits.MAX_MEMBERS_PER_FAMILY})")
        
        # 加入家族
        family.members.add(user)
        family.member_count += 1
        family.save(update_fields=['member_count'])
        
        # 清除缓存
        cls.clear_cache(f"{cls.cache_prefix}:detail:{family_id}")
        cls.clear_cache_pattern(f"{cls.cache_prefix}:stats:*")
        
        logger.info(f"用户 {user.username} 加入了家族 {family.name}")
        
        return True
    
    @classmethod
    @transaction.atomic
    def leave_family(cls, family_id: int, user: User) -> bool:
        """
        离开家族
        
        Args:
            family_id: 家族ID
            user: 用户
            
        Returns:
            bool: 是否离开成功
        """
        family = cls.get_family_detail(family_id)
        
        # 检查是否是成员
        if not family.members.filter(id=user.id).exists():
            raise FamilyValidationError("您不是该家族的成员")
        
        # 创建者不能离开自己的家族
        if family.creator == user:
            raise FamilyPermissionError("家族创建者不能离开自己的家族")
        
        # 离开家族
        family.members.remove(user)
        family.member_count -= 1
        family.save(update_fields=['member_count'])
        
        # 清除缓存
        cls.clear_cache(f"{cls.cache_prefix}:detail:{family_id}")
        cls.clear_cache_pattern(f"{cls.cache_prefix}:stats:*")
        
        logger.info(f"用户 {user.username} 离开了家族 {family.name}")
        
        return True
    
    # ============================================================================
    # 家族邀请相关业务逻辑
    # ============================================================================
    
    @classmethod
    def get_family_invitations(cls, family_id: int, user: User, status: str = None, 
                              page: int = 1, page_size: int = 20) -> Tuple[List[FamilyInvitation], int]:
        """
        获取家族邀请列表
        
        Args:
            family_id: 家族ID
            user: 当前用户
            status: 邀请状态过滤
            page: 页码
            page_size: 每页大小
            
        Returns:
            Tuple[List[FamilyInvitation], int]: (邀请列表, 总数)
        """
        family = cls.get_family_detail(family_id, user)
        
        # 检查权限
        checker = FamilyPermissionChecker(user, family)
        if not checker.has_permission(FamilyPermission.MANAGE_INVITATIONS):
            raise FamilyPermissionError("无权限查看家族邀请")
        
        queryset = FamilyInvitation.objects.filter(family_id=family_id).select_related('inviter')
        
        if status:
            queryset = queryset.filter(status=status)
        
        queryset = queryset.order_by('-created_at')
        
        return paginate_queryset(queryset, page, page_size)
    
    @classmethod
    @transaction.atomic
    def create_family_invitation(cls, family_id: int, invitation_data: Dict[str, Any], user: User) -> FamilyInvitation:
        """
        创建家族邀请
        
        Args:
            family_id: 家族ID
            invitation_data: 邀请数据
            user: 邀请者
            
        Returns:
            FamilyInvitation: 创建的邀请实例
        """
        from datetime import timedelta
        from django.utils import timezone
        import uuid
        from .utils import generate_invitation_code
        
        family = cls.get_family_detail(family_id, user)
        
        # 检查权限
        checker = FamilyPermissionChecker(user, family)
        if not checker.has_permission(FamilyPermission.INVITE_MEMBERS):
            raise FamilyPermissionError("无权限发送邀请")
        
        # 检查是否已存在未处理的邀请
        filters = {'family_id': family_id, 'status': 'pending'}
        if invitation_data.get('invitee_email'):
            filters['invitee_email'] = invitation_data['invitee_email']
        elif invitation_data.get('invitee_phone'):
            filters['invitee_phone'] = invitation_data['invitee_phone']
        
        if FamilyInvitation.objects.filter(**filters).exists():
            raise FamilyValidationError("已存在未处理的邀请")
        
        # 创建邀请
        invitation = FamilyInvitation.objects.create(
            family_id=family_id,
            inviter=user,
            invitation_code=generate_invitation_code(),
            expires_at=timezone.now() + timedelta(days=7),
            status='pending',
            **invitation_data
        )
        
        logger.info(f"用户 {user.username} 向 {invitation_data.get('invitee_email', invitation_data.get('invitee_phone'))} 发送了家族邀请")
        
        return invitation
    
    @classmethod
    def get_invitation_detail(cls, invitation_id: int, user: User) -> FamilyInvitation:
        """
        获取邀请详情
        
        Args:
            invitation_id: 邀请ID
            user: 当前用户
            
        Returns:
            FamilyInvitation: 邀请实例
        """
        try:
            invitation = FamilyInvitation.objects.select_related('inviter').get(id=invitation_id)
        except FamilyInvitation.DoesNotExist:
            raise FamilyNotFoundError("邀请不存在")
        
        # 检查权限：邀请者、被邀请者或家族管理员可以查看
        if not check_invitation_permission(user, invitation):
            family = cls.get_family_detail(invitation.family_id, user)
            checker = FamilyPermissionChecker(user, family)
            if not checker.has_permission(FamilyPermission.MANAGE_INVITATIONS):
                raise FamilyPermissionError("无权限查看此邀请")
        
        return invitation
    
    @classmethod
    @transaction.atomic
    def accept_invitation(cls, invitation_id: int, user: User) -> Dict[str, Any]:
        """
        接受家族邀请
        
        Args:
            invitation_id: 邀请ID
            user: 用户
            
        Returns:
            Dict[str, Any]: 包含成员信息和邀请状态的字典
        """
        from django.utils import timezone
        
        try:
            invitation = FamilyInvitation.objects.select_related().get(id=invitation_id)
        except FamilyInvitation.DoesNotExist:
            raise FamilyNotFoundError("邀请不存在")
        
        # 检查权限：只有被邀请者可以接受
        if not check_invitation_permission(user, invitation):
            raise FamilyPermissionError("无权限接受此邀请")
        
        # 检查邀请状态
        if invitation.status != 'pending':
            raise FamilyValidationError("邀请已处理")
        
        if invitation.expires_at < timezone.now():
            raise FamilyValidationError("邀请已过期")
        
        # 检查是否已是家族成员
        if FamilyMembership.objects.filter(family_id=invitation.family_id, user=user).exists():
            raise FamilyValidationError("您已是该家族成员")
        
        # 接受邀请
        invitation.status = 'accepted'
        invitation.processed_at = timezone.now()
        invitation.processor = user
        invitation.save()
        
        # 创建家族成员关系
        member = FamilyMembership.objects.create(
            family_id=invitation.family_id,
            user=user,
            role='member',
            joined_at=timezone.now()
        )
        
        # 清除相关缓存
        cls.clear_cache(f"{cls.cache_prefix}:detail:{invitation.family_id}")
        
        logger.info(f"用户 {user.username} 接受了家族邀请并加入家族 {invitation.family_id}")
        
        return {
            'member': member,
            'invitation': invitation
        }
    
    @classmethod
    @transaction.atomic
    def reject_invitation(cls, invitation_id: int, user: User) -> FamilyInvitation:
        """
        拒绝家族邀请
        
        Args:
            invitation_id: 邀请ID
            user: 用户
            
        Returns:
            FamilyInvitation: 更新后的邀请实例
        """
        from django.utils import timezone
        
        try:
            invitation = FamilyInvitation.objects.get(id=invitation_id, status='pending')
        except FamilyInvitation.DoesNotExist:
            raise FamilyNotFoundError("邀请不存在或已处理")
        
        # 验证用户是否为被邀请者
        if not (invitation.invitee_email == user.email or 
               invitation.invitee_phone == user.phone):
            raise FamilyPermissionError("您不是此邀请的接收者")
        
        # 更新邀请状态
        invitation.status = 'rejected'
        invitation.rejected_at = timezone.now()
        invitation.save()
        
        logger.info(f"用户 {user.username} 拒绝了家族邀请 {invitation_id}")
        
        return invitation
    
    @classmethod
    @transaction.atomic
    def cancel_invitation(cls, invitation_id: int, user: User) -> FamilyInvitation:
        """
        取消家族邀请
        
        Args:
            invitation_id: 邀请ID
            user: 用户
            
        Returns:
            FamilyInvitation: 更新后的邀请实例
        """
        try:
            invitation = FamilyInvitation.objects.select_related().get(
                id=invitation_id, 
                status='pending'
            )
        except FamilyInvitation.DoesNotExist:
            raise FamilyNotFoundError("邀请不存在或已处理")
        
        # 权限检查：只有邀请者或家族管理员可以取消
        if not (invitation.inviter == user or
               FamilyMembership.objects.filter(
                   family_id=invitation.family_id,
                   user=user,
                   role__in=['admin', 'owner']
               ).exists()):
            raise FamilyPermissionError("无权取消此邀请")
        
        # 更新邀请状态
        invitation.status = 'cancelled'
        invitation.save()
        
        logger.info(f"用户 {user.username} 取消了家族邀请 {invitation_id}")
        
        return invitation
    
    @classmethod
    def get_family_settings(cls, family_id: int, user: User) -> FamilySettings:
        """
        获取家族设置
        
        Args:
            family_id: 家族ID
            user: 当前用户
            
        Returns:
            FamilySettings: 家族设置实例
        """
        family = cls.get_family_detail(family_id, user)
        
        # 检查权限
        checker = FamilyPermissionChecker(user, family)
        if not checker.has_permission(FamilyPermission.VIEW_FAMILY):
            raise FamilyPermissionError("无权限查看家族设置")
        
        try:
            return FamilySettings.objects.get(family=family)
        except FamilySettings.DoesNotExist:
            # 如果不存在设置，创建默认设置
            return FamilySettings.objects.create(
                family=family,
                tree_layout='vertical',
                show_photos=True,
                show_birth_death_dates=True,
                privacy_level='family'
            )
    
    @classmethod
    @transaction.atomic
    def update_family_settings(cls, family_id: int, settings_data: Dict[str, Any], user: User) -> FamilySettings:
        """
        更新家族设置
        
        Args:
            family_id: 家族ID
            settings_data: 设置数据
            user: 当前用户
            
        Returns:
            FamilySettings: 更新后的设置实例
        """
        family = cls.get_family_detail(family_id, user)
        
        # 检查权限
        checker = FamilyPermissionChecker(user, family)
        if not checker.has_permission(FamilyPermission.MANAGE_SETTINGS):
            raise FamilyPermissionError("无权限修改家族设置")
        
        settings, created = FamilySettings.objects.get_or_create(
            family=family,
            defaults={
                'tree_layout': 'vertical',
                'show_photos': True,
                'show_birth_death_dates': True,
                'privacy_level': 'family'
            }
        )
        
        # 更新设置
        for key, value in settings_data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        settings.save()
        
        # 清除缓存
        cls.clear_cache(f"{cls.cache_prefix}:detail:{family_id}")
        
        logger.info(f"用户 {user.username} 更新了家族 {family.name} 的设置")
        
        return settings