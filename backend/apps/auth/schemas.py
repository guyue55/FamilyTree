"""
认证相关Schema定义

该文件定义了认证模块的所有Schema类。
遵循Django Ninja最佳实践和Google Python Style Guide。
"""

from typing import Optional, List
from datetime import datetime
from django.contrib.auth import get_user_model
from enum import Enum
from ninja import Schema, Field
from pydantic import field_validator, model_validator, ValidationInfo, EmailStr

User = get_user_model()

# ==================== 枚举定义 ====================

class TokenType(str, Enum):
    """令牌类型枚举"""
    BEARER = "Bearer"
    JWT = "JWT"

class LoginType(str, Enum):
    """登录方式枚举"""
    USERNAME = "username"
    EMAIL = "email"
    PHONE = "phone"

# ==================== 基础配置类 ====================

class BaseConfig:
    """基础Schema配置"""

    class Config:
        # 允许使用枚举
        use_enum_values = True
        # 字段别名生成器
        alias_generator = None
        # 允许字段填充
        allow_population_by_field_name = True
        # JSON编码器
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

# ==================== 用户认证Schema ====================

class UserRegisterSchema(Schema, BaseConfig):
    """用户注册请求Schema"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, max_length=128, description="密码")
    confirm_password: str = Field(..., description="确认密码")
    first_name: Optional[str] = Field(None, max_length=30, description="名字")
    last_name: Optional[str] = Field(None, max_length=30, description="姓氏")

    @field_validator('username')
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
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str, info: ValidationInfo) -> str:
        """
        验证密码强度

        Args:
            v: 密码
            info: 验证信息对象

        Returns:
            验证通过的密码

        Raises:
            ValueError: 当密码不符合要求时
        """
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v

    @model_validator(mode='after')
    def validate_passwords_match(self):
        """
        验证密码确认

        Returns:
            验证通过的模型实例

        Raises:
            ValueError: 当密码确认不匹配时
        """
        if self.password != self.confirm_password:
            raise ValueError('密码确认不匹配')
        return self

class UserLoginSchema(Schema, BaseConfig):
    """用户登录请求Schema"""

    username: str = Field(..., description="用户名、邮箱或手机号")
    password: str = Field(..., description="密码")
    remember_me: bool = Field(False, description="记住我")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str, info: ValidationInfo) -> str:
        """
        验证用户名

        Args:
            v: 用户名
            info: 验证信息对象

        Returns:
            验证通过的用户名

        Raises:
            ValueError: 当用户名为空时
        """
        if not v.strip():
            raise ValueError('用户名不能为空')
        return v.strip()

class RefreshTokenSchema(Schema, BaseConfig):
    """刷新令牌请求Schema"""

    refresh_token: str = Field(..., description="刷新令牌")

    @field_validator('refresh_token')
    @classmethod
    def validate_refresh_token(cls, v: str, info: ValidationInfo) -> str:
        """
        验证刷新令牌

        Args:
            v: 刷新令牌
            info: 验证信息对象

        Returns:
            验证通过的刷新令牌

        Raises:
            ValueError: 当令牌为空时
        """
        if not v.strip():
            raise ValueError('刷新令牌不能为空')
        return v.strip()

# ==================== 用户信息Schema ====================

class UserInfoSchema(Schema, BaseConfig):
    """用户基本信息Schema"""

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱地址")
    first_name: Optional[str] = Field(None, description="名字")
    last_name: Optional[str] = Field(None, description="姓氏")
    is_active: bool = Field(..., description="是否激活")
    is_staff: bool = Field(False, description="是否为管理员")
    date_joined: str = Field(..., description="注册时间")
    last_login: Optional[str] = Field(None, description="最后登录时间")

# ==================== 响应Schema ====================

class TokenResponseSchema(Schema, BaseConfig):
    """令牌响应Schema"""

    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: TokenType = Field(TokenType.BEARER, description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")

class LoginResponseSchema(TokenResponseSchema):
    """登录成功响应Schema"""

    user: UserInfoSchema = Field(..., description="用户信息")

class RegisterResponseSchema(Schema, BaseConfig):
    """注册成功响应Schema"""

    user: UserInfoSchema = Field(..., description="用户信息")
    message: str = Field(..., description="响应消息")

# ==================== 密码管理Schema ====================

class PasswordChangeSchema(Schema, BaseConfig):
    """修改密码Schema"""

    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str, info: ValidationInfo) -> str:
        """
        验证新密码强度

        Args:
            v: 新密码
            info: 验证信息对象

        Returns:
            验证通过的新密码

        Raises:
            ValueError: 当密码不符合要求时
        """
        if not any(c.isupper() for c in v):
            raise ValueError('新密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('新密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('新密码必须包含至少一个数字')
        return v

    @model_validator(mode='after')
    def validate_passwords_match(self):
        """
        验证密码确认

        Returns:
            验证通过的模型实例

        Raises:
            ValueError: 当密码确认不匹配时
        """
        if self.new_password != self.confirm_password:
            raise ValueError('密码确认不匹配')
        return self

class PasswordResetSchema(Schema, BaseConfig):
    """重置密码请求Schema"""

    email: EmailStr = Field(..., description="邮箱地址")

class PasswordResetConfirmSchema(Schema, BaseConfig):
    """确认重置密码Schema"""

    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str, info: ValidationInfo) -> str:
        """
        验证新密码强度

        Args:
            v: 新密码
            info: 验证信息对象

        Returns:
            验证通过的新密码

        Raises:
            ValueError: 当密码不符合要求时
        """
        if not any(c.isupper() for c in v):
            raise ValueError('新密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('新密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('新密码必须包含至少一个数字')
        return v

    @model_validator(mode='after')
    def validate_passwords_match(self):
        """
        验证密码确认

        Returns:
            验证通过的模型实例

        Raises:
            ValueError: 当密码确认不匹配时
        """
        if self.new_password != self.confirm_password:
            raise ValueError('密码确认不匹配')
        return self

# ==================== 导出列表 ====================

__all__ = [
    # 枚举
    'TokenType',
    'LoginType',

    # 请求Schema
    'UserRegisterSchema',
    'UserLoginSchema',
    'RefreshTokenSchema',
    'PasswordChangeSchema',
    'PasswordResetSchema',
    'PasswordResetConfirmSchema',

    # 响应Schema
    'UserInfoSchema',
    'TokenResponseSchema',
    'LoginResponseSchema',
    'RegisterResponseSchema',
]