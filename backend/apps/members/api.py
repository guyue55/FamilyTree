"""
成员模块API接口定义

基于Django Ninja的API接口，提供家族成员管理相关的所有API服务。
遵循Django Ninja最佳实践和Google Python Style Guide。
"""

from typing import Optional, Dict, Any, List
from django.http import HttpRequest
from ninja import Router, Query, Path
from loguru import logger

from apps.common.api import StandardCRUDController
from apps.common.schemas import (
    ApiResponseSchema, PaginatedApiResponseSchema, SuccessResponseSchema
)
from apps.common.utils import (
    create_success_response, create_paginated_response, 
    get_request_id
)
from apps.common.authentication import get_current_user
from apps.common.exceptions import (
    ValidationError, PermissionError, NotFoundError, OperationError
)
from .schemas import (
    MemberCreateSchema, MemberUpdateSchema, MemberResponseSchema,
    MemberQuerySchema, MemberBatchCreateSchema
)
from .services import MemberService


class MemberController(StandardCRUDController):
    """
    成员API控制器
    
    提供完整的家族成员管理API接口，包括成员的增删改查、批量操作等功能。
    """
    
    service_class = MemberService
    
    def __init__(self):
        super().__init__()
        self.service = self.service_class()
    
    def serialize_object(self, obj, user=None) -> Dict[str, Any]:
        """
        序列化成员对象
        
        Args:
            obj: 成员对象
            user: 当前用户（用于权限控制）
            
        Returns:
            Dict[str, Any]: 序列化后的数据
        """
        return {
            "id": obj.id,
            "family_id": obj.family_id,
            "name": obj.name,
            "gender": obj.gender,
            "birth_date": obj.birth_date.isoformat() if obj.birth_date else None,
            "death_date": obj.death_date.isoformat() if obj.death_date else None,
            "birth_place": obj.birth_place,
            "current_address": obj.current_address,
            "occupation": obj.occupation,
            "education": obj.education,
            "bio": obj.bio,
            "avatar": obj.avatar,
            "is_alive": obj.is_alive,
            "generation": obj.generation,
            "sort_order": obj.sort_order,
            "privacy_level": obj.privacy_level,
            "created_by": obj.created_by_id,
            "created_at": obj.created_at.isoformat(),
            "updated_at": obj.updated_at.isoformat()
        }
    
    def register_routes(self) -> None:
        """注册所有路由"""
        self.register_crud_routes()
        self.register_batch_routes()
        self.register_search_routes()
    
    def register_crud_routes(self) -> None:
        """注册CRUD路由"""
        
        @self.router.post("/", response=ApiResponseSchema, summary="创建成员")
        def create_member(request: HttpRequest, data: MemberCreateSchema):
            """创建家族成员"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)
                
                member = self.service.create_member(data.dict(), user)
                
                return create_success_response(
                    data=self.serialize_object(member, user),
                    message="成员创建成功",
                    request_id=request_id
                )
                
            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Create member error: {e}")
                raise OperationError("创建成员失败")
        
        @self.router.get("/", response=PaginatedApiResponseSchema, summary="获取成员列表")
        def list_members(request: HttpRequest, query: MemberQuerySchema = Query(...)):
            """获取家族成员列表"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)
                
                filters = {
                    'family_id': query.family_id,
                    'keyword': query.search,
                    'gender': query.gender,
                    'generation': query.generation,
                    'is_alive': query.is_alive,
                    'ordering': query.ordering,
                    'page': query.page,
                    'page_size': query.page_size
                }
                
                members, total = self.service.list_members(user, **filters)
                
                data = [self.serialize_object(m, user) for m in members]
                
                return create_paginated_response(
                    data=data,
                    total=total,
                    page=query.page,
                    page_size=query.page_size,
                    message="获取成员列表成功",
                    request_id=request_id
                )
                
            except (PermissionError, ValidationError) as e:
                raise e
            except Exception as e:
                logger.error(f"List members error: {e}")
                raise OperationError("获取成员列表失败")
        
        @self.router.get("/{member_id}", response=ApiResponseSchema, summary="获取成员详情")
        def get_member(request: HttpRequest, member_id: int = Path(...)):
            """获取成员详情"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)
                
                member = self.service.get_member(member_id, user)
                
                return create_success_response(
                    data=self.serialize_object(member, user),
                    message="获取成员详情成功",
                    request_id=request_id
                )
                
            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get member error: {e}")
                raise OperationError("获取成员详情失败")
        
        @self.router.put("/{member_id}", response=ApiResponseSchema, summary="更新成员信息")
        def update_member(request: HttpRequest, member_id: int = Path(...), data: MemberUpdateSchema = ...):
            """更新成员信息"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)
                
                member = self.service.update_member(
                    member_id, data.dict(exclude_unset=True), user
                )
                
                return create_success_response(
                    data=self.serialize_object(member, user),
                    message="成员信息更新成功",
                    request_id=request_id
                )
                
            except (NotFoundError, ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Update member error: {e}")
                raise OperationError("更新成员信息失败")
        
        @self.router.delete("/{member_id}", response=SuccessResponseSchema, summary="删除成员")
        def delete_member(request: HttpRequest, member_id: int = Path(...)):
            """删除成员"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)
                
                self.service.delete_member(member_id, user)
                
                return create_success_response(
                    message="成员删除成功",
                    request_id=request_id
                )
                
            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Delete member error: {e}")
                raise OperationError("删除成员失败")
    
    def register_batch_routes(self) -> None:
        """注册批量操作路由"""
        
        @self.router.post("/batch", response=ApiResponseSchema, summary="批量创建成员")
        def batch_create_members(request: HttpRequest, data: MemberBatchCreateSchema):
            """批量创建家族成员"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)
                
                result = self.service.batch_create_members(data.members, user)
                
                return create_success_response(
                    data={
                        "created_count": result['created_count'],
                        "failed_count": result['failed_count'],
                        "created_members": [
                            self.serialize_object(m, user) for m in result['created_members']
                        ],
                        "errors": result['errors']
                    },
                    message=f"批量创建完成，成功{result['created_count']}个，失败{result['failed_count']}个",
                    request_id=request_id
                )
                
            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Batch create members error: {e}")
                raise OperationError("批量创建成员失败")
        
        @self.router.delete("/batch", response=SuccessResponseSchema, summary="批量删除成员")
        def batch_delete_members(request: HttpRequest, member_ids: List[int]):
            """批量删除成员"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)
                
                result = self.service.batch_delete_members(member_ids, user)
                
                return create_success_response(
                    data={
                        "deleted_count": result['deleted_count'],
                        "failed_count": result['failed_count'],
                        "errors": result['errors']
                    },
                    message=f"批量删除完成，成功{result['deleted_count']}个，失败{result['failed_count']}个",
                    request_id=request_id
                )
                
            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Batch delete members error: {e}")
                raise OperationError("批量删除成员失败")
    
    def register_search_routes(self) -> None:
        """注册搜索路由"""
        
        @self.router.get("/search", response=PaginatedApiResponseSchema, summary="搜索成员")
        def search_members(request: HttpRequest, query: MemberQuerySchema = Query(...)):
            """搜索家族成员"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)
                
                if not query.search:
                    raise ValidationError("搜索关键词不能为空")
                
                filters = {
                    'family_id': query.family_id,
                    'keyword': query.search,
                    'gender': query.gender,
                    'generation': query.generation,
                    'is_alive': query.is_alive,
                    'ordering': query.ordering,
                    'page': query.page,
                    'page_size': query.page_size
                }
                
                members, total = self.service.search_members(user, **filters)
                
                data = [self.serialize_object(m, user) for m in members]
                
                return create_paginated_response(
                    data=data,
                    total=total,
                    page=query.page,
                    page_size=query.page_size,
                    message=f"搜索到{total}个相关成员",
                    request_id=request_id
                )
                
            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Search members error: {e}")
                raise OperationError("搜索成员失败")
        
        @self.router.get("/family/{family_id}/tree", response=ApiResponseSchema, summary="获取家族树")
        def get_family_tree(request: HttpRequest, family_id: int = Path(...)):
            """获取家族树结构"""
            try:
                user = get_current_user(request)
                request_id = get_request_id(request)
                
                tree_data = self.service.get_family_tree(family_id, user)
                
                return create_success_response(
                    data=tree_data,
                    message="获取家族树成功",
                    request_id=request_id
                )
                
            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get family tree error: {e}")
                raise OperationError("获取家族树失败")


# 创建控制器实例
member_controller = MemberController()
router = member_controller.router


# ==================== 导出 ====================

__all__ = [
    'MemberController',
    'router',
    'MemberCreateSchema',
    'MemberUpdateSchema',
    'MemberQuerySchema',
    'MemberBatchCreateSchema'
]