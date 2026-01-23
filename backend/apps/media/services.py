"""
媒体模块服务层

基于通用服务基类的媒体服务实现，提供媒体文件管理相关的所有业务逻辑。
遵循Django最佳实践和Google Python Style Guide。
"""

from typing import List, Dict, Any, Tuple, Optional
from django.db import transaction
from django.db.models import Q, QuerySet
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from loguru import logger

from apps.common.services import BaseService, CacheableService
from apps.common.constants import BusinessLimits
from apps.common.exceptions import (
    ValidationError,
    PermissionError,
    NotFoundError,
    OperationError,
)
from apps.common.utils import paginate_queryset
from .models import MediaFile

User = get_user_model()


class MediaService(BaseService, CacheableService):
    """
    媒体服务类

    提供媒体文件管理相关的所有业务逻辑，包括文件上传、下载、管理等功能。
    继承自BaseService和CacheableService，具备通用服务能力和缓存功能。
    """

    model = MediaFile
    cache_prefix = "media"
    cache_timeout = 1800  # 30分钟缓存

    # 搜索字段配置
    search_fields = ["title", "description", "tags", "location"]
    filter_fields = ["file_type", "category", "visibility", "is_featured"]
    ordering_fields = ["created_at", "updated_at", "title", "file_size", "taken_date"]

    @classmethod
    def get_search_fields(cls) -> List[str]:
        """获取搜索字段列表"""
        return cls.search_fields

    @classmethod
    def get_filter_fields(cls) -> List[str]:
        """获取过滤字段列表"""
        return cls.filter_fields

    @classmethod
    def get_ordering_fields(cls) -> List[str]:
        """获取排序字段列表"""
        return cls.ordering_fields

    @classmethod
    def get_queryset(cls, user: User = None) -> QuerySet:
        """
        获取基础查询集

        Args:
            user: 当前用户

        Returns:
            QuerySet: 媒体文件查询集
        """
        queryset = cls.model.objects.select_related("family", "uploader")

        if user and not user.is_superuser:
            # 非超级用户只能看到有权限的媒体文件
            queryset = cls._filter_by_permission(queryset, user)

        return queryset

    @classmethod
    def _filter_by_permission(cls, queryset: QuerySet, user: User) -> QuerySet:
        """
        根据权限过滤查询集

        Args:
            queryset: 原始查询集
            user: 当前用户

        Returns:
            QuerySet: 过滤后的查询集
        """
        return queryset.filter(
            Q(visibility="public") | Q(uploader=user) | Q(family__members=user)
        ).distinct()

    def upload_media(
        self, file: UploadedFile, data: Dict[str, Any], user: User
    ) -> MediaFile:
        """
        上传媒体文件

        Args:
            file: 上传的文件
            data: 媒体数据
            user: 上传用户

        Returns:
            MediaFile: 创建的媒体文件实例

        Raises:
            ValidationError: 验证失败
            PermissionError: 权限不足
        """
        try:
            # 验证文件
            self._validate_file(file)

            # 验证权限
            family_id = data.get("family_id")
            if family_id and not self._check_upload_permission(user, family_id):
                raise PermissionError("没有上传媒体文件的权限")

            # 处理文件上传
            with transaction.atomic():
                media_data = {
                    "title": data["title"],
                    "description": data.get("description"),
                    "family_id": family_id,
                    "uploader": user,
                    "file": file,
                    "file_name": file.name,
                    "file_size": file.size,
                    "file_type": self._get_file_type(file),
                    "mime_type": getattr(
                        file, "content_type", "application/octet-stream"
                    ),
                    "tags": ",".join(data.get("tags", [])) if data.get("tags") else "",
                    "category": data.get("category", "other"),
                    "visibility": data.get("privacy_level", "family"),
                    "processing_status": "pending",
                }

                media = self.create(media_data)

                # 清除相关缓存
                self.clear_cache_pattern(f"{self.cache_prefix}:*")

                logger.info(f"用户 {user.username} 上传了媒体文件 {media.title}")
                return media

        except Exception as e:
            logger.error(f"Upload media error: {e}")
            raise OperationError(f"文件上传失败: {str(e)}")

    def batch_upload_media(
        self, files: List[UploadedFile], data: Dict[str, Any], user: User
    ) -> Dict[str, Any]:
        """
        批量上传媒体文件

        Args:
            files: 上传的文件列表
            data: 媒体数据
            user: 上传用户

        Returns:
            Dict[str, Any]: 上传结果
        """
        uploaded_media = []
        errors = []

        for file in files:
            try:
                file_data = data.copy()
                file_data["title"] = file.name
                media = self.upload_media(file, file_data, user)
                uploaded_media.append(media)
            except Exception as e:
                errors.append({"file": file.name, "error": str(e)})

        return {
            "uploaded_count": len(uploaded_media),
            "failed_count": len(errors),
            "uploaded_media": uploaded_media,
            "errors": errors,
        }

    def list_media(self, user: User, **filters) -> Tuple[List[MediaFile], int]:
        """
        获取媒体文件列表

        Args:
            user: 当前用户
            **filters: 过滤条件

        Returns:
            Tuple[List[MediaFile], int]: 媒体文件列表和总数
        """
        queryset = self.get_queryset(user)

        # 应用过滤条件
        if filters.get("family_id"):
            queryset = queryset.filter(family_id=filters["family_id"])

        if filters.get("file_type"):
            queryset = queryset.filter(file_type=filters["file_type"])

        if filters.get("keyword"):
            queryset = queryset.filter(
                Q(title__icontains=filters["keyword"])
                | Q(description__icontains=filters["keyword"])
                | Q(tags__icontains=filters["keyword"])
            )

        if filters.get("is_featured") is not None:
            queryset = queryset.filter(is_featured=filters["is_featured"])

        # 排序
        ordering = filters.get("ordering", "-created_at")
        queryset = queryset.order_by(ordering)

        # 分页
        page = filters.get("page", 1)
        page_size = filters.get("page_size", 20)

        return paginate_queryset(queryset, page, page_size)

    def get_media(self, media_id: int, user: User) -> MediaFile:
        """
        获取媒体文件详情

        Args:
            media_id: 媒体文件ID
            user: 当前用户

        Returns:
            MediaFile: 媒体文件实例

        Raises:
            NotFoundError: 媒体文件不存在
            PermissionError: 权限不足
        """
        try:
            media = self.get_queryset(user).get(id=media_id)

            # 增加查看次数
            media.view_count += 1
            media.save(update_fields=["view_count"])

            return media
        except MediaFile.DoesNotExist:
            raise NotFoundError("媒体文件不存在")

    def update_media(
        self, media_id: int, data: Dict[str, Any], user: User
    ) -> MediaFile:
        """
        更新媒体文件信息

        Args:
            media_id: 媒体文件ID
            data: 更新数据
            user: 当前用户

        Returns:
            MediaFile: 更新后的媒体文件实例

        Raises:
            NotFoundError: 媒体文件不存在
            PermissionError: 权限不足
        """
        media = self.get_media(media_id, user)

        # 检查编辑权限
        if not self._check_edit_permission(user, media):
            raise PermissionError("没有编辑媒体文件的权限")

        # 更新数据
        for key, value in data.items():
            if hasattr(media, key):
                setattr(media, key, value)

        media.save()

        # 清除缓存
        self.clear_cache_pattern(f"{self.cache_prefix}:*")

        logger.info(f"用户 {user.username} 更新了媒体文件 {media.title}")
        return media

    def delete_media(self, media_id: int, user: User) -> None:
        """
        删除媒体文件

        Args:
            media_id: 媒体文件ID
            user: 当前用户

        Raises:
            NotFoundError: 媒体文件不存在
            PermissionError: 权限不足
        """
        media = self.get_media(media_id, user)

        # 检查删除权限
        if not self._check_delete_permission(user, media):
            raise PermissionError("没有删除媒体文件的权限")

        # 删除文件
        if media.file:
            media.file.delete()

        media.delete()

        # 清除缓存
        self.clear_cache_pattern(f"{self.cache_prefix}:*")

        logger.info(f"用户 {user.username} 删除了媒体文件 {media.title}")

    def batch_delete_media(self, media_ids: List[int], user: User) -> Dict[str, Any]:
        """
        批量删除媒体文件

        Args:
            media_ids: 媒体文件ID列表
            user: 当前用户

        Returns:
            Dict[str, Any]: 删除结果
        """
        deleted_count = 0
        errors = []

        for media_id in media_ids:
            try:
                self.delete_media(media_id, user)
                deleted_count += 1
            except Exception as e:
                errors.append({"media_id": media_id, "error": str(e)})

        return {
            "deleted_count": deleted_count,
            "failed_count": len(errors),
            "errors": errors,
        }

    def batch_update_tags(
        self, media_ids: List[int], tags: List[str], user: User
    ) -> Dict[str, Any]:
        """
        批量更新标签

        Args:
            media_ids: 媒体文件ID列表
            tags: 标签列表
            user: 当前用户

        Returns:
            Dict[str, Any]: 更新结果
        """
        updated_count = 0
        errors = []
        tags_str = ",".join(tags)

        for media_id in media_ids:
            try:
                self.update_media(media_id, {"tags": tags_str}, user)
                updated_count += 1
            except Exception as e:
                errors.append({"media_id": media_id, "error": str(e)})

        return {
            "updated_count": updated_count,
            "failed_count": len(errors),
            "errors": errors,
        }

    def get_family_gallery(self, user: User, **filters) -> Tuple[List[MediaFile], int]:
        """
        获取家族相册

        Args:
            user: 当前用户
            **filters: 过滤条件

        Returns:
            Tuple[List[MediaFile], int]: 媒体文件列表和总数
        """
        filters["file_type"] = "image"
        return self.list_media(user, **filters)

    def get_member_media(self, user: User, **filters) -> Tuple[List[MediaFile], int]:
        """
        获取成员相关媒体

        Args:
            user: 当前用户
            **filters: 过滤条件

        Returns:
            Tuple[List[MediaFile], int]: 媒体文件列表和总数
        """
        return self.list_media(user, **filters)

    def get_media_statistics(
        self, user: User, family_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取媒体统计信息

        Args:
            user: 当前用户
            family_id: 家族ID（可选）

        Returns:
            Dict[str, Any]: 统计信息
        """
        queryset = self.get_queryset(user)

        if family_id:
            queryset = queryset.filter(family_id=family_id)

        total_files = queryset.count()
        total_size = sum(media.file_size for media in queryset if media.file_size)

        # 按文件类型统计
        file_type_stats = {}
        for file_type in ["image", "video", "audio", "document"]:
            file_type_stats[f"{file_type}_count"] = queryset.filter(
                file_type=file_type
            ).count()

        return {
            "total_files": total_files,
            "total_size": total_size,
            "featured_count": queryset.filter(is_featured=True).count(),
            **file_type_stats,
            "category_distribution": [],
            "upload_timeline": [],
            "top_uploaders": [],
        }

    def _validate_file(self, file: UploadedFile) -> None:
        """
        验证上传文件

        Args:
            file: 上传的文件

        Raises:
            ValidationError: 验证失败
        """
        # 检查文件大小
        max_size = 100 * 1024 * 1024  # 100MB
        if file.size > max_size:
            raise ValidationError(f"文件大小不能超过{max_size // (1024 * 1024)}MB")

        # 检查文件类型
        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "video/mp4",
            "video/avi",
            "video/mov",
            "audio/mp3",
            "audio/wav",
            "audio/ogg",
            "application/pdf",
            "text/plain",
        ]

        content_type = getattr(file, "content_type", "")
        if content_type not in allowed_types:
            raise ValidationError(f"不支持的文件类型: {content_type}")

    def _get_file_type(self, file: UploadedFile) -> str:
        """
        获取文件类型

        Args:
            file: 上传的文件

        Returns:
            str: 文件类型
        """
        content_type = getattr(file, "content_type", "")

        if content_type.startswith("image/"):
            return "image"
        elif content_type.startswith("video/"):
            return "video"
        elif content_type.startswith("audio/"):
            return "audio"
        else:
            return "document"

    def _check_upload_permission(self, user: User, family_id: int) -> bool:
        """
        检查上传权限

        Args:
            user: 用户
            family_id: 家族ID

        Returns:
            bool: 是否有权限
        """
        # 简化权限检查，实际应该检查用户是否是家族成员
        return True

    def _check_edit_permission(self, user: User, media: MediaFile) -> bool:
        """
        检查编辑权限

        Args:
            user: 用户
            media: 媒体文件

        Returns:
            bool: 是否有权限
        """
        return user == media.uploader or user.is_superuser

    @classmethod
    def validate_create_data(
        cls, data: Dict[str, Any], user: User = None
    ) -> Dict[str, Any]:
        """
        验证创建数据

        Args:
            data: 创建数据
            user: 当前用户

        Returns:
            Dict[str, Any]: 验证后的数据

        Raises:
            ValidationError: 验证失败
        """
        # 验证必填字段
        if not data.get("title"):
            raise ValidationError("标题不能为空")

        # 验证标题长度
        if len(data["title"]) > 200:
            raise ValidationError("标题长度不能超过200个字符")

        # 验证描述长度
        if data.get("description") and len(data["description"]) > 1000:
            raise ValidationError("描述长度不能超过1000个字符")

        # 验证分类
        valid_categories = ["photo", "video", "audio", "document", "other"]
        if data.get("category") and data["category"] not in valid_categories:
            raise ValidationError(f"无效的分类，必须是: {', '.join(valid_categories)}")

        # 验证可见性
        valid_visibility = ["public", "family", "private"]
        if data.get("visibility") and data["visibility"] not in valid_visibility:
            raise ValidationError(
                f"无效的可见性设置，必须是: {', '.join(valid_visibility)}"
            )

        return data

    def _check_delete_permission(self, user: User, media: MediaFile) -> bool:
        """
        检查删除权限

        Args:
            user: 用户
            media: 媒体文件

        Returns:
            bool: 是否有权限
        """
        return user == media.uploader or user.is_superuser

    @classmethod
    def validate_update_data(
        cls, data: Dict[str, Any], user: User = None
    ) -> Dict[str, Any]:
        """
        验证更新数据

        Args:
            data: 更新数据
            user: 当前用户

        Returns:
            Dict[str, Any]: 验证后的数据

        Raises:
            ValidationError: 验证失败
        """
        # 验证标题长度
        if "title" in data and len(data["title"]) > 200:
            raise ValidationError("标题长度不能超过200个字符")

        # 验证描述长度
        if (
            "description" in data
            and data["description"]
            and len(data["description"]) > 1000
        ):
            raise ValidationError("描述长度不能超过1000个字符")

        # 验证分类
        valid_categories = ["photo", "video", "audio", "document", "other"]
        if "category" in data and data["category"] not in valid_categories:
            raise ValidationError(f"无效的分类，必须是: {', '.join(valid_categories)}")

        # 验证可见性
        valid_visibility = ["public", "family", "private"]
        if "visibility" in data and data["visibility"] not in valid_visibility:
            raise ValidationError(
                f"无效的可见性设置，必须是: {', '.join(valid_visibility)}"
            )

        return data
