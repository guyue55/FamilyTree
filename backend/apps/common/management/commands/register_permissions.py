"""
权限注册管理命令

该文件定义了权限注册的Django管理命令。
遵循Django最佳实践和Google Python Style Guide。
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from apps.users.models import User
from apps.family.models import Family


class Command(BaseCommand):
    """注册自定义权限的管理命令"""

    help = "注册所有应用的自定义权限"

    def add_arguments(self, parser):
        """添加命令行参数"""
        parser.add_argument("--app", type=str, help="只注册指定应用的权限（可选）")
        parser.add_argument(
            "--force", action="store_true", help="强制重新创建已存在的权限"
        )

    def handle(self, *args, **options):
        """执行命令"""
        app_name = options.get("app")
        force = options.get("force", False)

        if app_name:
            self.stdout.write(f"注册应用 '{app_name}' 的权限...")
            if app_name == "users":
                self._register_users_permissions(force)
            elif app_name == "family":
                self._register_family_permissions(force)
            else:
                self.stdout.write(self.style.ERROR(f"未知的应用: {app_name}"))
                return
        else:
            self.stdout.write("注册所有应用的权限...")
            self._register_users_permissions(force)
            self._register_family_permissions(force)

        self.stdout.write(self.style.SUCCESS("权限注册完成！"))

    @transaction.atomic
    def _register_users_permissions(self, force=False):
        """注册用户应用的权限"""

        try:
            user_ct = ContentType.objects.get_for_model(User)
            permissions = [
                ("can_view_user_details", "查看用户详情"),
                ("can_manage_user_status", "管理用户状态"),
                ("can_reset_user_password", "重置用户密码"),
                ("can_export_user_data", "导出用户数据"),
            ]

            created_count = 0
            updated_count = 0

            for codename, name in permissions:
                if force:
                    # 删除已存在的权限
                    Permission.objects.filter(
                        codename=codename, content_type=user_ct
                    ).delete()

                permission, created = Permission.objects.get_or_create(
                    codename=codename, content_type=user_ct, defaults={"name": name}
                )

                if created:
                    created_count += 1
                    self.stdout.write(f"  ✓ 创建权限: {codename}")
                elif force:
                    permission.name = name
                    permission.save()
                    updated_count += 1
                    self.stdout.write(f"  ↻ 更新权限: {codename}")
                else:
                    self.stdout.write(f"  - 权限已存在: {codename}")

            self.stdout.write(
                f"用户权限: 创建 {created_count} 个，更新 {updated_count} 个"
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"注册用户权限失败: {e}"))

    @transaction.atomic
    def _register_family_permissions(self, force=False):
        """注册家族应用的权限"""

        try:
            family_ct = ContentType.objects.get_for_model(Family)
            permissions = [
                ("view_family_details", "查看家族详情"),
                ("manage_family_members", "管理家族成员"),
                ("manage_family_invitations", "管理家族邀请"),
                ("edit_family_settings", "编辑家族设置"),
                ("delete_family", "删除家族"),
                ("export_family_data", "导出家族数据"),
                ("import_family_data", "导入家族数据"),
                ("view_family_statistics", "查看家族统计"),
                ("moderate_family_content", "审核家族内容"),
                ("backup_family_data", "备份家族数据"),
            ]

            created_count = 0
            updated_count = 0

            for codename, name in permissions:
                if force:
                    # 删除已存在的权限
                    Permission.objects.filter(
                        codename=codename, content_type=family_ct
                    ).delete()

                permission, created = Permission.objects.get_or_create(
                    codename=codename, content_type=family_ct, defaults={"name": name}
                )

                if created:
                    created_count += 1
                    self.stdout.write(f"  ✓ 创建权限: {codename}")
                elif force:
                    permission.name = name
                    permission.save()
                    updated_count += 1
                    self.stdout.write(f"  ↻ 更新权限: {codename}")
                else:
                    self.stdout.write(f"  - 权限已存在: {codename}")

            self.stdout.write(
                f"家族权限: 创建 {created_count} 个，更新 {updated_count} 个"
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"注册家族权限失败: {e}"))
