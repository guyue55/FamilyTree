"""
媒体模块API接口定义

基于Django Ninja的API接口，提供媒体文件管理相关的所有API服务。
遵循Django Ninja最佳实践和Google Python Style Guide。

设计原则：
- 标准化的控制器模式：继承StandardCRUDController，统一接口设计
- 路由注册分离：将CRUD路由和自定义路由分开注册
- Schema驱动的数据处理：使用Pydantic Schema进行数据验证和序列化
- 服务层分离：业务逻辑委托给Service层，API层仅负责请求响应处理
- 统一的异常处理：使用标准化的异常类型和错误响应格式
- 一致的响应格式：所有API返回统一的响应结构
- 完整的日志记录：记录关键操作和错误信息
- 文件处理优化：支持单文件和批量文件上传处理
"""

# 导入模块
# 标准库导入
from typing import Optional, Dict, Any, List
from django.http import HttpRequest
from ninja.files import UploadedFile
from ninja import Router, Query, Path, File, Form
from loguru import logger

# 通用模块导入
from apps.common.api import StandardCRUDController
from apps.common.schemas import (
    ApiResponseSchema,
    PaginatedApiResponseSchema,
    SuccessResponseSchema,
)
from apps.common.utils import (
    create_success_response,
    create_paginated_response,
    get_request_id,
)
from apps.common.authentication import get_current_user
from apps.common.exceptions import (
    ValidationError,
    PermissionError,
    NotFoundError,
    OperationError,
)

# 本地模块导入
from .schemas import (
    MediaFileCreateSchema,
    MediaFileUpdateSchema,
    MediaFileResponseSchema,
    MediaSearchSchema,
    MediaBatchUploadSchema,
)
from .services import MediaService


