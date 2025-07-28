from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from apps.common.models import BaseModel


class User(AbstractUser, BaseModel):
    """
    用户模型
    
    继承Django的AbstractUser，扩展用户字段。
    包含用户基础信息、认证信息等。
    """
    
    # 手机号验证器
    phone_validator = RegexValidator(
        regex=r'^1[3-9]\d{9}$',
        message='请输入有效的手机号码'
    )
    
    # 扩展字段
    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[phone_validator],
        verbose_name='手机号',
        help_text='用户手机号，用于登录和找回密码',
        db_comment='手机号'
    )
    
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='头像',
        help_text='用户头像图片',
        db_comment='头像URL'
    )
    
    nickname = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='昵称',
        help_text='用户显示昵称',
        db_comment='昵称'
    )
    
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', '男'),
            ('female', '女'),
            ('unknown', '未知'),
        ],
        default='unknown',
        verbose_name='性别',
        db_comment='性别：male-男，female-女，unknown-未知'
    )
    
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='出生日期',
        db_comment='出生日期'
    )
    
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='个人简介',
        db_comment='个人简介'
    )
    
    # 状态字段
    is_verified = models.BooleanField(
        default=False,
        verbose_name='是否已验证',
        help_text='用户是否已通过手机或邮箱验证',
        db_comment='是否已验证：1-已验证，0-未验证'
    )
    
    is_premium = models.BooleanField(
        default=False,
        verbose_name='是否为高级用户',
        help_text='高级用户享有更多功能权限',
        db_comment='是否为高级用户：1-是，0-否'
    )
    
    # 登录相关
    last_login_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='最后登录IP',
        db_comment='最后登录IP地址'
    )
    
    login_count = models.PositiveIntegerField(
        default=0,
        verbose_name='登录次数',
        db_comment='登录次数'
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active', 'is_verified']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        """返回用户的字符串表示"""
        return self.nickname or self.username
    
    def get_display_name(self):
        """获取用户显示名称"""
        return self.nickname or self.username or self.phone
    
    def get_full_name(self):
        """获取用户全名"""
        if self.first_name and self.last_name:
            return f"{self.last_name}{self.first_name}"
        return self.get_display_name()
    
    def increment_login_count(self):
        """增加登录次数"""
        self.login_count += 1
        self.save(update_fields=['login_count'])


class UserProfile(BaseModel):
    """
    用户配置模型
    
    存储用户的个性化配置信息。
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='用户',
        db_comment='关联用户ID'
    )
    
    # 隐私设置
    privacy_level = models.CharField(
        max_length=20,
        choices=[
            ('public', '公开'),
            ('friends', '仅好友'),
            ('private', '私密'),
        ],
        default='friends',
        verbose_name='隐私级别',
        db_comment='隐私级别：public-公开，friends-仅好友，private-私密'
    )
    
    # 通知设置
    email_notifications = models.BooleanField(
        default=True,
        verbose_name='邮件通知',
        db_comment='是否开启邮件通知：1-开启，0-关闭'
    )
    
    sms_notifications = models.BooleanField(
        default=True,
        verbose_name='短信通知',
        db_comment='是否开启短信通知：1-开启，0-关闭'
    )
    
    # 界面设置
    theme = models.CharField(
        max_length=20,
        choices=[
            ('light', '浅色主题'),
            ('dark', '深色主题'),
            ('auto', '自动'),
        ],
        default='light',
        verbose_name='界面主题',
        db_comment='界面主题：light-浅色，dark-深色，auto-自动'
    )
    
    language = models.CharField(
        max_length=10,
        choices=[
            ('zh-hans', '简体中文'),
            ('zh-hant', '繁体中文'),
            ('en', 'English'),
        ],
        default='zh-hans',
        verbose_name='界面语言',
        db_comment='界面语言：zh-hans-简体中文，zh-hant-繁体中文，en-英文'
    )
    
    # 功能设置
    auto_save = models.BooleanField(
        default=True,
        verbose_name='自动保存',
        db_comment='是否开启自动保存：1-开启，0-关闭'
    )
    
    show_tips = models.BooleanField(
        default=True,
        verbose_name='显示提示',
        db_comment='是否显示操作提示：1-显示，0-不显示'
    )
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户配置'
        verbose_name_plural = '用户配置'
    
    def __str__(self):
        return f"{self.user.get_display_name()}的配置"


class UserLoginLog(BaseModel):
    """
    用户登录日志模型
    
    记录用户的登录历史。
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_logs',
        verbose_name='用户',
        db_comment='关联用户ID'
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name='IP地址',
        db_comment='登录IP地址'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='用户代理',
        db_comment='浏览器用户代理字符串'
    )
    
    login_type = models.CharField(
        max_length=20,
        choices=[
            ('password', '密码登录'),
            ('sms', '短信登录'),
            ('email', '邮箱登录'),
            ('social', '第三方登录'),
        ],
        default='password',
        verbose_name='登录方式',
        db_comment='登录方式：password-密码，sms-短信，email-邮箱，social-第三方'
    )
    
    is_success = models.BooleanField(
        default=True,
        verbose_name='是否成功',
        db_comment='登录是否成功：1-成功，0-失败'
    )
    
    failure_reason = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='失败原因',
        db_comment='登录失败原因'
    )
    
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='登录地点',
        db_comment='登录地理位置'
    )
    
    class Meta:
        db_table = 'user_login_logs'
        verbose_name = '登录日志'
        verbose_name_plural = '登录日志'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['is_success']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        status = '成功' if self.is_success else '失败'
        return f"{self.user.get_display_name()} - {status} - {self.created_at}"