from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel, SoftDeleteModel, VisibilityChoices

"""
Family应用模型定义

定义家族相关的数据模型，包括家族、成员、邀请等核心实体。
遵循Django最佳实践和Google Python Style Guide。
"""

User = get_user_model()


class TreeLayoutChoices(models.TextChoices):
    """族谱布局选择枚举"""
    VERTICAL = 'vertical', _('垂直布局')
    HORIZONTAL = 'horizontal', _('水平布局')
    RADIAL = 'radial', _('放射布局')
    TREE = 'tree', _('树形布局')


class ThemeChoices(models.TextChoices):
    """主题选择枚举"""
    DEFAULT = 'default', _('默认主题')
    LIGHT = 'light', _('浅色主题')
    DARK = 'dark', _('深色主题')
    CLASSIC = 'classic', _('经典主题')


class FontFamilyChoices(models.TextChoices):
    """字体族选择枚举"""
    DEFAULT = 'default', _('默认字体')
    SERIF = 'serif', _('衬线字体')
    SANS_SERIF = 'sans-serif', _('无衬线字体')
    MONOSPACE = 'monospace', _('等宽字体')


class PrivacyLevelChoices(models.TextChoices):
    """隐私级别选择枚举"""
    PUBLIC = 'public', _('公开')
    FAMILY = 'family', _('仅家族')
    PRIVATE = 'private', _('私有')


class InvitationStatusChoices(models.TextChoices):
    """邀请状态选择枚举"""
    PENDING = 'pending', _('待处理')
    ACCEPTED = 'accepted', _('已接受')
    REJECTED = 'rejected', _('已拒绝')
    EXPIRED = 'expired', _('已过期')

