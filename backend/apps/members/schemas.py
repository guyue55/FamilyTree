"""
成员模块 Django Ninja Schema 定义

该模块定义了家族成员相关的输入输出数据结构，用于API接口的数据验证和序列化。
遵循Django Ninja最佳实践和Google Python Style Guide。
"""

from datetime import datetime, date
from typing import Optional, List
from ninja import Schema, Field
from pydantic import EmailStr, model_validator


class MemberBaseSchema(Schema):
    """成员基础信息Schema"""

    name: str = Field(..., min_length=1, max_length=50, description="成员姓名")
    english_name: Optional[str] = Field(None, max_length=100, description="英文名")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    gender: str = Field("unknown", description="性别")
    birth_date: Optional[date] = Field(None, description="出生日期")
    death_date: Optional[date] = Field(None, description="去世日期")
    is_alive: bool = Field(True, description="是否在世")
    birth_place: Optional[str] = Field(None, max_length=100, description="出生地")
    current_location: Optional[str] = Field(None, max_length=100, description="现居地")
    occupation: Optional[str] = Field(None, max_length=100, description="职业")
    company: Optional[str] = Field(None, max_length=100, description="工作单位")
    education: Optional[str] = Field(None, max_length=100, description="教育背景")
    phone: Optional[str] = Field(None, max_length=20, description="电话号码")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    bio: Optional[str] = Field(None, max_length=1000, description="个人简介")
    generation: int = Field(1, ge=1, le=20, description="世代")
    sort_order: int = Field(1, ge=1, description="排序序号")
    visibility: str = Field("family", description="可见性")


class MemberCreateSchema(MemberBaseSchema):
    """创建成员Schema"""

    family_id: int = Field(..., description="家族ID")
    user_id: Optional[int] = Field(None, description="关联用户ID")

    @model_validator(mode="after")
    def validate_member_constraints(self):
        """验证成员约束"""
        # 验证去世日期
        if self.death_date and self.birth_date and self.death_date < self.birth_date:
            raise ValueError("去世日期不能早于出生日期")

        # 验证生存状态
        if not self.is_alive and not self.death_date:
            raise ValueError("已故成员必须设置去世日期")

        return self


