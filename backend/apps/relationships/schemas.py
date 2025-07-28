"""
关系模块 Django Ninja Schema 定义

该模块定义了家庭关系相关的输入输出数据结构，用于API接口的数据验证和序列化。
遵循Django Ninja最佳实践和Google Python Style Guide。
"""

from datetime import datetime, date
from typing import Optional, List
from ninja import Schema, Field
from pydantic import field_validator, model_validator, ValidationInfo


class RelationshipBaseSchema(Schema):
    """关系基础信息Schema"""
    
    family_id: int = Field(..., description="家庭ID")
    from_member_id: int = Field(..., description="关系发起人ID")
    to_member_id: int = Field(..., description="关系接收人ID")
    relationship_type: str = Field(..., description="关系类型")
    relationship_detail: Optional[str] = Field(None, max_length=100, description="关系详情")
    confidence_level: int = Field(5, ge=1, le=10, description="可信度等级")
    start_date: Optional[date] = Field(None, description="关系开始日期")
    end_date: Optional[date] = Field(None, description="关系结束日期")
    notes: Optional[str] = Field(None, max_length=1000, description="备注信息")
    visibility: str = Field('family', description="可见性")


class RelationshipCreateSchema(RelationshipBaseSchema):
    """创建关系Schema"""
    
    @field_validator('to_member_id')
    @classmethod
    def validate_different_members(cls, v: int, info: ValidationInfo) -> int:
        """验证不能与自己建立关系"""
        # 注意：在field_validator中无法访问其他字段值
        # 这个验证应该在model_validator中进行
        return v
    
    @model_validator(mode='after')
    def validate_relationship_constraints(self):
        """验证关系约束"""
        # 验证不能与自己建立关系
        if self.to_member_id == self.from_member_id:
            raise ValueError('不能与自己建立关系')
        
        # 验证日期范围
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValueError('结束日期不能早于开始日期')
        
        return self


class RelationshipUpdateSchema(Schema):
    """更新关系Schema"""
    
    relationship_type: Optional[str] = Field(None, description="关系类型")
    relationship_detail: Optional[str] = Field(None, max_length=100, description="关系详情")
    confidence_level: Optional[int] = Field(None, ge=1, le=10, description="可信度等级")
    start_date: Optional[date] = Field(None, description="关系开始日期")
    end_date: Optional[date] = Field(None, description="关系结束日期")
    notes: Optional[str] = Field(None, max_length=1000, description="备注信息")
    visibility: Optional[str] = Field(None, description="可见性")
    is_active: Optional[bool] = Field(None, description="是否激活")


