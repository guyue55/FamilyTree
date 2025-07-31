"""
公共Schema定义

该文件定义了系统中使用的公共Schema类。
遵循Django Ninja最佳实践和Google Python Style Guide。
"""

from datetime import datetime
from typing import Optional, List, Any, Dict, Generic, TypeVar
from ninja import Schema, Field
from ninja.files import UploadedFile
from pydantic import field_validator, ValidationInfo
from .constants import PaginationDefaults

T = TypeVar('T')

class BaseResponseSchema(Schema):
    """基础响应Schema"""

    id: int = Field(..., description="记录ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

class TimestampSchema(Schema):
    """时间戳Schema"""

    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

class SoftDeleteResponseSchema(BaseResponseSchema):
    """软删除响应Schema"""

    is_deleted: bool = Field(..., description="是否删除")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")

class StatusChoicesSchema(Schema):
    """状态选择Schema"""

    value: str = Field(..., description="状态值")
    label: str = Field(..., description="状态标签")

class VisibilityChoicesSchema(Schema):
    """可见性选择Schema"""

    value: str = Field(..., description="可见性值")
    label: str = Field(..., description="可见性标签")

class GenderChoicesSchema(Schema):
    """性别选择Schema"""

    value: str = Field(..., description="性别值")
    label: str = Field(..., description="性别标签")

class SystemConfigCreateSchema(Schema):
    """创建系统配置Schema"""

    key: str = Field(..., min_length=1, max_length=100, description="配置键")
    value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, max_length=200, description="配置描述")
    is_active: bool = Field(True, description="是否启用")

    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str, info: ValidationInfo) -> str:
        """验证配置键格式"""
        if not v.replace('_', '').replace('-', '').replace('.', '').isalnum():
            raise ValueError('配置键只能包含字母、数字、下划线、连字符和点号')
        return v.lower()

class SystemConfigUpdateSchema(Schema):
    """更新系统配置Schema"""

    value: Optional[str] = Field(None, description="配置值")
    description: Optional[str] = Field(None, max_length=200, description="配置描述")
    is_active: Optional[bool] = Field(None, description="是否启用")

class SystemConfigResponseSchema(BaseResponseSchema):
    """系统配置响应Schema"""

    key: str = Field(..., description="配置键")
    value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="配置描述")
    is_active: bool = Field(..., description="是否启用")

class SystemConfigListResponseSchema(Schema):
    """系统配置列表响应Schema"""

    id: int = Field(..., description="配置ID")
    key: str = Field(..., description="配置键")
    description: Optional[str] = Field(None, description="配置描述")
    is_active: bool = Field(..., description="是否启用")
    updated_at: datetime = Field(..., description="更新时间")

class SystemConfigSearchSchema(Schema):
    """系统配置搜索Schema"""

    keyword: Optional[str] = Field(None, description="搜索关键词")
    is_active: Optional[bool] = Field(None, description="是否启用")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")

class SystemConfigBatchUpdateSchema(Schema):
    """批量更新系统配置Schema"""

    configs: List[Dict[str, Any]] = Field(..., description="配置列表")

    @field_validator('configs')
    @classmethod
    def validate_configs(cls, v: List[Dict[str, Any]], info: ValidationInfo) -> List[Dict[str, Any]]:
        """验证配置列表"""
        if not v:
            raise ValueError('配置列表不能为空')

        for config in v:
            if 'key' not in config:
                raise ValueError('每个配置必须包含key字段')
            if 'value' not in config:
                raise ValueError('每个配置必须包含value字段')

        return v

# ==================== 统一API响应Schema ====================

