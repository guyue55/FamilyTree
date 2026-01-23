"""
媒体模块Schema定义

基于Pydantic的数据验证和序列化Schema，用于媒体文件管理相关的API接口。
遵循Django Ninja最佳实践和Google Python Style Guide。

设计原则：
- 数据验证：使用Pydantic Field进行严格的数据类型和格式验证
- 文档化：每个Schema都有详细的字段说明和示例
- 可扩展性：支持灵活的字段组合和验证规则
- 一致性：统一的命名规范和数据结构
- 安全性：敏感字段的适当处理和验证
"""

# 导入模块
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, model_validator, field_validator, ValidationInfo
from ninja import Schema


# ==================== 枚举定义 ====================


class MediaFileType(str, Enum):
    """媒体文件类型枚举"""

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    OTHER = "other"


class MediaPrivacyLevel(str, Enum):
    """媒体隐私级别枚举"""

    PUBLIC = "public"
    FAMILY = "family"
    PRIVATE = "private"


class MediaProcessingStatus(str, Enum):
    """媒体处理状态枚举"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MediaCategory(str, Enum):
    """媒体分类枚举"""

    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    EVENT = "event"
    DOCUMENT = "document"
    GENEALOGY = "genealogy"
    OTHER = "other"


class AlbumType(str, Enum):
    """相册类型枚举"""

    FAMILY = "family"
    EVENT = "event"
    TIMELINE = "timeline"
    CUSTOM = "custom"


class AlbumVisibility(str, Enum):
    """相册可见性枚举"""

    PUBLIC = "public"
    FAMILY = "family"
    PRIVATE = "private"


class CommentStatus(str, Enum):
    """评论状态枚举"""

    ACTIVE = "active"
    HIDDEN = "hidden"
    DELETED = "deleted"


class ExportFormat(str, Enum):
    """导出格式枚举"""

    ZIP = "zip"
    TAR = "tar"
    PDF = "pdf"
    JSON = "json"


class ImportSource(str, Enum):
    """导入源枚举"""

    LOCAL = "local"
    CLOUD = "cloud"
    URL = "url"
    SOCIAL = "social"


class JobType(str, Enum):
    """任务类型枚举"""

    THUMBNAIL = "thumbnail"
    COMPRESS = "compress"
    METADATA = "metadata"
    ANALYSIS = "analysis"


class JobStatus(str, Enum):
    """任务状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ==================== 基础Schema ====================


class MediaFileBaseSchema(Schema):
    """媒体文件基础信息Schema"""

    title: str = Field(..., min_length=1, max_length=200, description="媒体标题")
    description: Optional[str] = Field(None, max_length=1000, description="媒体描述")
    tags: Optional[str] = Field(None, max_length=200, description="标签")
    category: MediaCategory = Field(MediaCategory.OTHER, description="分类")
    taken_date: Optional[datetime] = Field(None, description="拍摄时间")
    location: Optional[str] = Field(None, max_length=200, description="拍摄地点")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")
    visibility: MediaPrivacyLevel = Field(
        MediaPrivacyLevel.FAMILY, description="可见性"
    )
    is_featured: bool = Field(False, description="是否精选")


class MediaFileCreateSchema(MediaFileBaseSchema):
    """创建媒体文件Schema"""

    family_id: int = Field(..., description="家族ID")

    @field_validator("latitude")
    @classmethod
    def validate_latitude(
        cls, v: Optional[float], info: ValidationInfo
    ) -> Optional[float]:
        """验证纬度"""
        if v is not None and not (-90 <= v <= 90):
            raise ValueError("纬度必须在-90到90之间")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(
        cls, v: Optional[float], info: ValidationInfo
    ) -> Optional[float]:
        """验证经度"""
        if v is not None and not (-180 <= v <= 180):
            raise ValueError("经度必须在-180到180之间")
        return v


