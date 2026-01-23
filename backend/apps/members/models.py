"""
成员管理模块数据模型

该模块定义了家族成员相关的数据模型，包括成员基础信息、家族成员关系等。
遵循Django最佳实践和Google Python Style Guide。
"""

from django.db import models
from django.core.validators import (
    MinLengthValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.utils.translation import gettext_lazy as _
from apps.common.models import (
    BaseModel,
    SoftDeleteModel,
    GenderChoices,
    VisibilityChoices,
)


# 家族成员角色枚举
class FamilyRoleChoices(models.TextChoices):
    """家族角色选择枚举"""

    OWNER = "owner", _("家族创建者")
    ADMIN = "admin", _("管理员")
    EDITOR = "editor", _("编辑者")
    MEMBER = "member", _("普通成员")
    VIEWER = "viewer", _("访客")


class MembershipStatusChoices(models.TextChoices):
    """成员关系状态选择枚举"""

    ACTIVE = "active", _("活跃")
    INACTIVE = "inactive", _("非活跃")
    SUSPENDED = "suspended", _("暂停")
    PENDING = "pending", _("待审核")


class JoinMethodChoices(models.TextChoices):
    """加入方式选择枚举"""

    CREATED = "created", _("创建家族")
    INVITED = "invited", _("受邀加入")
    APPLIED = "applied", _("申请加入")
    IMPORTED = "imported", _("导入添加")


class NoteTypeChoices(models.TextChoices):
    """备注类型选择枚举"""

    GENERAL = "general", _("一般备注")
    IMPORTANT = "important", _("重要信息")
    MEDICAL = "medical", _("医疗信息")
    ACHIEVEMENT = "achievement", _("成就记录")
    STORY = "story", _("故事传说")


class Member(SoftDeleteModel):
    """
    家族成员模型

    存储家族成员的基础信息，包括姓名、性别、生卒年月等。
    """

    # 家族ID（逻辑关联）
    family_id = models.BigIntegerField(
        verbose_name="家族ID",
        help_text="所属家族ID，逻辑关联families.id",
        db_comment="所属家族ID，逻辑关联families.id",
    )

    # 关联用户ID（可选，如果成员已注册用户）
    user_id = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name="用户ID",
        help_text="关联的用户ID，逻辑关联users.id",
        db_comment="关联的用户ID，逻辑关联users.id",
    )

    # 基础信息
    name = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(1)],
        verbose_name="姓名",
        help_text="成员的姓名",
        db_comment="成员的姓名",
    )

    english_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="英文名",
        help_text="成员的英文名",
        db_comment="成员的英文名",
    )

    nickname = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="昵称",
        help_text="成员的昵称或小名",
        db_comment="成员的昵称或小名",
    )

    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices,
        default=GenderChoices.UNKNOWN,
        verbose_name="性别",
        db_comment="成员的性别",
    )

    # 生卒年月
    birth_date = models.DateField(
        blank=True, null=True, verbose_name="出生日期", db_comment="成员的出生日期"
    )

    death_date = models.DateField(
        blank=True, null=True, verbose_name="去世日期", db_comment="成员的去世日期"
    )

    is_alive = models.BooleanField(
        default=True,
        verbose_name="是否在世",
        help_text="成员是否还在世",
        db_comment="成员是否还在世",
    )

    # 出生地和居住地
    birth_place = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="出生地",
        help_text="成员的出生地",
        db_comment="成员的出生地",
    )

    current_location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="现居地",
        help_text="成员的现居住地",
        db_comment="成员的现居住地",
    )

    # 职业信息
    occupation = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="职业",
        help_text="成员的职业",
        db_comment="成员的职业",
    )

    company = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="工作单位",
        help_text="成员的工作单位",
        db_comment="成员的工作单位",
    )

    education = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="教育背景",
        help_text="成员的教育背景",
        db_comment="成员的教育背景",
    )

    # 联系方式
    phone = models.CharField(
        max_length=20, blank=True, verbose_name="电话号码", db_comment="成员的电话号码"
    )

    email = models.EmailField(
        blank=True, verbose_name="邮箱地址", db_comment="成员的邮箱地址"
    )

    # 头像
    avatar = models.ImageField(
        upload_to="member_avatars/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="头像",
        help_text="成员的头像照片",
        db_comment="成员的头像照片",
    )

    # 个人简介
    bio = models.TextField(
        max_length=1000,
        blank=True,
        verbose_name="个人简介",
        help_text="成员的个人简介",
        db_comment="成员的个人简介",
    )

    # 世代信息
    generation = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name="世代",
        help_text="成员在家族中的世代，1为第一代",
        db_comment="成员在家族中的世代，1为第一代",
    )

    # 排序序号（同世代中的排序）
    sort_order = models.PositiveIntegerField(
        default=1,
        verbose_name="排序序号",
        help_text="在同世代中的排序序号",
        db_comment="在同世代中的排序序号",
    )

    # 可见性设置
    visibility = models.CharField(
        max_length=20,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.FAMILY,
        verbose_name="可见性",
        help_text="成员信息的可见性设置",
        db_comment="成员信息的可见性设置",
    )

    # 是否为家族管理员
    is_admin = models.BooleanField(
        default=False,
        verbose_name="是否为管理员",
        help_text="是否为家族管理员",
        db_comment="是否为家族管理员",
    )

    # 加入时间
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="加入时间",
        help_text="成员加入家族的时间",
        db_comment="成员加入家族的时间",
    )

    # 创建者ID（添加此成员的用户）
    creator_id = models.BigIntegerField(
        verbose_name="创建者ID",
        help_text="添加此成员的用户ID，逻辑关联users.id",
        db_comment="添加此成员的用户ID，逻辑关联users.id",
    )

    class Meta:
        db_table = "family_members"
        verbose_name = "家族成员"
        verbose_name_plural = "家族成员"
        indexes = [
            models.Index(fields=["family_id"]),
            models.Index(fields=["user_id"]),
            models.Index(fields=["name"]),
            models.Index(fields=["generation"]),
            models.Index(fields=["sort_order"]),
            models.Index(fields=["is_admin"]),
            models.Index(fields=["joined_at"]),
        ]
        unique_together = [
            ("family_id", "user_id"),  # 同一用户在同一家族中只能有一个成员记录
        ]
        ordering = ["generation", "sort_order", "name"]

    def __str__(self):
        return f"{self.name} (家族{self.family_id})"

    def get_age(self):
        """计算年龄"""
        if not self.birth_date:
            return None

        from datetime import date

        end_date = self.death_date if self.death_date else date.today()
        age = end_date.year - self.birth_date.year

        # 检查是否还没到生日
        if end_date.month < self.birth_date.month or (
            end_date.month == self.birth_date.month
            and end_date.day < self.birth_date.day
        ):
            age -= 1

        return age

    def get_display_name(self):
        """获取显示名称"""
        if self.nickname:
            return f"{self.name}({self.nickname})"
        return self.name

    def is_deceased(self):
        """是否已故"""
        return not self.is_alive or self.death_date is not None