class MemberUpdateSchema(Schema):
    """更新成员Schema"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=50, description="成员姓名"
    )
    english_name: Optional[str] = Field(None, max_length=100, description="英文名")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    gender: Optional[str] = Field(None, description="性别")
    birth_date: Optional[date] = Field(None, description="出生日期")
    death_date: Optional[date] = Field(None, description="去世日期")
    is_alive: Optional[bool] = Field(None, description="是否在世")
    birth_place: Optional[str] = Field(None, max_length=100, description="出生地")
    current_location: Optional[str] = Field(None, max_length=100, description="现居地")
    occupation: Optional[str] = Field(None, max_length=100, description="职业")
    company: Optional[str] = Field(None, max_length=100, description="工作单位")
    education: Optional[str] = Field(None, max_length=100, description="教育背景")
    phone: Optional[str] = Field(None, max_length=20, description="电话号码")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    bio: Optional[str] = Field(None, max_length=1000, description="个人简介")
    generation: Optional[int] = Field(None, ge=1, le=20, description="世代")
    sort_order: Optional[int] = Field(None, ge=1, description="排序序号")
    visibility: Optional[str] = Field(None, description="可见性")
    is_admin: Optional[bool] = Field(None, description="是否为管理员")


class MemberResponseSchema(Schema):
    """成员响应Schema"""

    id: int = Field(..., description="成员ID")
    family_id: int = Field(..., description="家族ID")
    user_id: Optional[int] = Field(None, description="关联用户ID")
    name: str = Field(..., description="成员姓名")
    english_name: Optional[str] = Field(None, description="英文名")
    nickname: Optional[str] = Field(None, description="昵称")
    gender: str = Field(..., description="性别")
    birth_date: Optional[date] = Field(None, description="出生日期")
    death_date: Optional[date] = Field(None, description="去世日期")
    is_alive: bool = Field(..., description="是否在世")
    birth_place: Optional[str] = Field(None, description="出生地")
    current_location: Optional[str] = Field(None, description="现居地")
    occupation: Optional[str] = Field(None, description="职业")
    company: Optional[str] = Field(None, description="工作单位")
    education: Optional[str] = Field(None, description="教育背景")
    phone: Optional[str] = Field(None, description="电话号码")
    email: Optional[str] = Field(None, description="邮箱地址")
    avatar: Optional[str] = Field(None, description="头像URL")
    bio: Optional[str] = Field(None, description="个人简介")
    generation: int = Field(..., description="世代")
    sort_order: int = Field(..., description="排序序号")
    visibility: str = Field(..., description="可见性")
    is_admin: bool = Field(..., description="是否为管理员")
    joined_at: datetime = Field(..., description="加入时间")
    creator_id: int = Field(..., description="创建者ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class MemberListResponseSchema(Schema):
    """成员列表响应Schema"""

    id: int = Field(..., description="成员ID")
    family_id: int = Field(..., description="家族ID")
    name: str = Field(..., description="成员姓名")
    nickname: Optional[str] = Field(None, description="昵称")
    gender: str = Field(..., description="性别")
    birth_date: Optional[date] = Field(None, description="出生日期")
    is_alive: bool = Field(..., description="是否在世")
    avatar: Optional[str] = Field(None, description="头像URL")
    generation: int = Field(..., description="世代")
    sort_order: int = Field(..., description="排序序号")
    is_admin: bool = Field(..., description="是否为管理员")
    joined_at: datetime = Field(..., description="加入时间")


class FamilyMembershipSchema(Schema):
    """家族成员关系Schema"""

    user_id: int = Field(..., description="用户ID")
    family_id: int = Field(..., description="家族ID")
    member_id: int = Field(..., description="成员ID")
    role: str = Field("member", description="角色")
    can_edit_tree: bool = Field(False, description="可编辑族谱")
    can_add_member: bool = Field(False, description="可添加成员")
    can_edit_member: bool = Field(False, description="可编辑成员")
    can_delete_member: bool = Field(False, description="可删除成员")
    can_manage_media: bool = Field(False, description="可管理媒体")
    can_invite_member: bool = Field(True, description="可邀请成员")
    status: str = Field("active", description="状态")
    join_method: str = Field("invited", description="加入方式")


class FamilyMembershipResponseSchema(FamilyMembershipSchema):
    """家族成员关系响应Schema"""

    id: int = Field(..., description="关系ID")
    joined_at: datetime = Field(..., description="加入时间")
    last_active_at: datetime = Field(..., description="最后活跃时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class MemberNoteCreateSchema(Schema):
    """创建成员备注Schema"""

    member_id: int = Field(..., description="成员ID")
    content: str = Field(..., max_length=1000, description="备注内容")
    note_type: str = Field("general", description="备注类型")
    is_private: bool = Field(False, description="是否私有")
    visibility: str = Field("family", description="可见性")


class MemberNoteUpdateSchema(Schema):
    """更新成员备注Schema"""

    content: Optional[str] = Field(None, max_length=1000, description="备注内容")
    note_type: Optional[str] = Field(None, description="备注类型")
    is_private: Optional[bool] = Field(None, description="是否私有")
    visibility: Optional[str] = Field(None, description="可见性")


class MemberNoteResponseSchema(Schema):
    """成员备注响应Schema"""

    id: int = Field(..., description="备注ID")
    member_id: int = Field(..., description="成员ID")
    creator_id: int = Field(..., description="创建者ID")
    content: str = Field(..., description="备注内容")
    note_type: str = Field(..., description="备注类型")
    is_private: bool = Field(..., description="是否私有")
    visibility: str = Field(..., description="可见性")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


from apps.common.schemas import PaginationQuerySchema


class MemberSearchSchema(PaginationQuerySchema):
    """成员搜索Schema"""

    family_id: Optional[int] = Field(None, description="家族ID")
    keyword: Optional[str] = Field(None, description="搜索关键词")
    gender: Optional[str] = Field(None, description="性别筛选")
    generation: Optional[int] = Field(None, ge=1, le=20, description="世代筛选")
    is_alive: Optional[bool] = Field(None, description="是否在世")
    is_admin: Optional[bool] = Field(None, description="是否为管理员")
    birth_year_start: Optional[int] = Field(None, description="出生年份开始")
    birth_year_end: Optional[int] = Field(None, description="出生年份结束")
    location: Optional[str] = Field(None, description="地点筛选")
    occupation: Optional[str] = Field(None, description="职业筛选")


class MemberQuerySchema(PaginationQuerySchema):
    """成员查询Schema"""

    family_id: Optional[int] = Field(None, description="家族ID")
    search: Optional[str] = Field(None, description="搜索关键词")
    gender: Optional[str] = Field(None, description="性别筛选")
    generation: Optional[int] = Field(None, ge=1, le=20, description="世代筛选")
    is_alive: Optional[bool] = Field(None, description="是否在世")
    is_admin: Optional[bool] = Field(None, description="是否为管理员")
    ordering: Optional[str] = Field(None, description="排序字段")


class MemberStatisticsSchema(Schema):
    """成员统计Schema"""

    total_members: int = Field(..., description="总成员数")
    living_members: int = Field(..., description="在世成员数")
    deceased_members: int = Field(..., description="已故成员数")
    male_members: int = Field(..., description="男性成员数")
    female_members: int = Field(..., description="女性成员数")
    generation_distribution: List[dict] = Field(..., description="世代分布")
    age_distribution: List[dict] = Field(..., description="年龄分布")
    location_distribution: List[dict] = Field(..., description="地区分布")
    occupation_distribution: List[dict] = Field(..., description="职业分布")


class MemberTreeNodeSchema(Schema):
    """成员树节点Schema"""

    id: int = Field(..., description="成员ID")
    name: str = Field(..., description="成员姓名")
    nickname: Optional[str] = Field(None, description="昵称")
    gender: str = Field(..., description="性别")
    birth_date: Optional[date] = Field(None, description="出生日期")
    death_date: Optional[date] = Field(None, description="去世日期")
    is_alive: bool = Field(..., description="是否在世")
    avatar: Optional[str] = Field(None, description="头像URL")
    generation: int = Field(..., description="世代")
    sort_order: int = Field(..., description="排序序号")
    children: List["MemberTreeNodeSchema"] = Field([], description="子节点")
    spouses: List["MemberTreeNodeSchema"] = Field([], description="配偶")
    relationships: List[dict] = Field([], description="关系信息")


class MemberBatchCreateSchema(Schema):
    """批量创建成员Schema"""

    members: List[MemberCreateSchema] = Field(..., description="成员列表")
    auto_generate_relationships: bool = Field(False, description="自动生成关系")
    skip_duplicates: bool = Field(True, description="跳过重复")


class MemberBatchUpdateSchema(Schema):
    """批量更新成员Schema"""

    member_ids: List[int] = Field(..., description="成员ID列表")
    update_data: MemberUpdateSchema = Field(..., description="更新数据")


class MemberImportSchema(Schema):
    """成员导入Schema"""

    family_id: int = Field(..., description="家族ID")
    file_type: str = Field(..., description="文件类型")
    file_content: str = Field(..., description="文件内容")
    auto_create_relationships: bool = Field(False, description="自动创建关系")
    merge_strategy: str = Field("skip", description="合并策略")


class MemberExportSchema(Schema):
    """成员导出Schema"""

    family_id: int = Field(..., description="家族ID")
    export_format: str = Field("json", description="导出格式")
    include_photos: bool = Field(False, description="包含照片")
    include_notes: bool = Field(False, description="包含备注")
    include_relationships: bool = Field(True, description="包含关系")
    generation_filter: Optional[List[int]] = Field(None, description="世代筛选")
    gender_filter: Optional[List[str]] = Field(None, description="性别筛选")


class MemberValidationSchema(Schema):
    """成员验证Schema"""

    member_id: int = Field(..., description="成员ID")
    validation_type: str = Field(..., description="验证类型")
    validation_result: bool = Field(..., description="验证结果")
    validation_message: str = Field(..., description="验证消息")
    validation_details: Optional[dict] = Field(None, description="验证详情")


class MemberPermissionSchema(Schema):
    """成员权限Schema"""

    member_id: int = Field(..., description="成员ID")
    permissions: List[str] = Field(..., description="权限列表")
    role: str = Field(..., description="角色")
    granted_by: int = Field(..., description="授权者ID")
    granted_at: datetime = Field(..., description="授权时间")


class MemberActivityLogSchema(Schema):
    """成员活动日志Schema"""

    id: int = Field(..., description="日志ID")
    member_id: int = Field(..., description="成员ID")
    user_id: int = Field(..., description="用户ID")
    action: str = Field(..., description="操作类型")
    description: str = Field(..., description="操作描述")
    metadata: Optional[dict] = Field(None, description="元数据")
    created_at: datetime = Field(..., description="操作时间")


# 解决循环引用问题
MemberTreeNodeSchema.model_rebuild()
