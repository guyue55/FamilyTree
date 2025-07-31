"""
Family应用配置

Django应用配置类，定义应用的基本信息和初始化设置。
遵循Django最佳实践和Google Python Style Guide。
"""

import sys
from django.apps import AppConfig
from django.db import connection
from django.db.utils import OperationalError
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class FamilyConfig(AppConfig):
    """家族应用配置类"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.family'
    verbose_name = _('家族管理')

    def ready(self):
        """应用准备就绪时的初始化操作"""
        # 导入信号处理器
        try:
            from . import signals
        except ImportError:
            pass

        # 导入任务（如果使用Celery）
        try:
            from . import tasks
        except ImportError:
            pass

        # 安全地注册权限
        self._safe_register_permissions()

        # 注册缓存键
        self._register_cache_keys()

        # 注册通知类型
        self._register_notification_types()

    def _safe_register_permissions(self):
        """安全地注册权限，避免在不合适的时机执行"""

        # 检查是否在执行管理命令
        management_commands = [
            'makemigrations', 'migrate', 'showmigrations', 'sqlmigrate',
            'squashmigrations', 'test', 'check', 'collectstatic',
            'compilemessages', 'makemessages', 'shell', 'dbshell',
            'dumpdata', 'loaddata', 'flush', 'inspectdb'
        ]

        # 如果在执行管理命令，跳过权限注册
        if any(cmd in sys.argv for cmd in management_commands):
            return

        # 延迟注册权限，确保数据库已经准备好
        try:

            # 测试数据库连接
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")

            # 如果数据库连接正常，注册权限
            self._register_permissions()

        except (OperationalError, Exception):
            # 数据库未准备好或其他错误，静默跳过
            # 在生产环境中，权限应该通过数据迁移或管理命令来创建
            pass

    def _register_permissions(self):
        """注册家族相关权限"""

        try:
            from django.contrib.auth.models import Permission
            from django.contrib.contenttypes.models import ContentType
            from .models import Family
            family_content_type = ContentType.objects.get_for_model(Family)

            # 定义自定义权限
            custom_permissions = [
                ('view_family_details', _('查看家族详情')),
                ('manage_family_members', _('管理家族成员')),
                ('manage_family_invitations', _('管理家族邀请')),
                ('edit_family_settings', _('编辑家族设置')),
                ('delete_family', _('删除家族')),
                ('export_family_data', _('导出家族数据')),
                ('import_family_data', _('导入家族数据')),
                ('view_family_statistics', _('查看家族统计')),
                ('moderate_family_content', _('审核家族内容')),
                ('backup_family_data', _('备份家族数据')),
            ]

            for codename, name in custom_permissions:
                Permission.objects.get_or_create(
                    codename=codename,
                    name=name,
                    content_type=family_content_type,
                )
        except Exception:
            # 在迁移过程中可能会出现异常，忽略
            pass

    def _register_cache_keys(self):
        """注册缓存键模式"""

        # 定义缓存键前缀
        cache_prefixes = {
            'family_detail': 'family:detail:{}',
            'family_members': 'family:members:{}',
            'family_invitations': 'family:invitations:{}',
            'family_settings': 'family:settings:{}',
            'family_statistics': 'family:stats:{}',
            'user_families': 'user:families:{}',
            'family_permissions': 'family:permissions:{}:{}',
            'family_search': 'family:search:{}',
            'popular_families': 'families:popular',
            'recent_families': 'families:recent',
        }

        # 存储到设置中（如果需要）
        if not hasattr(settings, 'FAMILY_CACHE_KEYS'):
            settings.FAMILY_CACHE_KEYS = cache_prefixes

    def _register_notification_types(self):
        """注册通知类型"""
        # 如果使用通知系统，在这里注册通知类型
        notification_types = [
            'family_invitation_received',
            'family_invitation_accepted',
            'family_invitation_rejected',
            'family_member_joined',
            'family_member_left',
            'family_member_role_changed',
            'family_settings_updated',
            'family_deleted',
            'family_created',
        ]

        # 这里可以注册到通知系统
        # 例如：NotificationRegistry.register(notification_types)
        pass