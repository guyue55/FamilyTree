"""
Family应用Schema定义

该文件定义了Family应用的所有Schema类。
遵循Django Ninja最佳实践和Google Python Style Guide。
"""

from datetime import datetime
from typing import Optional, List, Any, Dict
from django.contrib.auth import get_user_model
from enum import Enum
from ninja import Schema, Field, ModelSchema, FilterSchema
from ninja.files import UploadedFile
from pydantic import field_validator, create_model, ValidationInfo, model_validator, EmailStr
from .models import Family, FamilySettings, FamilyInvitation
from apps.common.schemas import PaginationQuerySchema
from apps.common.schemas import PaginatedApiResponseSchema

User = get_user_model()

# ==================== 枚举定义 ====================

class FamilyVisibility(str, Enum):
    """家族可见性枚举"""
    PUBLIC = "public"
    FAMILY = "family"
    PRIVATE = "private"

class InvitationStatus(str, Enum):
    """邀请状态枚举"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class TreeLayout(str, Enum):
    """族谱布局枚举"""
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    RADIAL = "radial"

class ExportFormat(str, Enum):
    """导出格式枚举"""
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    PDF = "pdf"

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

# ==================== 查询参数Schema ====================

class FamilyFilterSchema(FilterSchema):
    """家族查询过滤Schema"""

    keyword: Optional[str] = Field(None, description="搜索关键词")
    visibility: Optional[FamilyVisibility] = Field(None, description="可见性筛选")
    is_active: Optional[bool] = Field(None, description="是否激活")
    allow_join: Optional[bool] = Field(None, description="是否允许加入")
    member_count_min: Optional[int] = Field(None, ge=0, description="最少成员数")
    member_count_max: Optional[int] = Field(None, ge=0, description="最多成员数")
    created_date_start: Optional[datetime] = Field(None, description="创建开始时间")
    created_date_end: Optional[datetime] = Field(None, description="创建结束时间")
    tags: Optional[str] = Field(None, description="标签筛选")
    origin_location: Optional[str] = Field(None, description="起源地筛选")

# 分页Schema已移至apps.common.schemas，请使用PaginationQuerySchema

# ==================== ModelSchema定义 ====================

class FamilyModelSchema(ModelSchema):
    """家族模型Schema - 自动映射Django Model"""
    
    class Meta:
        model = Family
        fields = "__all__"

class FamilySettingsModelSchema(ModelSchema):
    """家族设置模型Schema - 自动映射Django Model"""
    
    class Meta:
        model = FamilySettings
        fields = "__all__"

class FamilyInvitationModelSchema(ModelSchema):
    """家族邀请模型Schema - 自动映射Django Model"""
    
    class Meta:
        model = FamilyInvitation
        fields = "__all__"

# ==================== 动态Schema生成 ====================

def create_family_schema(fields: List[str], base_schema=None):
    """动态创建家族Schema"""
    if base_schema is None:
        base_schema = FamilyModelSchema

    field_definitions = {}
    for field_name in fields:
        if hasattr(base_schema, field_name):
            field_definitions[field_name] = getattr(base_schema, field_name)

    return create_model('DynamicFamilySchema', **field_definitions, __base__=Schema)

# ==================== 家族相关Schema ====================

class FamilyBaseSchema(Schema, BaseConfig):
    """家族基础信息Schema"""

    name: str = Field(..., min_length=2, max_length=100, description="家族名称")
    description: Optional[str] = Field(None, max_length=1000, description="家族描述")
    visibility: FamilyVisibility = Field(FamilyVisibility.FAMILY, description="可见性设置")
    allow_join: bool = Field(True, description="是否允许加入")
    tags: Optional[str] = Field(None, max_length=200, description="家族标签")
    origin_location: Optional[str] = Field(None, max_length=100, description="起源地")
    motto: Optional[str] = Field(None, max_length=200, description="家族座右铭")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str, info: ValidationInfo) -> str:
        """
        验证家族名称

        Args:
            v: 家族名称
            info: 验证信息对象

        Returns:
            验证通过的家族名称（去除首尾空格）

        Raises:
            ValueError: 当家族名称为空时
        """
        if not v.strip():
            raise ValueError('家族名称不能为空')
        return v.strip()

# 使用ModelSchema自动生成响应Schema
FamilyResponseSchema = FamilyModelSchema

# 动态生成列表响应Schema
FamilyListResponseSchema = create_family_schema([
    'id', 'name', 'description', 'avatar', 'member_count',
    'generation_count', 'visibility', 'is_active', 'allow_join', 'created_at'
])

# 创建和更新Schema使用部分字段
class FamilyCreateSchema(FamilyBaseSchema):
    """创建家族Schema"""
    # 添加数据库模型中的必需字段，提供默认值
    is_active: bool = Field(True, description="是否激活")
    member_count: int = Field(0, description="成员数量")
    generation_count: int = Field(0, description="世代数量")

class FamilyUpdateSchema(Schema, BaseConfig):
    """更新家族Schema - 所有字段可选"""

    name: Optional[str] = Field(None, min_length=2, max_length=100, description="家族名称")
    description: Optional[str] = Field(None, max_length=1000, description="家族描述")
    visibility: Optional[FamilyVisibility] = Field(None, description="可见性设置")
    allow_join: Optional[bool] = Field(None, description="是否允许加入")
    tags: Optional[str] = Field(None, max_length=200, description="家族标签")
    origin_location: Optional[str] = Field(None, max_length=100, description="起源地")
    motto: Optional[str] = Field(None, max_length=200, description="家族座右铭")
    is_active: Optional[bool] = Field(None, description="是否激活")

# ==================== 家族设置Schema ====================

class FamilySettingsSchema(Schema, BaseConfig):
    """家族设置Schema"""

    tree_layout: TreeLayout = Field(TreeLayout.VERTICAL, description="族谱布局")
    default_generations: int = Field(5, ge=1, le=20, description="默认显示世代")
    show_photos: bool = Field(True, description="显示照片")
    show_birth_dates: bool = Field(True, description="显示出生日期")
    show_death_dates: bool = Field(True, description="显示死亡日期")
    show_occupation: bool = Field(False, description="显示职业")
    theme_color: str = Field('#1890ff', pattern=r'^#[0-9A-Fa-f]{6}$', description="主题颜色")
    font_family: str = Field('default', description="字体族")
    theme: str = Field('default', description="主题")
    font_size: int = Field(14, ge=10, le=24, description="字体大小")
    privacy_level: str = Field('family', description="隐私级别")
    require_approval: bool = Field(True, description="需要审批")
    allow_member_invite: bool = Field(True, description="允许成员邀请")
    enable_notifications: bool = Field(True, description="启用通知")
    email_notifications: bool = Field(True, description="邮件通知")
    push_notifications: bool = Field(True, description="推送通知")
    notify_new_member: bool = Field(True, description="新成员通知")
    notify_tree_update: bool = Field(True, description="族谱更新通知")

# 使用ModelSchema自动生成响应Schema
FamilySettingsResponseSchema = FamilySettingsModelSchema

# ==================== 家族邀请Schema ====================

class FamilyInvitationCreateSchema(Schema, BaseConfig):
    """创建家族邀请Schema"""

    invitee_id: Optional[int] = Field(None, description="被邀请者用户ID")
    invitee_email: Optional[EmailStr] = Field(None, description="被邀请者邮箱")
    invitee_phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="被邀请者手机号")
    invitee_name: str = Field(..., max_length=50, description="被邀请者姓名")
    message: Optional[str] = Field(None, max_length=500, description="邀请消息")

    @field_validator('invitee_email', 'invitee_phone')
    @classmethod
    def validate_contact_info(cls, v, info: ValidationInfo):
        """
        验证联系方式

        Args:
            v: 字段值（邮箱或手机号）
            info: 验证信息对象

        Returns:
            验证通过的字段值

        Raises:
            ValueError: 当联系方式不完整时
        """
        field_name = info.field_name
        # 在Pydantic v2中，我们需要通过model validation来访问其他字段
        # 这里我们只验证当前字段的格式，跨字段验证应该在model_validator中进行
        return v

    @model_validator(mode='after')
    def validate_contact_required(self):
        """
        验证至少提供一种联系方式

        Returns:
            验证通过的模型实例

        Raises:
            ValueError: 当没有提供任何联系方式时
        """
        if not any([self.invitee_id, self.invitee_email, self.invitee_phone]):
            raise ValueError('用户ID、邮箱和手机号至少需要提供一个')
        return self

class FamilyInvitationProcessSchema(Schema, BaseConfig):
    """处理家族邀请Schema"""

    action: str = Field(..., description="处理动作", pattern=r'^(accept|reject)$')
    rejection_reason: Optional[str] = Field(None, max_length=200, description="拒绝原因")

# 使用ModelSchema自动生成响应Schema
FamilyInvitationResponseSchema = FamilyInvitationModelSchema

# ==================== 统计和其他Schema ====================

class FamilyStatisticsSchema(Schema, BaseConfig):
    """家族统计Schema"""

    total_families: int = Field(..., description="总家族数")
    active_families: int = Field(..., description="活跃家族数")
    public_families: int = Field(..., description="公开家族数")
    total_members: int = Field(..., description="总成员数")
    average_members_per_family: float = Field(..., description="平均每家族成员数")
    families_created_today: int = Field(..., description="今日新增家族")
    families_created_this_week: int = Field(..., description="本周新增家族")
    families_created_this_month: int = Field(..., description="本月新增家族")
    top_families_by_members: List[Dict[str, Any]] = Field(..., description="成员数最多的家族")

class FamilyMemberRoleSchema(Schema, BaseConfig):
    """家族成员角色Schema"""

    member_id: int = Field(..., description="成员ID")
    role: str = Field(..., description="角色")
    permissions: List[str] = Field(..., description="权限列表")
    assigned_at: datetime = Field(..., description="分配时间")
    assigned_by: int = Field(..., description="分配者ID")

class FamilyTreeConfigSchema(Schema, BaseConfig):
    """家族树配置Schema"""

    layout: TreeLayout = Field(TreeLayout.VERTICAL, description="布局方式")
    generations: int = Field(5, ge=1, le=20, description="显示世代数")
    show_photos: bool = Field(True, description="显示照片")
    show_dates: bool = Field(True, description="显示日期")
    show_relationships: bool = Field(True, description="显示关系")
    theme: str = Field('default', description="主题")
    zoom_level: float = Field(1.0, ge=0.1, le=5.0, description="缩放级别")

class FamilyExportSchema(Schema, BaseConfig):
    """家族导出Schema"""

    family_id: int = Field(..., description="家族ID")
    export_format: ExportFormat = Field(ExportFormat.JSON, description="导出格式")
    include_photos: bool = Field(False, description="包含照片")
    include_relationships: bool = Field(True, description="包含关系")
    include_settings: bool = Field(False, description="包含设置")
    generations: Optional[int] = Field(None, ge=1, le=20, description="导出世代数")

class FamilyImportSchema(Schema, BaseConfig):
    """家族导入Schema"""

    file: UploadedFile = Field(..., description="导入文件")
    merge_strategy: str = Field('skip', description="合并策略")
    auto_create_relationships: bool = Field(True, description="自动创建关系")
    validate_data: bool = Field(True, description="验证数据")

class FamilyJoinRequestSchema(Schema, BaseConfig):
    """加入家族申请Schema"""

    family_id: int = Field(..., description="家族ID")
    message: Optional[str] = Field(None, max_length=500, description="申请消息")
    relationship_to_family: Optional[str] = Field(None, max_length=100, description="与家族的关系")

class FamilyJoinRequestResponseSchema(Schema, BaseConfig):
    """加入家族申请响应Schema"""

    id: int = Field(..., description="申请ID")
    family_id: int = Field(..., description="家族ID")
    applicant_id: int = Field(..., description="申请者ID")
    message: Optional[str] = Field(None, description="申请消息")
    relationship_to_family: Optional[str] = Field(None, description="与家族的关系")
    status: str = Field(..., description="申请状态")
    processed_by: Optional[int] = Field(None, description="处理者ID")
    processed_at: Optional[datetime] = Field(None, description="处理时间")
    created_at: datetime = Field(..., description="申请时间")

class FamilyActivityLogSchema(Schema, BaseConfig):
    """家族活动日志Schema"""

    id: int = Field(..., description="日志ID")
    family_id: int = Field(..., description="家族ID")
    user_id: int = Field(..., description="用户ID")
    action: str = Field(..., description="操作类型")
    description: str = Field(..., description="操作描述")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    created_at: datetime = Field(..., description="操作时间")

# ==================== 路径和查询参数Schema ====================

class FamilyPathSchema(Schema):
    """家族路径参数Schema"""

    family_id: int = Field(..., description="家族ID", gt=0)

class InvitationPathSchema(Schema):
    """邀请路径参数Schema"""

    invitation_id: int = Field(..., description="邀请ID", gt=0)

# ==================== 组合查询Schema ====================

# 导入统一的分页Schema

class FamilySearchQuerySchema(FamilyFilterSchema, PaginationQuerySchema):
    """家族搜索查询Schema - 组合过滤和分页"""
    pass

class FamilySearchSchema(FamilyFilterSchema):
    """家族搜索Schema"""
    pass

class FamilyQuerySchema(PaginationQuerySchema):
    """家族查询Schema"""
    search: Optional[str] = Field(None, description="搜索关键词")
    visibility: Optional[str] = Field(None, pattern=r"^(public|private|members_only)$", description="可见性过滤")
    allow_join: Optional[bool] = Field(None, description="是否允许加入过滤")
    tags: Optional[List[str]] = Field(None, description="标签过滤")
    ordering: Optional[str] = Field("-created_at", description="排序字段")

class PublicFamilyQuerySchema(PaginationQuerySchema):
    """公开家族查询Schema"""
    search: Optional[str] = Field(None, description="搜索关键词")
    tags: Optional[List[str]] = Field(None, description="标签过滤")
    allow_join: Optional[bool] = Field(None, description="是否允许加入过滤")
    ordering: Optional[str] = Field("-member_count", description="排序字段")

# ==================== 响应Schema ====================
# 注意：MessageResponseSchema 已移至 apps.common.schemas
# 请使用: from apps.common.schemas import MessageResponseSchema

# 使用通用分页响应Schema

# 家族专用分页响应类型别名
PaginatedFamilyResponseSchema = PaginatedApiResponseSchema[FamilyResponseSchema]

# ==================== 导出的Schema列表 ====================

__all__ = [
    # 枚举
    'FamilyVisibility', 'InvitationStatus', 'TreeLayout', 'ExportFormat',

    # 通用Schema (注意：部分已移至 apps.common.schemas)
    'PaginatedFamilyResponseSchema',

    # 过滤和分页
    'FamilyFilterSchema', 'FamilySearchQuerySchema', 'FamilySearchSchema',

    # 模型Schema
    'FamilyModelSchema', 'FamilySettingsModelSchema', 'FamilyInvitationModelSchema',

    # 家族Schema
    'FamilyBaseSchema', 'FamilyCreateSchema', 'FamilyUpdateSchema',
    'FamilyResponseSchema', 'FamilyListResponseSchema',

    # 设置Schema
    'FamilySettingsSchema', 'FamilySettingsResponseSchema',

    # 邀请Schema
    'FamilyInvitationCreateSchema', 'FamilyInvitationProcessSchema', 'FamilyInvitationResponseSchema',

    # 其他Schema
    'FamilyStatisticsSchema', 'FamilyMemberRoleSchema', 'FamilyTreeConfigSchema',
    'FamilyExportSchema', 'FamilyImportSchema', 'FamilyJoinRequestSchema',
    'FamilyJoinRequestResponseSchema', 'FamilyActivityLogSchema',

    # 路径参数Schema
    'FamilyPathSchema', 'InvitationPathSchema',

    # 工具函数
    'create_family_schema',
]