class ApiResponseSchema(Schema, Generic[T]):
    """统一API响应Schema"""

    code: int = Field(..., description="响应状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    request_id: Optional[str] = Field(None, description="请求ID")

class SuccessResponseSchema(ApiResponseSchema[T]):
    """成功响应Schema"""

    code: int = Field(200, description="响应状态码")
    message: str = Field("success", description="响应消息")

class ErrorResponseSchema(Schema):
    """错误响应Schema"""

    code: int = Field(..., description="错误状态码")
    message: str = Field(..., description="错误消息")
    data: Optional[Any] = Field(None, description="错误数据")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="详细错误信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    request_id: Optional[str] = Field(None, description="请求ID")

class ValidationErrorDetailSchema(Schema):
    """验证错误详情Schema"""

    field: str = Field(..., description="字段名")
    message: str = Field(..., description="错误消息")
    code: str = Field(..., description="错误代码")
    value: Optional[Any] = Field(None, description="错误值")

# ==================== 分页相关Schema ====================

class PaginationQuerySchema(Schema):
    """分页查询参数Schema"""

    page: int = Field(PaginationDefaults.DEFAULT_PAGE, ge=1, description="页码")
    page_size: int = Field(
        PaginationDefaults.DEFAULT_PAGE_SIZE,
        ge=PaginationDefaults.MIN_PAGE_SIZE,
        le=PaginationDefaults.MAX_PAGE_SIZE,
        description="每页数量"
    )

class PaginationInfoSchema(Schema):
    """分页信息Schema"""

    page: int = Field(..., description="当前页码", ge=1)
    page_size: int = Field(..., description="每页数量", ge=1, le=100)
    total: int = Field(..., description="总数量", ge=0)
    total_pages: int = Field(..., description="总页数", ge=1)
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")

class PaginatedResponseSchema(Schema, Generic[T]):
    """分页响应Schema"""

    items: List[T] = Field(..., description="数据列表")
    pagination: PaginationInfoSchema = Field(..., description="分页信息")

class PaginatedApiResponseSchema(ApiResponseSchema[PaginatedResponseSchema[T]]):
    """分页API响应Schema"""
    pass

# ==================== 搜索和过滤Schema ====================

class SearchQuerySchema(Schema):
    """搜索查询参数Schema"""

    search: Optional[str] = Field(None, description="搜索关键词")
    ordering: Optional[str] = Field(None, description="排序字段")

class FilterQuerySchema(Schema):
    """过滤查询参数Schema"""

    status: Optional[str] = Field(None, description="状态过滤")
    created_at_gte: Optional[datetime] = Field(None, description="创建时间起始")
    created_at_lte: Optional[datetime] = Field(None, description="创建时间结束")

class BaseQuerySchema(PaginationQuerySchema, SearchQuerySchema, FilterQuerySchema):
    """基础查询参数Schema"""
    pass

class ValidationErrorSchema(Schema):
    """验证错误Schema"""

    field: str = Field(..., description="字段名")
    message: str = Field(..., description="错误消息")
    code: str = Field(..., description="错误代码")

class BulkOperationSchema(Schema):
    """批量操作Schema"""

    operation: str = Field(..., description="操作类型")
    ids: List[int] = Field(..., description="ID列表")
    data: Optional[Dict[str, Any]] = Field(None, description="操作数据")

    @field_validator('ids')
    @classmethod
    def validate_ids(cls, v: List[int], info: ValidationInfo) -> List[int]:
        """验证ID列表"""
        if not v:
            raise ValueError('ID列表不能为空')
        if len(v) > 1000:
            raise ValueError('批量操作最多支持1000条记录')
        return v

class BulkOperationResultSchema(Schema):
    """批量操作结果Schema"""

    success_count: int = Field(..., description="成功数量")
    failure_count: int = Field(..., description="失败数量")
    total_count: int = Field(..., description="总数量")
    success_ids: List[int] = Field(..., description="成功ID列表")
    failure_details: List[Dict[str, Any]] = Field(..., description="失败详情")

class FileUploadSchema(Schema):
    """文件上传Schema"""

    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    file_type: str = Field(..., description="文件类型")
    upload_path: Optional[str] = Field(None, description="上传路径")

class ImageUploadSchema(Schema):
    """图片上传Schema"""

    file: UploadedFile = Field(..., description="上传的图片文件")
    description: Optional[str] = Field(None, max_length=200, description="图片描述")

    @field_validator('file')
    @classmethod
    def validate_image_file(cls, v: UploadedFile, info: ValidationInfo) -> UploadedFile:
        """
        验证图片文件

        Args:
            v: 上传的文件对象
            info: 验证信息对象

        Returns:
            验证通过的文件对象

        Raises:
            ValueError: 当文件不是图片或超过大小限制时
        """
        if not v.content_type.startswith('image/'):
            raise ValueError('只能上传图片文件')
        if v.size > 20 * 1024 * 1024:  # 20MB
            raise ValueError('图片文件大小不能超过20MB')
        return v

class MessageResponseSchema(Schema):
    """消息响应Schema"""

    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    code: int = Field(200, description="响应状态码")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class DataResponseSchema(Schema):
    """数据响应Schema"""

    success: bool = Field(..., description="操作是否成功")
    message: str = Field("success", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    code: int = Field(200, description="响应状态码")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class FileUploadResponseSchema(Schema):
    """文件上传响应Schema"""

    file_id: str = Field(..., description="文件ID")
    file_name: str = Field(..., description="文件名")
    file_url: str = Field(..., description="文件URL")
    file_size: int = Field(..., description="文件大小")
    upload_time: datetime = Field(..., description="上传时间")

# ==================== 导出的Schema列表 ====================

__all__ = [
    # 基础Schema
    'BaseResponseSchema', 'TimestampSchema', 'SoftDeleteResponseSchema',

    # 选择Schema
    'StatusChoicesSchema', 'VisibilityChoicesSchema', 'GenderChoicesSchema',

    # 系统配置Schema
    'SystemConfigCreateSchema', 'SystemConfigUpdateSchema', 'SystemConfigResponseSchema',
    'SystemConfigListResponseSchema', 'SystemConfigSearchSchema', 'SystemConfigBatchUpdateSchema',

    # 通用响应Schema
    'ApiResponseSchema', 'PaginatedResponseSchema', 'ErrorResponseSchema', 'ValidationErrorSchema',
    'MessageResponseSchema', 'DataResponseSchema',

    # 文件上传Schema
    'FileUploadSchema', 'ImageUploadSchema', 'FileUploadResponseSchema',

    # 批量操作Schema
    'BulkOperationSchema', 'BulkOperationResultSchema',
]