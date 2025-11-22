from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from loguru import logger
from ninja import Router, Query, Path
from apps.common.authentication import JWTAuth, get_current_user
from apps.common.exceptions import (
    OperationError,
    ValidationError,
    PermissionError,
    NotFoundError
)
from apps.common.schemas import (
    ApiResponseSchema,
    PaginatedApiResponseSchema
)
from apps.common.api import StandardCRUDController
from apps.common import utils as common_utils
from .services import FamilyService
from .schemas import (
    FamilyCreateSchema,
    FamilyUpdateSchema,
    FamilyQuerySchema,
    PublicFamilyQuerySchema,
    FamilySettingsSchema,
    FamilyInvitationCreateSchema,
    FamilyInvitationProcessSchema,
    FamilyResponseSchema,
    FamilySettingsResponseSchema,
    FamilyInvitationResponseSchema
)
from apps.members.schemas import FamilyMembershipResponseSchema
from .permissions import (
    get_user_family_permissions,
    PermissionSchema,
    FamilyPermissionChecker,
    FamilyPermission,
    check_invitation_permission
)

"""
Family应用API接口定义

基于Django Ninja的API接口，整合了原有功能和V2重构功能。
提供家族管理相关的所有API服务，遵循Django Ninja最佳实践。

架构设计原则：
1. API层仅提供接口服务，不直接操作模型
2. 所有业务逻辑通过Service层处理
3. 统一的依赖管理和异常处理
4. 遵循Django Ninja框架最佳实践
5. 标准化的控制器模式和路由组织
6. 统一的错误处理和响应格式
"""

User = get_user_model()

# ==================== Controller ====================

