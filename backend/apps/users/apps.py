from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    """
    用户应用配置
    
    配置用户应用的基本信息和初始化设置。
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    label = 'users'
    verbose_name = _('用户管理')
    
    def ready(self):
        """
        应用准备就绪时的初始化操作
        """
        # 导入信号处理器
        try:
            from . import signals
        except ImportError:
            pass
        
        # 注册权限（仅在非迁移命令执行时）
        import sys
        if not ('makemigrations' in sys.argv or 'migrate' in sys.argv):
            try:
                self._register_permissions()
            except Exception as e:
                print(f"权限注册失败，可能是数据库表尚未创建: {e}")
        
        # 注册定时任务
        self._register_tasks()
    
    def _register_permissions(self):
        """注册自定义权限"""
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import User, UserLoginLog
        
        # 用户相关权限
        user_ct = ContentType.objects.get_for_model(User)
        permissions = [
            ('can_view_user_details', '查看用户详情'),
            ('can_manage_user_status', '管理用户状态'),
            ('can_reset_user_password', '重置用户密码'),
            ('can_export_user_data', '导出用户数据'),
        ]
        
        for codename, name in permissions:
            Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=user_ct
            )
    
    def _register_tasks(self):
        """注册定时任务"""
        try:
            from celery import current_app
            
            # 注册清理过期登录日志任务
            @current_app.task(name='users.cleanup_old_login_logs')
            def cleanup_old_login_logs():
                """清理30天前的登录日志"""
                from datetime import datetime, timedelta
                from .models import UserLoginLog
                
                cutoff_date = datetime.now() - timedelta(days=30)
                deleted_count = UserLoginLog.objects.filter(
                    created_at__lt=cutoff_date
                ).delete()[0]
                
                return f"已清理 {deleted_count} 条过期登录日志"
            
            # 注册用户统计任务
            @current_app.task(name='users.generate_user_statistics')
            def generate_user_statistics():
                """生成用户统计数据"""
                from .models import User
                from django.utils import timezone
                from datetime import timedelta
                
                now = timezone.now()
                today = now.date()
                week_ago = today - timedelta(days=7)
                month_ago = today - timedelta(days=30)
                
                stats = {
                    'total_users': User.objects.count(),
                    'active_users': User.objects.filter(is_active=True).count(),
                    'verified_users': User.objects.filter(is_verified=True).count(),
                    'premium_users': User.objects.filter(is_premium=True).count(),
                    'new_users_this_week': User.objects.filter(
                        date_joined__gte=week_ago
                    ).count(),
                    'new_users_this_month': User.objects.filter(
                        date_joined__gte=month_ago
                    ).count(),
                }
                
                return stats
                
        except ImportError:
            # Celery 未安装，跳过任务注册
            pass