"""Family应用信号处理器

处理家庭相关的Django信号。
遵循Django Ninja框架的API设计规范。
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Family, FamilySettings, FamilyInvitation


@receiver(post_save, sender=Family)
def handle_family_created(sender, instance, created, **kwargs):
    """处理家庭创建后的操作"""
    if created:
        # 创建默认家庭设置
        FamilySettings.objects.get_or_create(
            family=instance,
            defaults={
                'privacy_level': 'private',
                'allow_invitations': True,
                'max_members': 50,
                'settings': {}
            }
        )


@receiver(post_save, sender=FamilySettings)
def handle_family_settings_updated(sender, instance, **kwargs):
    """处理家庭设置更新"""
    # 可以在这里添加设置更新后的处理逻辑
    pass


@receiver(post_save, sender=FamilyInvitation)
def handle_family_invitation_created(sender, instance, created, **kwargs):
    """处理家庭邀请创建"""
    if created:
        # 可以在这里添加邀请创建后的处理逻辑，如发送通知
        pass


@receiver(post_delete, sender=Family)
def handle_family_deleted(sender, instance, **kwargs):
    """处理家庭删除"""
    # 可以在这里添加家庭删除后的清理逻辑
    pass