class Family(SoftDeleteModel):
    """
    家族模型

    存储家族的基础信息，如家族名称、描述、创建者等。
    """

    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2)],
        verbose_name='家族名称',
        help_text='家族的名称，至少2个字符',
        db_comment='家族的名称，至少2个字符'
    )

    description = models.TextField(
        max_length=1000,
        blank=True,
        verbose_name='家族描述',
        help_text='家族的详细描述信息',
        db_comment='家族的详细描述信息'
    )

    # 创建者信息（逻辑关联，不使用外键）
    creator_id = models.BigIntegerField(
        verbose_name='创建者ID',
        help_text='家族创建者的用户ID，逻辑关联users.id',
        db_comment='家族创建者的用户ID，逻辑关联users.id'
    )

    # 家族头像
    avatar = models.ImageField(
        upload_to='family_avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='家族头像',
        help_text='家族的头像图片',
        db_comment='家族的头像图片文件路径'
    )

    # 家族封面
    cover_image = models.ImageField(
        upload_to='family_covers/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='家族封面',
        help_text='家族的封面图片',
        db_comment='家族的封面图片文件路径'
    )

    # 可见性设置
    visibility = models.CharField(
        max_length=20,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.FAMILY,
        verbose_name='可见性',
        help_text='家族信息的可见性设置',
        db_comment='家族信息的可见性设置：public-公开，private-私有，family-仅家族成员'
    )

    # 家族状态
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否激活',
        help_text='家族是否处于激活状态',
        db_comment='家族是否处于激活状态'
    )

    # 是否允许加入
    allow_join = models.BooleanField(
        default=True,
        verbose_name='允许加入',
        help_text='是否允许其他用户申请加入家族',
        db_comment='是否允许其他用户申请加入家族'
    )

    # 统计信息
    member_count = models.PositiveIntegerField(
        default=1,
        verbose_name='成员数量',
        help_text='家族成员总数',
        db_comment='家族成员总数'
    )

    generation_count = models.PositiveIntegerField(
        default=1,
        verbose_name='世代数量',
        help_text='家族的世代数量',
        db_comment='家族的世代数量'
    )

    # 家族标签
    tags = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='家族标签',
        help_text='家族标签，用逗号分隔',
        db_comment='家族标签，用逗号分隔'
    )

    # 家族起源地
    origin_location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='起源地',
        help_text='家族的起源地或祖籍',
        db_comment='家族的起源地或祖籍'
    )

    # 家族座右铭
    motto = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='家族座右铭',
        help_text='家族的座右铭或家训',
        db_comment='家族的座右铭或家训'
    )

    class Meta:
        db_table = 'families'
        verbose_name = '家族'
        verbose_name_plural = '家族'
        indexes = [
            models.Index(fields=['creator_id']),
            models.Index(fields=['name']),
            models.Index(fields=['visibility']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    @property
    def creator(self):
        """获取创建者用户对象"""
        if hasattr(self, '_creator_cache'):
            return self._creator_cache
        try:
            self._creator_cache = User.objects.get(id=self.creator_id)
            return self._creator_cache
        except User.DoesNotExist:
            return None

    @property
    def settings(self):
        """获取家族设置"""
        try:
            return FamilySettings.objects.get(family_id=self.id)
        except FamilySettings.DoesNotExist:
            # 如果设置不存在，创建默认设置
            return FamilySettings.objects.create(
                family_id=self.id,
                tree_layout='vertical',
                default_generations=5
            )

    def get_tags_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    def set_tags_list(self, tags_list):
        """设置标签列表"""
        self.tags = ','.join(tags_list) if tags_list else ''

    def update_member_count(self):
        """更新成员数量（根据FamilyMembership计算）"""
        # 计算活跃的家族成员关系数量
        count = FamilyMembership.objects.filter(
            family_id=self.id,
            status='active'
        ).count()
        self.member_count = 1 + count  # 1为创建者
        self.save(update_fields=['member_count'])

    def increment_member_count(self):
        """增加成员数量"""
        self.member_count += 1
        self.save(update_fields=['member_count'])

    def decrement_member_count(self):
        """减少成员数量"""
        if self.member_count > 0:
            self.member_count -= 1
            self.save(update_fields=['member_count'])

class FamilySettings(BaseModel):
    """
    家族设置模型

    存储家族的个性化设置信息。
    """

    # 家族ID（逻辑关联）
    family_id = models.BigIntegerField(
        unique=True,
        verbose_name='家族ID',
        help_text='家族ID，逻辑关联families.id',
        db_comment='家族ID，逻辑关联families.id'
    )

    # 族谱显示设置
    tree_layout = models.CharField(
        max_length=20,
        choices=TreeLayoutChoices.choices,
        default=TreeLayoutChoices.VERTICAL,
        verbose_name='族谱布局',
        help_text='族谱的显示布局方式',
        db_comment='族谱的显示布局方式：vertical-垂直，horizontal-水平，radial-放射，tree-树形'
    )

    # 默认显示世代数
    default_generations = models.PositiveIntegerField(
        default=5,
        verbose_name='默认显示世代',
        help_text='族谱默认显示的世代数量',
        db_comment='族谱默认显示的世代数量'
    )

    # 是否显示照片
    show_photos = models.BooleanField(
        default=True,
        verbose_name='显示照片',
        help_text='是否在族谱中显示成员照片',
        db_comment='是否在族谱中显示成员照片'
    )

    # 是否显示出生日期
    show_birth_dates = models.BooleanField(
        default=True,
        verbose_name='显示出生日期',
        help_text='是否显示成员的出生日期',
        db_comment='是否显示成员的出生日期'
    )

    # 是否显示死亡日期
    show_death_dates = models.BooleanField(
        default=True,
        verbose_name='显示死亡日期',
        help_text='是否显示成员的死亡日期',
        db_comment='是否显示成员的死亡日期'
    )

    # 是否显示职业信息
    show_occupation = models.BooleanField(
        default=False,
        verbose_name='显示职业',
        help_text='是否显示成员的职业信息',
        db_comment='是否显示成员的职业信息'
    )

    # 主题设置
    theme = models.CharField(
        max_length=20,
        choices=ThemeChoices.choices,
        default=ThemeChoices.DEFAULT,
        verbose_name='主题',
        help_text='家族族谱的主题风格',
        db_comment='家族族谱的主题风格：default-默认，light-浅色，dark-深色，classic-经典'
    )

    # 主题颜色
    theme_color = models.CharField(
        max_length=7,
        default='#1890ff',
        verbose_name='主题颜色',
        help_text='家族主题颜色，十六进制格式',
        db_comment='家族主题颜色，十六进制格式'
    )

    # 字体大小
    font_size = models.PositiveIntegerField(
        default=14,
        verbose_name='字体大小',
        help_text='族谱显示的字体大小（像素）',
        db_comment='族谱显示的字体大小（像素）'
    )

    # 字体设置
    font_family = models.CharField(
        max_length=50,
        choices=FontFamilyChoices.choices,
        default=FontFamilyChoices.DEFAULT,
        verbose_name='字体族',
        help_text='族谱显示的字体族',
        db_comment='族谱显示的字体族：default-默认，serif-衬线，sans-serif-无衬线，monospace-等宽'
    )

    # 隐私设置
    privacy_level = models.CharField(
        max_length=20,
        choices=PrivacyLevelChoices.choices,
        default=PrivacyLevelChoices.FAMILY,
        verbose_name='隐私级别',
        help_text='家族信息的隐私级别',
        db_comment='家族信息的隐私级别：public-公开，family-仅家族，private-私有'
    )

    require_approval = models.BooleanField(
        default=True,
        verbose_name='需要审批',
        help_text='新成员加入是否需要管理员审批',
        db_comment='新成员加入是否需要管理员审批'
    )

    allow_member_invite = models.BooleanField(
        default=True,
        verbose_name='允许成员邀请',
        help_text='是否允许普通成员邀请他人加入',
        db_comment='是否允许普通成员邀请他人加入'
    )

    # 通知设置
    enable_notifications = models.BooleanField(
        default=True,
        verbose_name='启用通知',
        help_text='是否启用通知功能',
        db_comment='是否启用通知功能'
    )

    email_notifications = models.BooleanField(
        default=True,
        verbose_name='邮件通知',
        help_text='是否启用邮件通知',
        db_comment='是否启用邮件通知'
    )

    push_notifications = models.BooleanField(
        default=True,
        verbose_name='推送通知',
        help_text='是否启用推送通知',
        db_comment='是否启用推送通知'
    )

    # 通知设置
    notify_new_member = models.BooleanField(
        default=True,
        verbose_name='新成员通知',
        help_text='有新成员加入时是否通知管理员',
        db_comment='有新成员加入时是否通知管理员'
    )

    notify_tree_update = models.BooleanField(
        default=True,
        verbose_name='族谱更新通知',
        help_text='族谱有更新时是否通知相关成员',
        db_comment='族谱有更新时是否通知相关成员'
    )

    class Meta:
        db_table = 'family_settings'
        verbose_name = '家族设置'
        verbose_name_plural = '家族设置'
        indexes = [
            models.Index(fields=['family_id']),
        ]

    def __str__(self):
        return f'家族设置 - {self.family_id}'

class FamilyInvitation(BaseModel):
    """
    家族邀请模型

    记录家族邀请信息。
    """

    # 家族ID（逻辑关联）
    family_id = models.BigIntegerField(
        verbose_name='家族ID',
        help_text='家族ID，逻辑关联families.id',
        db_comment='家族ID，逻辑关联families.id'
    )

    # 邀请者ID（逻辑关联）
    inviter_id = models.BigIntegerField(
        verbose_name='邀请者ID',
        help_text='邀请者用户ID，逻辑关联users.id',
        db_comment='邀请者用户ID，逻辑关联users.id'
    )

    # 被邀请者ID（逻辑关联）
    invitee_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='被邀请者ID',
        help_text='被邀请者用户ID，逻辑关联users.id',
        db_comment='被邀请者用户ID，逻辑关联users.id'
    )

    # 被邀请者信息
    invitee_email = models.EmailField(
        verbose_name='被邀请者邮箱',
        db_comment='被邀请者的邮箱地址'
    )

    invitee_phone = models.CharField(
        max_length=11,
        blank=True,
        verbose_name='被邀请者手机号',
        db_comment='被邀请者的手机号码'
    )

    invitee_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='被邀请者姓名',
        db_comment='被邀请者的姓名'
    )

    # 邀请状态
    status = models.CharField(
        max_length=20,
        choices=InvitationStatusChoices.choices,
        default=InvitationStatusChoices.PENDING,
        verbose_name='邀请状态',
        db_comment='邀请状态：pending-待处理，accepted-已接受，rejected-已拒绝，expired-已过期'
    )

    # 邀请消息
    message = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='邀请消息',
        help_text='邀请时的附加消息',
        db_comment='邀请时的附加消息'
    )

    # 邀请码
    invitation_code = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='邀请码',
        help_text='用于验证邀请的唯一码',
        db_comment='用于验证邀请的唯一码'
    )

    # 过期时间
    expires_at = models.DateTimeField(
        verbose_name='过期时间',
        help_text='邀请的过期时间',
        db_comment='邀请的过期时间'
    )

    # 处理时间
    processed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='处理时间',
        help_text='邀请被处理的时间',
        db_comment='邀请被处理的时间'
    )

    # 拒绝原因
    rejection_reason = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='拒绝原因',
        help_text='拒绝邀请的原因',
        db_comment='拒绝邀请的原因'
    )

    @property
    def family(self):
        """获取家族对象"""
        try:
            return Family.objects.get(id=self.family_id)
        except Family.DoesNotExist:
            return None

    @property
    def inviter(self):
        """获取邀请者对象"""
        User = get_user_model()
        try:
            return User.objects.get(id=self.inviter_id)
        except User.DoesNotExist:
            return None

    @property
    def invitee(self):
        """获取被邀请者对象"""
        User = get_user_model()
        if self.invitee_id:
            try:
                return User.objects.get(id=self.invitee_id)
            except User.DoesNotExist:
                return None
        return None

    def is_expired(self):
        """检查邀请是否已过期"""
        return timezone.now() > self.expires_at

    def accept(self):
        """接受邀请"""
        self.status = 'accepted'
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])

    def reject(self):
        """拒绝邀请"""
        self.status = 'rejected'
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])

    class Meta:
        db_table = 'family_invitations'
        verbose_name = '家族邀请'
        verbose_name_plural = '家族邀请'
        indexes = [
            models.Index(fields=['family_id']),
            models.Index(fields=['inviter_id']),
            models.Index(fields=['invitee_id']),
            models.Index(fields=['status']),
            models.Index(fields=['invitation_code']),
        ]

    def __str__(self):
        return f'邀请 - {self.invitee_email} 加入家族 {self.family_id}'