class FamilyController(StandardCRUDController):
    """
    家族API控制器

    基于Django Ninja框架的标准化API控制器。
    提供家族管理相关的所有API接口，包括CRUD操作和自定义功能。
    遵循标准化的API设计模式。
    """

    # 服务类配置
    service_class = FamilyService

    # Schema配置
    list_query_schema = FamilyQuerySchema
    create_schema = FamilyCreateSchema
    update_schema = FamilyUpdateSchema

    def __init__(self):
        self.router = Router(auth=JWTAuth(), tags=["家族管理"])
        self.register_routes()

    def serialize_object(self, obj, user=None) -> Dict[str, Any]:
        """
        序列化家族对象

        Args:
            obj: 家族对象
            user: 当前用户（用于权限控制）

        Returns:
            Dict[str, Any]: 序列化后的数据
        """
        return {
            "id": obj.id,
            "name": obj.name,
            "description": obj.description,
            "creator_id": obj.creator_id,
            "avatar": obj.avatar.url if obj.avatar else None,
            "cover_image": obj.cover_image.url if obj.cover_image else None,
            "visibility": obj.visibility,
            "is_active": obj.is_active,
            "allow_join": obj.allow_join,
            "member_count": obj.member_count,
            "generation_count": obj.generation_count,
            "tags": obj.tags,
            "origin_location": obj.origin_location,
            "motto": obj.motto,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }

    def register_routes(self) -> None:
        """注册所有路由"""
        self.register_crud_routes()
        self.register_custom_routes()

    def register_crud_routes(self) -> None:
        """注册标准CRUD路由"""

        @self.router.get("/", response=PaginatedApiResponseSchema, summary="获取家族列表", tags=["家族管理"])
        def list_families(request: HttpRequest, query: FamilyQuerySchema = Query(...)):
            """获取家族列表"""
            try:
                user = get_current_user(request)

                # 利用Schema的数据构建过滤条件
                filters = query.dict(exclude_unset=True)

                families, total = self.service_class.list_families(user, **filters)

                # 使用Schema序列化数据，避免手动构建字典
                def serialize_family(family):
                    """序列化家族对象"""
                    return FamilyResponseSchema.from_orm(family).dict()

                data = [serialize_family(family) for family in families]

                return common_utils.create_paginated_response(
                    data=data,
                    total=total,
                    page=query.page,
                    page_size=query.page_size,
                    message="获取家族列表成功",
                    request_id=common_utils.get_request_id(request)
                )

            except Exception as e:
                logger.error(f"List families error: {e}")
                raise OperationError("获取家族列表失败")

        @self.router.post("/", response=ApiResponseSchema, summary="创建家族", tags=["家族管理"])
        def create_family(request: HttpRequest, family_data: FamilyCreateSchema):
            """创建新家族"""
            try:
                user = get_current_user(request)

                # 获取Schema数据并补充默认值
                data = family_data.dict()
                
                # 确保所有可能的必需字段有默认值
                defaults = {
                    'tags': '',
                    'origin_location': '',
                    'motto': '',
                    'description': '',
                    'is_active': True,
                    'member_count': 1,  # 创建者算一个成员
                    'generation_count': 1,  # 至少有一代
                    'visibility': 'family',
                    'allow_join': True
                }
                
                # 为缺失的字段设置默认值
                for key, default_value in defaults.items():
                    if key not in data or data[key] is None:
                        data[key] = default_value

                family = self.service_class.create_family(data, user)

                # 使用Schema序列化响应数据
                data = FamilyResponseSchema.from_orm(family).dict()

                return common_utils.create_success_response(
                    data=data,
                    message="创建家族成功",
                    request_id=common_utils.get_request_id(request)
                )

            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Create family error: {e}")
                raise OperationError("创建家族失败")

        @self.router.get("/{family_id}", response=ApiResponseSchema, summary="获取家族详情", tags=["家族管理"])
        def get_family(request: HttpRequest, family_id: int = Path(...)):
            """获取家族详细信息"""
            try:
                user = get_current_user(request)

                family = self.service_class.get_family_detail(family_id, user)

                # 使用Schema序列化响应数据
                data = FamilyResponseSchema.from_orm(family).dict()

                return common_utils.create_success_response(
                    data=data,
                    message="获取家族信息成功",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get family error: {e}")
                raise OperationError("获取家族信息失败")

        @self.router.put("/{family_id}", response=ApiResponseSchema, summary="更新家族信息", tags=["家族管理"])
        def update_family(request: HttpRequest, family_data: FamilyUpdateSchema, family_id: int = Path(...)):
            """更新家族基本信息"""
            try:
                user = get_current_user(request)

                # 使用Schema的exclude_unset功能，只更新提供的字段
                family = self.service_class.update_family(
                    family_id, family_data.dict(exclude_unset=True), user
                )

                # 使用Schema序列化响应数据
                data = FamilyResponseSchema.from_orm(family).dict()

                return common_utils.create_success_response(
                    data=data,
                    message="更新家族信息成功",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError, ValidationError) as e:
                raise e
            except Exception as e:
                logger.error(f"Update family error: {e}")
                raise OperationError("更新家族信息失败")

        @self.router.delete("/{family_id}", response=ApiResponseSchema, summary="删除家族", tags=["家族管理"])
        def delete_family(request: HttpRequest, family_id: int = Path(...)):
            """删除家族"""
            try:
                user = get_current_user(request)
                self.service_class.delete_family(family_id, user)

                return common_utils.create_success_response(
                    data={"family_id": family_id, "deleted": True},
                    message="家族删除成功",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Delete family error: {e}")
                raise OperationError("删除家族失败")

    def register_custom_routes(self) -> None:
        """注册自定义路由"""

        # 公开家族搜索
        @self.router.get("/public", response=PaginatedApiResponseSchema, summary="搜索公开家族", tags=["家族搜索"], auth=None)
        def search_public_families(request: HttpRequest, query: PublicFamilyQuerySchema = Query(...)):
            """搜索公开家族"""
            try:
                # 构建搜索过滤器，利用Schema的数据
                filters = query.dict(exclude_unset=True)

                families, total = self.service_class.search_public_families(**filters)

                # 使用Schema序列化数据
                data = [FamilyResponseSchema.from_orm(family).dict() for family in families]

                return common_utils.create_paginated_response(
                    data=data,
                    total=total,
                    page=query.page,
                    page_size=query.page_size,
                    message="搜索公开家族成功",
                    request_id=common_utils.get_request_id(request)
                )

            except Exception as e:
                logger.error(f"Search public families error: {e}")
                raise OperationError("搜索公开家族失败")

        # 家族权限管理
        @self.router.get("/{family_id}/permissions", response=ApiResponseSchema, summary="获取家族权限信息", tags=["家族权限"])
        def get_family_permissions(request: HttpRequest, family_id: int = Path(...)):
            """获取当前用户在家族中的权限信息"""
            try:
                user = get_current_user(request)
                family = self.service_class.get_family_detail(family_id, user)

                # 使用已定义的权限Schema和函数
                permission_info = get_user_family_permissions(user, family)

                # 添加额外的业务逻辑信息
                data = permission_info.dict()
                data.update({
                    "can_join": family.allow_join and not permission_info.is_member,
                    "can_view": True,  # 能访问此API说明已有查看权限
                    "family_id": family.id,
                    "family_name": family.name
                })

                return common_utils.create_success_response(
                    data=data,
                    message="获取权限信息成功",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get family permissions error: {e}")
                raise OperationError("获取权限信息失败")

        @self.router.get("/{family_id}/statistics", response=ApiResponseSchema, summary="获取家族统计信息", tags=["家族统计"])
        def get_family_statistics(request: HttpRequest, family_id: int = Path(...)):
            """获取家族统计信息"""
            try:
                user = get_current_user(request)
                statistics = self.service_class.get_family_statistics(family_id, user)

                # 如果service返回的是dict，直接使用；如果是对象，可以考虑使用Schema序列化
                return common_utils.create_success_response(
                    data=statistics,
                    message="获取家族统计信息成功",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get family statistics error: {e}")
                raise OperationError("获取家族统计信息失败")

        # 家族成员管理
        @self.router.post("/{family_id}/join", response=ApiResponseSchema, summary="加入家族", tags=["家族成员"])
        def join_family(request: HttpRequest, family_id: int = Path(...)):
            """加入家族"""
            try:
                user = get_current_user(request)
                result = self.service_class.join_family(family_id, user)

                # 如果service返回详细信息，使用它；否则返回简单的成功信息
                if isinstance(result, dict):
                    data = result
                else:
                    data = {"success": result, "family_id": family_id, "user_id": user.id}

                return common_utils.create_success_response(
                    data=data,
                    message="成功加入家族",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError, ValidationError) as e:
                raise e
            except Exception as e:
                logger.error(f"Join family error: {e}")
                raise OperationError("加入家族失败")

        @self.router.post("/{family_id}/leave", response=ApiResponseSchema, summary="离开家族", tags=["家族成员"])
        def leave_family(request: HttpRequest, family_id: int = Path(...)):
            """离开家族"""
            try:
                user = get_current_user(request)
                result = self.service_class.leave_family(family_id, user)

                # 如果service返回详细信息，使用它；否则返回简单的成功信息
                if isinstance(result, dict):
                    data = result
                else:
                    data = {"success": result, "family_id": family_id, "user_id": user.id}

                return common_utils.create_success_response(
                    data=data,
                    message="已离开家族",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError, ValidationError) as e:
                raise e
            except Exception as e:
                logger.error(f"Leave family error: {e}")
                raise OperationError("离开家族失败")

        # 家族设置管理
        @self.router.get("/{family_id}/settings", response=ApiResponseSchema, summary="获取家族设置", tags=["家族设置"])
        def get_family_settings(request: HttpRequest, family_id: int = Path(...)):
            """获取家族设置"""
            try:
                user = get_current_user(request)

                # 使用Service层获取家族设置
                settings = self.service_class.get_family_settings(family_id, user)

                # 使用Schema自动序列化
                data = FamilySettingsResponseSchema.from_orm(settings).dict()

                return common_utils.create_success_response(
                    data=data,
                    message="获取家族设置成功",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get family settings error: {e}")
                raise OperationError("获取家族设置失败")

        @self.router.put("/{family_id}/settings", response=ApiResponseSchema, summary="更新家族设置", tags=["家族设置"])
        def update_family_settings(request: HttpRequest, settings_data: FamilySettingsSchema, family_id: int = Path(...)):
            """更新家族设置"""
            try:
                user = get_current_user(request)

                # 使用Service层更新家族设置
                update_data = settings_data.dict(exclude_unset=True)
                settings = self.service_class.update_family_settings(family_id, update_data, user)

                # 使用Schema自动序列化响应
                response_data = FamilySettingsResponseSchema.from_orm(settings).dict()

                return common_utils.create_success_response(
                    data=response_data,
                    message="更新家族设置成功",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError, ValidationError) as e:
                raise e
            except Exception as e:
                logger.error(f"Update family settings error: {e}")
                raise OperationError("更新家族设置失败")

        # 家族邀请管理
        @self.router.get("/{family_id}/invitations", response=PaginatedApiResponseSchema, summary="获取家族邀请列表", tags=["家族邀请"])
        def list_family_invitations(
            request: HttpRequest,
            family_id: int = Path(...),
            status: Optional[str] = Query(None),
            page: int = Query(1, ge=1),
            page_size: int = Query(20, ge=1, le=100)
        ):
            """获取家族邀请列表"""
            try:
                user = get_current_user(request)

                # 使用Service层获取邀请列表
                invitations, total = self.service_class.get_family_invitations(
                    family_id=family_id,
                    user=user,
                    status=status,
                    page=page,
                    page_size=page_size
                )

                def serialize_invitation(invitation):
                    """序列化邀请对象"""
                    return FamilyInvitationResponseSchema.from_orm(invitation).dict()

                data = [serialize_invitation(invitation) for invitation in invitations]

                return common_utils.create_paginated_response(
                    data=data,
                    total=total,
                    page=page,
                    page_size=page_size,
                    message="获取邀请列表成功",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"List family invitations error: {e}")
                raise OperationError("获取邀请列表失败")

        @self.router.post("/{family_id}/invitations", response=ApiResponseSchema, summary="创建家族邀请", tags=["家族邀请"])
        def create_family_invitation(request: HttpRequest, invitation_data: FamilyInvitationCreateSchema, family_id: int = Path(...)):
            """创建家族邀请"""
            try:
                user = get_current_user(request)

                # 使用Service层创建邀请
                invitation_dict = invitation_data.dict(exclude_unset=True)
                invitation = self.service_class.create_family_invitation(
                    family_id=family_id,
                    invitation_data=invitation_dict,
                    user=user
                )

                # TODO: 发送邀请邮件

                # 使用Schema自动序列化
                data = FamilyInvitationResponseSchema.from_orm(invitation).dict()

                return common_utils.create_success_response(
                    data=data,
                    message="邀请发送成功",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError, ValidationError) as e:
                raise e
            except Exception as e:
                logger.error(f"Create family invitation error: {e}")
                raise OperationError("创建邀请失败")

        @self.router.get("/invitations/{invitation_id}", response=ApiResponseSchema, summary="获取邀请详情", tags=["家族邀请"])
        def get_invitation(request: HttpRequest, invitation_id: int = Path(...)):
            """获取邀请详情"""
            try:
                user = get_current_user(request)

                # 使用Service层获取邀请详情
                invitation = self.service_class.get_invitation_detail(invitation_id, user)

                # 使用Schema自动序列化
                data = FamilyInvitationResponseSchema.from_orm(invitation).dict()

                return common_utils.create_success_response(
                    data=data,
                    message="获取邀请详情成功",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get invitation detail error: {e}")
                raise OperationError("获取邀请详情失败")

        @self.router.post("/invitations/{invitation_id}/accept", response=ApiResponseSchema, summary="接受邀请", tags=["家族邀请"])
        def accept_invitation(request: HttpRequest, invitation_id: int = Path(...)):
            """接受家族邀请"""
            try:
                user = get_current_user(request)

                # 使用Service层接受邀请
                result = self.service_class.accept_invitation(invitation_id, user)
                member = result['member']
                invitation = result['invitation']

                # 使用ModelSchema自动序列化响应数据
                data = FamilyMembershipResponseSchema.from_orm(member).dict()
                data.update({
                    "invitation_id": invitation.id,
                    "invitation_status": invitation.status,
                    "processed_at": invitation.processed_at.isoformat()
                })

                return common_utils.create_success_response(
                    data=data,
                    message="成功加入家族",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError, ValidationError) as e:
                raise e
            except Exception as e:
                logger.error(f"Accept invitation error: {e}")
                raise OperationError("接受邀请失败")

        @self.router.post("/invitations/{invitation_id}/reject", response=ApiResponseSchema, summary="拒绝邀请", tags=["家族邀请"])
        def reject_invitation(request: HttpRequest, invitation_id: int = Path(...)):
            """拒绝家族邀请"""
            try:
                user = get_current_user(request)

                # 使用Service层拒绝邀请
                invitation = self.service_class.reject_invitation(invitation_id, user)

                # 使用Schema自动序列化
                data = FamilyInvitationResponseSchema.from_orm(invitation).dict()

                return common_utils.create_success_response(
                    data=data,
                    message="已拒绝邀请",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Reject invitation error: {e}")
                raise OperationError("拒绝邀请失败")

        @self.router.delete("/invitations/{invitation_id}", response=ApiResponseSchema, summary="取消邀请", tags=["家族邀请"])
        def cancel_invitation(request: HttpRequest, invitation_id: int = Path(...)):
            """取消家族邀请（仅邀请者或家族管理员可操作）"""
            try:
                user = get_current_user(request)

                # 使用Service层取消邀请
                invitation = self.service_class.cancel_invitation(invitation_id, user)

                return common_utils.create_success_response(
                    data={
                        "invitation_id": invitation.id,
                        "status": invitation.status,
                        "cancelled": True
                    },
                    message="邀请已取消",
                    request_id=common_utils.get_request_id(request)
                )

            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Cancel invitation error: {e}")
                raise OperationError("取消邀请失败")

# ==================== 导出 ====================

family_controller = FamilyController()
router = family_controller.router
family_router = router  # 为了兼容性添加别名

# 创建占位符路由器，避免导入错误
members_router = Router(auth=JWTAuth(), tags=["成员管理"])
relationships_router = Router(auth=JWTAuth(), tags=["关系管理"])

# TODO: 实现成员管理和关系管理的具体路由

__all__ = [
    "FamilyController",
    "family_controller",
    "router",
    "family_router",
    "members_router",
    "relationships_router"
]