class FamilyMembership(BaseModel):
    """
    家族成员关系模型

    记录用户与家族的关系，包括角色、权限等。
    """

    # 用户ID（逻辑关联）
    user_id = models.BigIntegerField(
        verbose_name="用户ID",
        help_text="用户ID，逻辑关联users.id",
        db_comment="用户ID，逻辑关联users.id",
    )

    # 家族ID（逻辑关联）
    family_id = models.BigIntegerField(
        verbose_name="家族ID",
        help_text="家族ID，逻辑关联families.id",
        db_comment="家族ID，逻辑关联families.id",
    )

    # 成员ID（逻辑关联）
    member_id = models.BigIntegerField(
        verbose_name="成员ID",
        help_text="成员ID，逻辑关联family_members.id",
        db_comment="成员ID，逻辑关联family_members.id",
    )

    # 角色
    role = models.CharField(
        max_length=20,
        choices=FamilyRoleChoices.choices,
        default=FamilyRoleChoices.MEMBER,
        verbose_name="角色",
        help_text="用户在家族中的角色",
        db_comment="用户在家族中的角色",
    )

    # 权限设置
    can_edit_tree = models.BooleanField(
        default=False,
        verbose_name="可编辑族谱",
        help_text="是否可以编辑族谱结构",
        db_comment="是否可以编辑族谱结构",
    )

    can_add_member = models.BooleanField(
        default=False,
        verbose_name="可添加成员",
        help_text="是否可以添加新成员",
        db_comment="是否可以添加新成员",
    )

    can_edit_member = models.BooleanField(
        default=False,
        verbose_name="可编辑成员",
        help_text="是否可以编辑成员信息",
        db_comment="是否可以编辑成员信息",
    )

    can_delete_member = models.BooleanField(
        default=False,
        verbose_name="可删除成员",
        help_text="是否可以删除成员",
        db_comment="是否可以删除成员",
    )

    can_manage_media = models.BooleanField(
        default=False,
        verbose_name="可管理媒体",
        help_text="是否可以管理家族媒体文件",
        db_comment="是否可以管理家族媒体文件",
    )

    can_invite_member = models.BooleanField(
        default=True,
        verbose_name="可邀请成员",
        help_text="是否可以邀请新成员加入",
        db_comment="是否可以邀请新成员加入",
    )

    # 状态
    status = models.CharField(
        max_length=20,
        choices=MembershipStatusChoices.choices,
        default=MembershipStatusChoices.ACTIVE,
        verbose_name="状态",
        db_comment="成员关系状态",
    )

    # 加入方式
    join_method = models.CharField(
        max_length=20,
        choices=JoinMethodChoices.choices,
        default=JoinMethodChoices.INVITED,
        verbose_name="加入方式",
        db_comment="成员加入家族的方式",
    )

    # 加入时间
    joined_at = models.DateTimeField(
        auto_now_add=True, verbose_name="加入时间", db_comment="成员加入家族的时间"
    )

    # 最后活跃时间
    last_active_at = models.DateTimeField(
        auto_now=True, verbose_name="最后活跃时间", db_comment="成员最后活跃时间"
    )

    class Meta:
        db_table = "family_memberships"
        verbose_name = "家族成员关系"
        verbose_name_plural = "家族成员关系"
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["family_id"]),
            models.Index(fields=["member_id"]),
            models.Index(fields=["role"]),
            models.Index(fields=["status"]),
            models.Index(fields=["joined_at"]),
        ]
        unique_together = [
            ("user_id", "family_id"),  # 用户在同一家族中只能有一个关系记录
        ]
        ordering = ["-joined_at"]

    def __str__(self):
        return f"用户{self.user_id}在家族{self.family_id}的关系"

    def is_admin_or_above(self):
        """是否为管理员或以上角色"""
        return self.role in ["owner", "admin"]

    def is_editor_or_above(self):
        """是否为编辑者或以上角色"""
        return self.role in ["owner", "admin", "editor"]

    def can_manage_family(self):
        """是否可以管理家族"""
        return self.role in ["owner", "admin"]

    def update_last_active(self):
        """更新最后活跃时间"""
        from django.utils import timezone

        self.last_active_at = timezone.now()
        self.save(update_fields=["last_active_at"])


