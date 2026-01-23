"""
Family应用信号处理器

该文件定义了Family应用的信号处理器。
遵循Django最佳实践和Google Python Style Guide。
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
            family_id=instance.id,
            defaults={
                "tree_layout": "vertical",
                "default_generations": 5,
                "show_photos": True,
                "show_birth_dates": True,
                "show_death_dates": True,
                "show_occupation": False,
                "theme": "default",
                "theme_color": "#1890ff",
                "font_size": 14,
                "font_family": "default",
                "privacy_level": "family",
                "require_approval": True,
                "allow_member_invite": True,
                "enable_notifications": True,
                "email_notifications": True,
                "push_notifications": True,
                "notify_new_member": True,
                "notify_tree_update": True,
            },
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