class RelationshipResponseSchema(Schema):
    """关系响应Schema"""
    
    id: int = Field(..., description="关系ID")
    family_id: int = Field(..., description="家庭ID")
    from_member_id: int = Field(..., description="关系发起人ID")
    to_member_id: int = Field(..., description="关系接收人ID")
    relationship_type: str = Field(..., description="关系类型")
    relationship_detail: Optional[str] = Field(None, description="关系详情")
    is_confirmed: bool = Field(..., description="是否已确认")
    confidence_level: int = Field(..., description="可信度等级")
    start_date: Optional[date] = Field(None, description="关系开始日期")
    end_date: Optional[date] = Field(None, description="关系结束日期")
    is_active: bool = Field(..., description="是否激活")
    notes: Optional[str] = Field(None, description="备注信息")
    visibility: str = Field(..., description="可见性")
    creator_id: int = Field(..., description="创建者ID")
    confirmed_by_id: Optional[int] = Field(None, description="确认者ID")
    confirmed_at: Optional[datetime] = Field(None, description="确认时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class RelationshipListResponseSchema(Schema):
    """关系列表响应Schema"""
    
    id: int = Field(..., description="关系ID")
    family_id: int = Field(..., description="家庭ID")
    from_member_id: int = Field(..., description="关系发起人ID")
    to_member_id: int = Field(..., description="关系接收人ID")
    relationship_type: str = Field(..., description="关系类型")
    relationship_detail: Optional[str] = Field(None, description="关系详情")
    is_confirmed: bool = Field(..., description="是否已确认")
    confidence_level: int = Field(..., description="可信度等级")
    is_active: bool = Field(..., description="是否激活")
    visibility: str = Field(..., description="可见性")
    created_at: datetime = Field(..., description="创建时间")


class RelationshipConfirmSchema(Schema):
    """确认关系Schema"""
    
    is_confirmed: bool = Field(..., description="是否确认")
    notes: Optional[str] = Field(None, max_length=500, description="确认备注")


from apps.common.schemas import PaginationQuerySchema

class RelationshipSearchSchema(PaginationQuerySchema):
    """关系搜索Schema"""
    
    family_id: Optional[int] = Field(None, description="家庭ID")
    member_id: Optional[int] = Field(None, description="成员ID")
    relationship_type: Optional[str] = Field(None, description="关系类型")
    is_confirmed: Optional[bool] = Field(None, description="是否已确认")
    is_active: Optional[bool] = Field(None, description="是否激活")
    confidence_level_min: Optional[int] = Field(None, ge=1, le=10, description="最低可信度")
    confidence_level_max: Optional[int] = Field(None, ge=1, le=10, description="最高可信度")
    start_date_from: Optional[date] = Field(None, description="开始日期起")
    start_date_to: Optional[date] = Field(None, description="开始日期止")
    visibility: Optional[str] = Field(None, description="可见性")


class RelationshipQuerySchema(PaginationQuerySchema):
    """关系查询Schema"""
    
    family_id: Optional[int] = Field(None, description="家庭ID")
    member_id: Optional[int] = Field(None, description="成员ID")
    relationship_type: Optional[str] = Field(None, description="关系类型")
    is_confirmed: Optional[bool] = Field(None, description="是否已确认")
    ordering: Optional[str] = Field(None, description="排序字段")


class RelationshipTypeSchema(Schema):
    """关系类型Schema"""
    
    code: str = Field(..., description="关系类型代码")
    name: str = Field(..., description="关系类型名称")
    description: Optional[str] = Field(None, description="关系类型描述")
    is_bidirectional: bool = Field(..., description="是否双向关系")
    reverse_type: Optional[str] = Field(None, description="反向关系类型")


class RelationshipStatisticsSchema(Schema):
    """关系统计Schema"""
    
    total_relationships: int = Field(..., description="总关系数")
    confirmed_relationships: int = Field(..., description="已确认关系数")
    pending_relationships: int = Field(..., description="待确认关系数")
    active_relationships: int = Field(..., description="活跃关系数")
    relationship_types: List[dict] = Field(..., description="关系类型统计")
    confidence_distribution: List[dict] = Field(..., description="可信度分布")


class RelationshipTreeSchema(Schema):
    """关系树Schema"""
    
    member_id: int = Field(..., description="成员ID")
    member_name: str = Field(..., description="成员姓名")
    relationships: List[dict] = Field(..., description="关系列表")
    children: List['RelationshipTreeSchema'] = Field([], description="子关系")


class RelationshipPathSchema(Schema):
    """关系路径Schema"""
    
    from_member_id: int = Field(..., description="起始成员ID")
    to_member_id: int = Field(..., description="目标成员ID")
    path: List[dict] = Field(..., description="关系路径")
    path_length: int = Field(..., description="路径长度")
    relationship_description: str = Field(..., description="关系描述")


class RelationshipValidationSchema(Schema):
    """关系验证Schema"""
    
    relationship_id: int = Field(..., description="关系ID")
    validation_type: str = Field(..., description="验证类型")
    validation_result: bool = Field(..., description="验证结果")
    validation_message: str = Field(..., description="验证消息")
    validation_details: Optional[dict] = Field(None, description="验证详情")


class RelationshipBatchCreateSchema(Schema):
    """批量创建关系Schema"""
    
    relationships: List[RelationshipCreateSchema] = Field(..., description="关系列表")
    auto_confirm: bool = Field(False, description="自动确认")
    skip_duplicates: bool = Field(True, description="跳过重复")


class RelationshipBatchUpdateSchema(Schema):
    """批量更新关系Schema"""
    
    relationship_ids: List[int] = Field(..., description="关系ID列表")
    update_data: RelationshipUpdateSchema = Field(..., description="更新数据")


class RelationshipImportSchema(Schema):
    """关系导入Schema"""
    
    file_type: str = Field(..., description="文件类型")
    file_content: str = Field(..., description="文件内容")
    family_id: int = Field(..., description="家庭ID")
    auto_create_members: bool = Field(False, description="自动创建成员")
    auto_confirm: bool = Field(False, description="自动确认")


class RelationshipExportSchema(Schema):
    """关系导出Schema"""
    
    family_id: int = Field(..., description="家庭ID")
    export_format: str = Field('json', description="导出格式")
    include_inactive: bool = Field(False, description="包含非活跃关系")
    include_unconfirmed: bool = Field(False, description="包含未确认关系")
    date_range_start: Optional[date] = Field(None, description="日期范围开始")
    date_range_end: Optional[date] = Field(None, description="日期范围结束")


# 解决循环引用问题
RelationshipTreeSchema.model_rebuild()