class MemberNote(BaseModel):
    """
    成员备注模型

    记录成员的备注信息，支持多人添加备注。
    """

    # 成员ID（逻辑关联）
    member_id = models.BigIntegerField(
        verbose_name="成员ID",
        help_text="成员ID，逻辑关联family_members.id",
        db_comment="成员ID，逻辑关联family_members.id",
    )

    # 创建者ID（逻辑关联）
    creator_id = models.BigIntegerField(
        verbose_name="创建者ID",
        help_text="备注创建者的用户ID，逻辑关联users.id",
        db_comment="备注创建者的用户ID，逻辑关联users.id",
    )

    # 备注内容
    content = models.TextField(
        max_length=1000,
        verbose_name="备注内容",
        help_text="备注的具体内容",
        db_comment="备注的具体内容",
    )

    # 备注类型
    note_type = models.CharField(
        max_length=20,
        choices=NoteTypeChoices.choices,
        default=NoteTypeChoices.GENERAL,
        verbose_name="备注类型",
        db_comment="备注的类型分类",
    )

    # 是否私有
    is_private = models.BooleanField(
        default=False,
        verbose_name="是否私有",
        help_text="私有备注只有创建者可见",
        db_comment="私有备注只有创建者可见",
    )

    # 可见性
    visibility = models.CharField(
        max_length=20,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.FAMILY,
        verbose_name="可见性",
        db_comment="备注的可见性设置",
    )

    class Meta:
        db_table = "member_notes"
        verbose_name = "成员备注"
        verbose_name_plural = "成员备注"
        indexes = [
            models.Index(fields=["member_id"]),
            models.Index(fields=["creator_id"]),
            models.Index(fields=["note_type"]),
            models.Index(fields=["is_private"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"成员{self.member_id}的备注"