class MediaFileUpdateSchema(Schema):
    """更新媒体文件Schema"""

    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="媒体标题"
    )
    description: Optional[str] = Field(None, max_length=1000, description="媒体描述")
    tags: Optional[str] = Field(None, max_length=200, description="标签")
    category: Optional[MediaCategory] = Field(None, description="分类")
    taken_date: Optional[datetime] = Field(None, description="拍摄时间")
    location: Optional[str] = Field(None, max_length=200, description="拍摄地点")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")
    visibility: Optional[MediaPrivacyLevel] = Field(None, description="可见性")
    is_featured: Optional[bool] = Field(None, description="是否精选")


class MediaFileResponseSchema(Schema):
    """媒体文件响应Schema"""

    id: int = Field(..., description="媒体文件ID")
    family_id: int = Field(..., description="家族ID")
    uploader_id: int = Field(..., description="上传者ID")
    title: str = Field(..., description="媒体标题")
    description: Optional[str] = Field(None, description="媒体描述")
    file: str = Field(..., description="文件URL")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    file_type: MediaFileType = Field(..., description="文件类型")
    mime_type: str = Field(..., description="MIME类型")
    width: Optional[int] = Field(None, description="宽度")
    height: Optional[int] = Field(None, description="高度")
    duration: Optional[int] = Field(None, description="时长")
    thumbnail: Optional[str] = Field(None, description="缩略图URL")
    tags: Optional[str] = Field(None, description="标签")
    category: MediaCategory = Field(..., description="分类")
    taken_date: Optional[datetime] = Field(None, description="拍摄时间")
    location: Optional[str] = Field(None, description="拍摄地点")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")
    visibility: MediaPrivacyLevel = Field(..., description="可见性")
    is_featured: bool = Field(..., description="是否精选")
    view_count: int = Field(..., description="查看次数")
    download_count: int = Field(..., description="下载次数")
    processing_status: MediaProcessingStatus = Field(..., description="处理状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class MediaFileListResponseSchema(Schema):
    """媒体文件列表响应Schema"""

    id: int = Field(..., description="媒体文件ID")
    title: str = Field(..., description="媒体标题")
    file_type: MediaFileType = Field(..., description="文件类型")
    thumbnail: Optional[str] = Field(None, description="缩略图URL")
    category: MediaCategory = Field(..., description="分类")
    taken_date: Optional[datetime] = Field(None, description="拍摄时间")
    is_featured: bool = Field(..., description="是否精选")
    view_count: int = Field(..., description="查看次数")
    created_at: datetime = Field(..., description="创建时间")


class MediaMemberTagCreateSchema(Schema):
    """创建媒体成员标记Schema"""

    media_id: int = Field(..., description="媒体文件ID")
    member_id: int = Field(..., description="成员ID")
    x_coordinate: Optional[float] = Field(None, ge=0, le=100, description="X坐标百分比")
    y_coordinate: Optional[float] = Field(None, ge=0, le=100, description="Y坐标百分比")
    width: Optional[float] = Field(None, ge=0, le=100, description="标记宽度百分比")
    height: Optional[float] = Field(None, ge=0, le=100, description="标记高度百分比")


class MediaMemberTagResponseSchema(Schema):
    """媒体成员标记响应Schema"""

    id: int = Field(..., description="标记ID")
    media_id: int = Field(..., description="媒体文件ID")
    member_id: int = Field(..., description="成员ID")
    tagger_id: int = Field(..., description="标记者ID")
    x_coordinate: Optional[float] = Field(None, description="X坐标百分比")
    y_coordinate: Optional[float] = Field(None, description="Y坐标百分比")
    width: Optional[float] = Field(None, description="标记宽度百分比")
    height: Optional[float] = Field(None, description="标记高度百分比")
    is_confirmed: bool = Field(..., description="是否确认")
    confirmed_by_id: Optional[int] = Field(None, description="确认者ID")
    confirmed_at: Optional[datetime] = Field(None, description="确认时间")
    created_at: datetime = Field(..., description="创建时间")


class MediaAlbumCreateSchema(Schema):
    """创建媒体相册Schema"""

    family_id: int = Field(..., description="家族ID")
    name: str = Field(..., min_length=1, max_length=100, description="相册名称")
    description: Optional[str] = Field(None, max_length=500, description="相册描述")
    album_type: AlbumType = Field(AlbumType.CUSTOM, description="相册类型")
    tags: Optional[str] = Field(None, max_length=200, description="标签")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    visibility: AlbumVisibility = Field(AlbumVisibility.FAMILY, description="可见性")
    sort_order: int = Field(0, ge=0, description="排序权重")

    @model_validator(mode="after")
    def validate_date_range(self):
        """验证日期范围"""
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValueError("结束日期不能早于开始日期")
        return self


class MediaAlbumUpdateSchema(Schema):
    """更新媒体相册Schema"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="相册名称"
    )
    description: Optional[str] = Field(None, max_length=500, description="相册描述")
    album_type: Optional[AlbumType] = Field(None, description="相册类型")
    tags: Optional[str] = Field(None, max_length=200, description="标签")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    visibility: Optional[AlbumVisibility] = Field(None, description="可见性")
    sort_order: Optional[int] = Field(None, ge=0, description="排序权重")


class MediaAlbumResponseSchema(Schema):
    """媒体相册响应Schema"""

    id: int = Field(..., description="相册ID")
    family_id: int = Field(..., description="家族ID")
    creator_id: int = Field(..., description="创建者ID")
    name: str = Field(..., description="相册名称")
    description: Optional[str] = Field(None, description="相册描述")
    cover_image: Optional[str] = Field(None, description="封面图片URL")
    album_type: AlbumType = Field(..., description="相册类型")
    tags: Optional[str] = Field(None, description="标签")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    visibility: AlbumVisibility = Field(..., description="可见性")
    media_count: int = Field(..., description="媒体数量")
    view_count: int = Field(..., description="查看次数")
    sort_order: int = Field(..., description="排序权重")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class MediaAlbumItemCreateSchema(Schema):
    """创建相册媒体项Schema"""

    album_id: int = Field(..., description="相册ID")
    media_id: int = Field(..., description="媒体文件ID")
    sort_order: int = Field(0, ge=0, description="排序序号")
    caption: Optional[str] = Field(None, max_length=500, description="说明")


class MediaAlbumItemResponseSchema(Schema):
    """相册媒体项响应Schema"""

    id: int = Field(..., description="项目ID")
    album_id: int = Field(..., description="相册ID")
    media_id: int = Field(..., description="媒体文件ID")
    added_by_id: int = Field(..., description="添加者ID")
    sort_order: int = Field(..., description="排序序号")
    caption: Optional[str] = Field(None, description="说明")
    created_at: datetime = Field(..., description="创建时间")


class MediaCommentCreateSchema(Schema):
    """创建媒体评论Schema"""

    media_id: int = Field(..., description="媒体文件ID")
    parent_comment_id: Optional[int] = Field(None, description="父评论ID")
    content: str = Field(..., max_length=1000, description="评论内容")


class MediaCommentUpdateSchema(Schema):
    """更新媒体评论Schema"""

    content: Optional[str] = Field(None, max_length=1000, description="评论内容")
    status: Optional[CommentStatus] = Field(None, description="状态")


class MediaCommentResponseSchema(Schema):
    """媒体评论响应Schema"""

    id: int = Field(..., description="评论ID")
    media_id: int = Field(..., description="媒体文件ID")
    commenter_id: int = Field(..., description="评论者ID")
    parent_comment_id: Optional[int] = Field(None, description="父评论ID")
    content: str = Field(..., description="评论内容")
    status: CommentStatus = Field(..., description="状态")
    like_count: int = Field(..., description="点赞数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


from apps.common.schemas import PaginationQuerySchema


class MediaSearchSchema(PaginationQuerySchema):
    """媒体搜索Schema"""

    family_id: Optional[int] = Field(None, description="家族ID")
    keyword: Optional[str] = Field(None, description="搜索关键词")
    file_type: Optional[MediaFileType] = Field(None, description="文件类型")
    category: Optional[MediaCategory] = Field(None, description="分类")
    is_featured: Optional[bool] = Field(None, description="是否精选")
    uploader_id: Optional[int] = Field(None, description="上传者ID")
    taken_date_start: Optional[datetime] = Field(None, description="拍摄开始时间")
    taken_date_end: Optional[datetime] = Field(None, description="拍摄结束时间")
    location: Optional[str] = Field(None, description="地点筛选")
    tags: Optional[str] = Field(None, description="标签筛选")
    processing_status: Optional[MediaProcessingStatus] = Field(
        None, description="处理状态"
    )


class MediaStatisticsSchema(Schema):
    """媒体统计Schema"""

    total_files: int = Field(..., description="总文件数")
    total_size: int = Field(..., description="总文件大小")
    image_count: int = Field(..., description="图片数量")
    video_count: int = Field(..., description="视频数量")
    audio_count: int = Field(..., description="音频数量")
    document_count: int = Field(..., description="文档数量")
    featured_count: int = Field(..., description="精选数量")
    category_distribution: List[dict] = Field(..., description="分类分布")
    upload_timeline: List[dict] = Field(..., description="上传时间线")
    top_uploaders: List[dict] = Field(..., description="上传排行")


class MediaUploadSchema(Schema):
    """媒体上传Schema"""

    family_id: int = Field(..., description="家族ID")
    title: str = Field(..., min_length=1, max_length=200, description="媒体标题")
    description: Optional[str] = Field(None, max_length=1000, description="媒体描述")
    category: MediaCategory = Field(MediaCategory.OTHER, description="分类")
    tags: Optional[str] = Field(None, max_length=200, description="标签")
    taken_date: Optional[datetime] = Field(None, description="拍摄时间")
    location: Optional[str] = Field(None, max_length=200, description="拍摄地点")
    visibility: MediaPrivacyLevel = Field(
        MediaPrivacyLevel.FAMILY, description="可见性"
    )


class MediaBatchUploadSchema(Schema):
    """批量媒体上传Schema"""

    family_id: int = Field(..., description="家族ID")
    files: List[MediaUploadSchema] = Field(..., description="文件列表")
    auto_categorize: bool = Field(True, description="自动分类")
    extract_metadata: bool = Field(True, description="提取元数据")


class MediaExportSchema(Schema):
    """媒体导出Schema"""

    family_id: int = Field(..., description="家族ID")
    export_format: ExportFormat = Field(ExportFormat.ZIP, description="导出格式")
    include_metadata: bool = Field(True, description="包含元数据")
    file_types: Optional[List[str]] = Field(None, description="文件类型筛选")
    categories: Optional[List[str]] = Field(None, description="分类筛选")
    date_range_start: Optional[datetime] = Field(None, description="日期范围开始")
    date_range_end: Optional[datetime] = Field(None, description="日期范围结束")
    max_file_size: Optional[int] = Field(None, description="最大文件大小")


class MediaImportSchema(Schema):
    """媒体导入Schema"""

    family_id: int = Field(..., description="家族ID")
    import_source: ImportSource = Field(..., description="导入源")
    auto_categorize: bool = Field(True, description="自动分类")
    extract_metadata: bool = Field(True, description="提取元数据")
    create_albums: bool = Field(False, description="创建相册")
    merge_duplicates: bool = Field(True, description="合并重复")


class MediaProcessingJobSchema(Schema):
    """媒体处理任务Schema"""

    id: int = Field(..., description="任务ID")
    media_id: int = Field(..., description="媒体文件ID")
    job_type: JobType = Field(..., description="任务类型")
    status: JobStatus = Field(..., description="任务状态")
    progress: int = Field(..., ge=0, le=100, description="进度百分比")
    error_message: Optional[str] = Field(None, description="错误信息")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    created_at: datetime = Field(..., description="创建时间")


class MediaAnalyticsSchema(Schema):
    """媒体分析Schema"""

    family_id: int = Field(..., description="家族ID")
    period: str = Field("month", description="统计周期")
    view_stats: List[dict] = Field(..., description="查看统计")
    upload_stats: List[dict] = Field(..., description="上传统计")
    popular_media: List[dict] = Field(..., description="热门媒体")
    active_users: List[dict] = Field(..., description="活跃用户")
    storage_usage: dict = Field(..., description="存储使用情况")
