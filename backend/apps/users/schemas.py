"""
用户模块 Django Ninja Schema 定义

该模块定义了用户相关的输入输出数据结构，用于API接口的数据验证和序列化。
遵循Django Ninja最佳实践和Google Python Style Guide。
"""

from datetime import datetime, date
from typing import Optional
from ninja import Schema, Field
from pydantic import EmailStr, field_validator, model_validator, ValidationInfo


class UserBaseSchema(Schema):
    """用户基础信息Schema"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    gender: Optional[str] = Field("unknown", description="性别")
    birth_date: Optional[date] = Field(None, description="出生日期")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


class UserCreateSchema(UserBaseSchema):
    """创建用户Schema"""

    password: str = Field(..., min_length=8, max_length=128, description="密码")
    confirm_password: str = Field(..., description="确认密码")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str, info: ValidationInfo) -> str:
        """
        验证用户名格式

        Args:
            v: 用户名
            info: 验证信息对象

        Returns:
            验证通过的用户名

        Raises:
            ValueError: 当用户名格式不正确时
        """
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("用户名只能包含字母、数字、下划线和连字符")
        return v

    @model_validator(mode="after")
    def validate_passwords_match(self):
        """
        验证密码确认

        Returns:
            验证通过的模型实例

        Raises:
            ValueError: 当密码确认不匹配时
        """
        if self.password != self.confirm_password:
            raise ValueError("密码确认不匹配")
        return self


class UserUpdateSchema(Schema):
    """更新用户Schema"""

    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    gender: Optional[str] = Field(None, description="性别")
    birth_date: Optional[date] = Field(None, description="出生日期")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


class UserResponseSchema(Schema):
    """用户响应Schema"""

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱地址")
    phone: str = Field(..., description="手机号")
    nickname: Optional[str] = Field(None, description="昵称")
    gender: str = Field(..., description="性别")
    birth_date: Optional[date] = Field(None, description="出生日期")
    bio: Optional[str] = Field(None, description="个人简介")
    avatar: Optional[str] = Field(None, description="头像URL")
    is_verified: bool = Field(..., description="是否已验证")
    is_premium: bool = Field(..., description="是否为高级用户")
    is_active: bool = Field(..., description="是否激活")
    date_joined: datetime = Field(..., description="注册时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    login_count: int = Field(..., description="登录次数")


class UserListResponseSchema(Schema):
    """用户列表响应Schema"""

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    is_verified: bool = Field(..., description="是否已验证")
    is_premium: bool = Field(..., description="是否为高级用户")
    date_joined: datetime = Field(..., description="注册时间")


class UserLoginSchema(Schema):
    """用户登录Schema"""

    username: str = Field(..., description="用户名或邮箱或手机号")
    password: str = Field(..., description="密码")
    remember_me: bool = Field(False, description="记住我")


class UserLoginResponseSchema(Schema):
    """用户登录响应Schema"""

    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("Bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")
    user: UserResponseSchema = Field(..., description="用户信息")


class PasswordChangeSchema(Schema):
    """修改密码Schema"""

    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")

    @model_validator(mode="after")
    def validate_passwords_match(self):
        """
        验证密码确认

        Returns:
            验证通过的模型实例

        Raises:
            ValueError: 当新密码确认不匹配时
        """
        if self.new_password != self.confirm_password:
            raise ValueError("新密码确认不匹配")
        return self


class PasswordResetSchema(Schema):
    """重置密码Schema"""

    email: EmailStr = Field(..., description="邮箱地址")


class PasswordResetConfirmSchema(Schema):
    """确认重置密码Schema"""

    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")

    @model_validator(mode="after")
    def validate_passwords_match(self):
        """
        验证密码确认

        Returns:
            验证通过的模型实例

        Raises:
            ValueError: 当新密码确认不匹配时
        """
        if self.new_password != self.confirm_password:
            raise ValueError("新密码确认不匹配")
        return self


class UserProfileSchema(Schema):
    """用户配置Schema"""

    privacy_level: str = Field("friends", description="隐私级别")
    email_notifications: bool = Field(True, description="邮件通知")
    sms_notifications: bool = Field(True, description="短信通知")
    theme: str = Field("light", description="界面主题")
    language: str = Field("zh-hans", description="界面语言")
    auto_save: bool = Field(True, description="自动保存")
    show_tips: bool = Field(True, description="显示提示")


class UserProfileResponseSchema(UserProfileSchema):
    """用户配置响应Schema"""

    id: int = Field(..., description="配置ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class UserLoginLogSchema(Schema):
    """用户登录日志Schema"""

    id: int = Field(..., description="日志ID")
    user_id: int = Field(..., description="用户ID")
    ip_address: str = Field(..., description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    login_type: str = Field(..., description="登录方式")
    is_success: bool = Field(..., description="是否成功")
    failure_reason: Optional[str] = Field(None, description="失败原因")
    location: Optional[str] = Field(None, description="登录地点")
    created_at: datetime = Field(..., description="登录时间")


from apps.common.schemas import PaginationQuerySchema


class UserQuerySchema(PaginationQuerySchema):
    """用户查询Schema"""

    search: Optional[str] = Field(None, description="搜索关键词")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_verified: Optional[bool] = Field(None, description="是否已验证")
    is_premium: Optional[bool] = Field(None, description="是否为高级用户")
    ordering: Optional[str] = Field("-date_joined", description="排序字段")


class UserSearchSchema(PaginationQuerySchema):
    """用户搜索Schema"""

    keyword: Optional[str] = Field(None, description="搜索关键词")
    gender: Optional[str] = Field(None, description="性别筛选")
    is_verified: Optional[bool] = Field(None, description="是否已验证")
    is_premium: Optional[bool] = Field(None, description="是否为高级用户")
    date_joined_start: Optional[date] = Field(None, description="注册开始时间")
    date_joined_end: Optional[date] = Field(None, description="注册结束时间")


class UserStatisticsSchema(Schema):
    """用户统计Schema"""

    total_users: int = Field(..., description="总用户数")
    verified_users: int = Field(..., description="已验证用户数")
    premium_users: int = Field(..., description="高级用户数")
    active_users: int = Field(..., description="活跃用户数")
    new_users_today: int = Field(..., description="今日新增用户")
    new_users_this_week: int = Field(..., description="本周新增用户")
    new_users_this_month: int = Field(..., description="本月新增用户")