class MediaController(StandardCRUDController):
    """
    媒体API控制器

    提供完整的媒体文件管理API接口，包括文件上传、下载、管理等功能。
    继承自StandardCRUDController，提供标准化的CRUD操作。

    主要功能：
    - 标准CRUD操作：媒体文件的增删改查
    - 文件上传：单文件和批量文件上传
    - 批量操作：批量删除、标签更新等
    - 媒体管理：家族相册、成员媒体、统计信息
    """

    # 配置服务类和Schema
    service_class = MediaService
    list_query_schema = MediaSearchSchema
    create_schema = MediaFileCreateSchema
    update_schema = MediaFileUpdateSchema

    def __init__(self):
        """初始化媒体控制器"""
        self.router = Router(tags=["媒体管理"])
        self.register_routes()

    def serialize_object(self, obj, user=None) -> Dict[str, Any]:
        """
        序列化媒体对象

        Args:
            obj: 媒体对象
            user: 当前用户（用于权限控制）

        Returns:
            Dict[str, Any]: 序列化后的数据
        """
        return {
            "id": obj.id,
            "family_id": obj.family_id,
            "member_id": obj.member_id,
            "title": obj.title,
            "description": obj.description,
            "file_type": obj.file_type,
            "file_path": obj.file_path,
            "file_url": obj.get_file_url()
            if hasattr(obj, "get_file_url")
            else obj.file_path,
            "file_size": obj.file_size,
            "mime_type": obj.mime_type,
            "width": obj.width,
            "height": obj.height,
            "duration": obj.duration,
            "thumbnail": obj.thumbnail,
            "tags": obj.tags,
            "privacy_level": obj.privacy_level,
            "is_featured": obj.is_featured,
            "uploaded_by": obj.uploaded_by_id,
            "created_at": obj.created_at.isoformat(),
            "updated_at": obj.updated_at.isoformat(),
            # 关联对象信息
            "member": {
                "id": obj.member.id,
                "name": obj.member.name,
                "avatar": obj.member.avatar,
            }
            if hasattr(obj, "member") and obj.member
            else None,
        }

    def register_routes(self) -> None:
        """注册所有路由"""
        self.register_crud_routes()
        self.register_custom_routes()

    def register_crud_routes(self) -> None:
        """注册标准CRUD路由"""

        @self.router.get(
            "/",
            response=PaginatedApiResponseSchema,
            summary="获取媒体列表",
            tags=["媒体管理"],
        )
        def list_media(request: HttpRequest, query: MediaSearchSchema = Query(...)):
            """获取媒体文件列表"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)

                filters = {
                    "family_id": query.family_id,
                    "member_id": getattr(query, "member_id", None),
                    "file_type": query.file_type,
                    "keyword": query.keyword,
                    "tags": query.tags,
                    "is_featured": query.is_featured,
                    "ordering": getattr(query, "ordering", None),
                    "page": query.page,
                    "page_size": query.page_size,
                }

                media_list, total = self.service_class.list_media(user, **filters)

                data = [self.serialize_object(m, user) for m in media_list]

                return create_paginated_response(
                    data=data,
                    total=total,
                    page=query.page,
                    page_size=query.page_size,
                    message="获取媒体列表成功",
                    request_id=request_id,
                )

            except (PermissionError, ValidationError) as e:
                raise e
            except Exception as e:
                logger.error(f"List media error: {e}")
                raise OperationError("获取媒体列表失败")

        @self.router.get(
            "/{media_id}",
            response=ApiResponseSchema,
            summary="获取媒体详情",
            tags=["媒体管理"],
        )
        def get_media(request: HttpRequest, media_id: int = Path(...)):
            """获取媒体文件详情"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)

                media = self.service_class.get_media(media_id, user)

                return create_success_response(
                    data=self.serialize_object(media, user),
                    message="获取媒体详情成功",
                    request_id=request_id,
                )

            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get media error: {e}")
                raise OperationError("获取媒体详情失败")

        @self.router.put(
            "/{media_id}",
            response=ApiResponseSchema,
            summary="更新媒体信息",
            tags=["媒体管理"],
        )
        def update_media(
            request: HttpRequest,
            media_id: int = Path(...),
            data: MediaFileUpdateSchema = ...,
        ):
            """更新媒体文件信息"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)

                media = self.service_class.update_media(
                    media_id, data.dict(exclude_unset=True), user
                )

                return create_success_response(
                    data=self.serialize_object(media, user),
                    message="媒体信息更新成功",
                    request_id=request_id,
                )

            except (NotFoundError, ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Update media error: {e}")
                raise OperationError("更新媒体信息失败")

        @self.router.delete(
            "/{media_id}",
            response=SuccessResponseSchema,
            summary="删除媒体文件",
            tags=["媒体管理"],
        )
        def delete_media(request: HttpRequest, media_id: int = Path(...)):
            """删除媒体文件"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)

                self.service_class.delete_media(media_id, user)

                return create_success_response(
                    message="媒体文件删除成功", request_id=request_id
                )

            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Delete media error: {e}")
                raise OperationError("删除媒体文件失败")

    def register_custom_routes(self) -> None:
        """注册自定义路由"""
        self._register_upload_routes()
        self._register_batch_routes()
        self._register_gallery_routes()
        self._register_statistics_routes()

    def _register_upload_routes(self) -> None:
        """注册文件上传路由"""

        @self.router.post(
            "/upload",
            response=ApiResponseSchema,
            summary="上传媒体文件",
            tags=["媒体管理"],
        )
        def upload_media(
            request: HttpRequest,
            file: UploadedFile = File(...),
            title: str = Form(...),
            description: Optional[str] = Form(None),
            family_id: Optional[int] = Form(None),
            member_id: Optional[int] = Form(None),
            tags: Optional[str] = Form(None),
            privacy_level: Optional[str] = Form("family"),
        ):
            """上传媒体文件"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)

                # 构建上传数据
                upload_data = {
                    "title": title,
                    "description": description,
                    "family_id": family_id,
                    "member_id": member_id,
                    "tags": tags.split(",") if tags else [],
                    "privacy_level": privacy_level,
                }

                media = self.service_class.upload_media(file, upload_data, user)

                return create_success_response(
                    data=self.serialize_object(media, user),
                    message="文件上传成功",
                    request_id=request_id,
                )

            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Upload media error: {e}")
                raise OperationError("文件上传失败")

        @self.router.post(
            "/upload/batch",
            response=ApiResponseSchema,
            summary="批量上传媒体文件",
            tags=["媒体管理"],
        )
        def batch_upload_media(
            request: HttpRequest,
            files: List[UploadedFile] = File(...),
            family_id: Optional[int] = Form(None),
            member_id: Optional[int] = Form(None),
            privacy_level: Optional[str] = Form("family"),
        ):
            """批量上传媒体文件"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)

                upload_data = {
                    "family_id": family_id,
                    "member_id": member_id,
                    "privacy_level": privacy_level,
                }

                result = self.service_class.batch_upload_media(files, upload_data, user)

                return create_success_response(
                    data={
                        "uploaded_count": result["uploaded_count"],
                        "failed_count": result["failed_count"],
                        "uploaded_media": [
                            self.serialize_object(m, user)
                            for m in result["uploaded_media"]
                        ],
                        "errors": result["errors"],
                    },
                    message=f"批量上传完成，成功{result['uploaded_count']}个，失败{result['failed_count']}个",
                    request_id=request_id,
                )

            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Batch upload media error: {e}")
                raise OperationError("批量上传失败")

    def _register_batch_routes(self) -> None:
        """注册批量操作路由"""

        @self.router.delete(
            "/batch",
            response=SuccessResponseSchema,
            summary="批量删除媒体文件",
            tags=["媒体管理"],
        )
        def batch_delete_media(request: HttpRequest, media_ids: List[int]):
            """批量删除媒体文件"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)

                result = self.service_class.batch_delete_media(media_ids, user)

                return create_success_response(
                    data={
                        "deleted_count": result["deleted_count"],
                        "failed_count": result["failed_count"],
                        "errors": result["errors"],
                    },
                    message=f"批量删除完成，成功{result['deleted_count']}个，失败{result['failed_count']}个",
                    request_id=request_id,
                )

            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Batch delete media error: {e}")
                raise OperationError("批量删除媒体文件失败")

        @self.router.put(
            "/batch/tags",
            response=SuccessResponseSchema,
            summary="批量更新标签",
            tags=["媒体管理"],
        )
        def batch_update_tags(
            request: HttpRequest, media_ids: List[int], tags: List[str]
        ):
            """批量更新媒体文件标签"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)

                result = self.service_class.batch_update_tags(media_ids, tags, user)

                return create_success_response(
                    data={
                        "updated_count": result["updated_count"],
                        "failed_count": result["failed_count"],
                        "errors": result["errors"],
                    },
                    message=f"批量更新标签完成，成功{result['updated_count']}个，失败{result['failed_count']}个",
                    request_id=request_id,
                )

            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Batch update tags error: {e}")
                raise OperationError("批量更新标签失败")

    def _register_gallery_routes(self) -> None:
        """注册相册管理路由"""

        @self.router.get(
            "/family/{family_id}/gallery",
            response=PaginatedApiResponseSchema,
            summary="获取家族相册",
            tags=["媒体管理"],
        )
        def get_family_gallery(
            request: HttpRequest,
            family_id: int = Path(...),
            query: MediaSearchSchema = Query(...),
        ):
            """获取家族相册"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)

                filters = {
                    "family_id": family_id,
                    "file_type": "image",
                    "ordering": getattr(query, "ordering", None) or "-created_at",
                    "page": query.page,
                    "page_size": query.page_size,
                }

                media_list, total = self.service_class.get_family_gallery(
                    user, **filters
                )

                data = [self.serialize_object(m, user) for m in media_list]

                return create_paginated_response(
                    data=data,
                    total=total,
                    page=query.page,
                    page_size=query.page_size,
                    message="获取家族相册成功",
                    request_id=request_id,
                )

            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get family gallery error: {e}")
                raise OperationError("获取家族相册失败")

        @self.router.get(
            "/member/{member_id}/media",
            response=PaginatedApiResponseSchema,
            summary="获取成员媒体",
            tags=["媒体管理"],
        )
        def get_member_media(
            request: HttpRequest,
            member_id: int = Path(...),
            query: MediaSearchSchema = Query(...),
        ):
            """获取成员相关媒体"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)

                filters = {
                    "member_id": member_id,
                    "file_type": query.file_type,
                    "ordering": getattr(query, "ordering", None) or "-created_at",
                    "page": query.page,
                    "page_size": query.page_size,
                }

                media_list, total = self.service_class.get_member_media(user, **filters)

                data = [self.serialize_object(m, user) for m in media_list]

                return create_paginated_response(
                    data=data,
                    total=total,
                    page=query.page,
                    page_size=query.page_size,
                    message="获取成员媒体成功",
                    request_id=request_id,
                )

            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get member media error: {e}")
                raise OperationError("获取成员媒体失败")

    def _register_statistics_routes(self) -> None:
        """注册统计信息路由"""

        @self.router.get(
            "/statistics",
            response=ApiResponseSchema,
            summary="获取媒体统计",
            tags=["媒体管理"],
        )
        def get_media_statistics(
            request: HttpRequest, family_id: Optional[int] = Query(None)
        ):
            """获取媒体统计信息"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)

                stats = self.service_class.get_media_statistics(user, family_id)

                return create_success_response(
                    data=stats, message="获取媒体统计成功", request_id=request_id
                )

            except (PermissionError, ValidationError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get media statistics error: {e}")
                raise OperationError("获取媒体统计失败")


# 创建控制器实例
media_controller = MediaController()
router = media_controller.router
media_router = router  # 为了兼容性添加别名


# ==================== 导出 ====================

__all__ = ["MediaController", "media_controller", "router", "media_router"]
