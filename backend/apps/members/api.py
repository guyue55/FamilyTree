"""
Members应用API接口定义

基于Django Ninja的API接口，提供家族成员管理相关的所有API服务。
遵循Django Ninja最佳实践和标准化架构设计。

设计原则：
1. 统一的API控制器模式 - 继承StandardCRUDController
2. 标准化的路由注册 - 分离CRUD和自定义路由
3. Schema驱动的数据处理 - 使用Pydantic Schema进行验证和序列化
4. 服务层分离 - 业务逻辑委托给Service层处理
5. 统一的异常处理 - 使用标准化异常类型
6. 一致的响应格式 - 使用通用响应Schema
7. 完整的权限控制 - 基于JWT的身份验证和授权
8. 标准化的日志记录 - 统一的错误日志格式
"""

# ============================================================================
# 导入模块
# ============================================================================

# 标准库导入
from typing import Optional, Dict, Any, List

# Django框架导入
from django.http import HttpRequest

# 第三方库导入
from ninja import Router, Query, Path
from loguru import logger

# 公共模块导入
from apps.common.api import StandardCRUDController
from apps.common.schemas import (
    ApiResponseSchema, 
    PaginatedApiResponseSchema, 
    SuccessResponseSchema
)
from apps.common.utils import (
    create_success_response, 
    create_paginated_response, 
    get_request_id
)
from apps.common.authentication import JWTAuth, get_current_user
from apps.common.exceptions import (
    ValidationError, 
    PermissionError, 
    NotFoundError, 
    OperationError
)

# 本地应用导入
from .schemas import (
    MemberCreateSchema, 
    MemberUpdateSchema, 
    MemberResponseSchema,
    MemberQuerySchema, 
    MemberBatchCreateSchema
)
from .services import MemberService
from apps.relationships.models import Relationship
from .models import Member


# ============================================================================
# 成员管理API控制器
# ============================================================================


class MemberController(StandardCRUDController):
    """
    成员API控制器
    
    基于Django Ninja框架的标准化API控制器。
    遵循架构设计原则：
    1. 仅处理HTTP请求和响应
    2. 业务逻辑委托给Service层
    3. 使用Schema进行数据序列化
    4. 统一的异常处理和日志记录
    """
    
    service_class = MemberService
    
    # Schema配置
    list_query_schema = MemberQuerySchema
    create_schema = MemberCreateSchema
    update_schema = MemberUpdateSchema
    
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
    
    def __init__(self):
        super().__init__()
        self.router = Router(auth=JWTAuth(), tags=["成员管理"])
        self.register_routes()
    
    def register_routes(self) -> None:
        """注册所有路由"""
        self.register_crud_routes()
        self.register_custom_routes()
    
    def register_crud_routes(self) -> None:
        """注册标准CRUD路由"""
        
        @self.router.get("/", response=PaginatedApiResponseSchema, summary="获取成员列表", tags=["成员管理"])
        def list_members(request: HttpRequest, query: MemberQuerySchema = Query(...)):
            """获取家族成员列表"""
            try:
                
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
                
                members, total = self.service_class.list_members(user, **filters)
                
                data = [self.serialize_object(m, user) for m in members]
                
                return create_paginated_response(
                    data=data,
                    total=total,
                    page=query.page,
                    page_size=query.page_size,
                    message="获取成员列表成功",
                    request_id=get_request_id(request)
                )
                
            except (PermissionError, ValidationError) as e:
                raise e
            except Exception as e:
                logger.error(f"List members error: {e}")
                raise OperationError("获取成员列表失败")
        
        @self.router.post("/", response=ApiResponseSchema, summary="创建成员", tags=["成员管理"])
        def create_member(request: HttpRequest, data: MemberCreateSchema):
            """创建家族成员"""
            try:
                user = get_current_user(request)
                
                member = self.service_class.create_member(data.dict(), user)
                
                return create_success_response(
                    data=self.serialize_object(member, user),
                    message="成员创建成功",
                    request_id=get_request_id(request)
                )
                
            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Create member error: {e}")
                raise OperationError("创建成员失败")
        
        @self.router.get("/{member_id}", response=ApiResponseSchema, summary="获取成员详情", tags=["成员管理"])
        def get_member(request: HttpRequest, member_id: int = Path(...)):
            """获取成员详情"""
            try:
                user = get_current_user(request)
                
                member = self.service_class.get_member(member_id, user)
                
                return create_success_response(
                    data=self.serialize_object(member, user),
                    message="获取成员详情成功",
                    request_id=get_request_id(request)
                )
                
            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get member error: {e}")
                raise OperationError("获取成员详情失败")
        
        @self.router.put("/{member_id}", response=ApiResponseSchema, summary="更新成员信息", tags=["成员管理"])
        def update_member(request: HttpRequest, member_id: int = Path(...), data: MemberUpdateSchema = ...):
            """更新成员信息"""
            try:
                user = get_current_user(request)
                
                member = self.service_class.update_member(
                    member_id, data.dict(exclude_unset=True), user
                )
                
                return create_success_response(
                    data=self.serialize_object(member, user),
                    message="成员信息更新成功",
                    request_id=get_request_id(request)
                )
                
            except (NotFoundError, ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Update member error: {e}")
                raise OperationError("更新成员信息失败")
        
        @self.router.delete("/{member_id}", response=SuccessResponseSchema, summary="删除成员", tags=["成员管理"])
        def delete_member(request: HttpRequest, member_id: int = Path(...)):
            """删除成员"""
            try:
                user = get_current_user(request)
                
                self.service_class.delete_member(member_id, user)
                
                return create_success_response(
                    message="成员删除成功",
                    request_id=get_request_id(request)
                )
                
            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Delete member error: {e}")
                raise OperationError("删除成员失败")
    
    def register_custom_routes(self) -> None:
        """注册自定义路由（批量操作、搜索等）"""
        
        @self.router.post("/batch", response=ApiResponseSchema, summary="批量创建成员", tags=["成员管理"])
        def batch_create_members(request: HttpRequest, data: MemberBatchCreateSchema):
            """批量创建家族成员"""
            try:
                user = get_current_user(request)
                
                result = self.service_class.batch_create_members(data.members, user)
                
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
                    request_id=get_request_id(request)
                )
                
            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Batch create members error: {e}")
                raise OperationError("批量创建成员失败")
        
        @self.router.delete("/batch", response=SuccessResponseSchema, summary="批量删除成员", tags=["成员管理"])
        def batch_delete_members(request: HttpRequest, member_ids: List[int]):
            """批量删除成员"""
            try:
                user = get_current_user(request)
                
                result = self.service_class.batch_delete_members(member_ids, user)
                
                return create_success_response(
                    data={
                        "deleted_count": result['deleted_count'],
                        "failed_count": result['failed_count'],
                        "errors": result['errors']
                    },
                    message=f"批量删除完成，成功{result['deleted_count']}个，失败{result['failed_count']}个",
                    request_id=get_request_id(request)
                )
                
            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Batch delete members error: {e}")
                raise OperationError("批量删除成员失败")
        
        @self.router.get("/search", response=PaginatedApiResponseSchema, summary="搜索成员", tags=["成员管理"])
        def search_members(request: HttpRequest, query: MemberQuerySchema = Query(...)):
            """搜索家族成员"""
            try:
                user = get_current_user(request)
                
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
                
                members, total = self.service_class.search_members(user, **filters)
                
                data = [self.serialize_object(m, user) for m in members]
                
                return create_paginated_response(
                    data=data,
                    total=total,
                    page=query.page,
                    page_size=query.page_size,
                    message=f"搜索到{total}个相关成员",
                    request_id=get_request_id(request)
                )
                
            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Search members error: {e}")
                raise OperationError("搜索成员失败")
        
        @self.router.get("/family/{family_id}/tree", response=ApiResponseSchema, summary="获取家族树", tags=["成员管理"])
        def get_family_tree(request: HttpRequest, family_id: int = Path(...)):
            """获取家族树结构"""
            try:
                user = get_current_user(request)
                
                tree_data = self.service_class.get_family_tree(family_id, user)
                
                return create_success_response(
                    data=tree_data,
                    message="获取家族树成功",
                    request_id=get_request_id(request)
                )
                
            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get family tree error: {e}")
                raise OperationError("获取家族树失败")

        @self.router.get("/family/{family_id}/flat", response=ApiResponseSchema, summary="获取成员扁平结构", tags=["成员管理"], auth=None)
        def get_family_members_flat(request: HttpRequest, family_id: int = Path(...)):
            try:
                member_qs = Member.objects.filter(family_id=family_id)
                rel_qs = Relationship.objects.filter(family_id=family_id)

                members = list(member_qs)
                parent_map = {}
                spouse_map = {}
                children_map = {}

                for m in members:
                    children_map[m.id] = []

                for rel in rel_qs:
                    if rel.relationship_type == "parent":
                        children_map.setdefault(rel.from_member_id, []).append(rel.to_member_id)
                        parent_map.setdefault(rel.to_member_id, [])
                        parent_map[rel.to_member_id].append(rel.from_member_id)
                    elif rel.relationship_type == "spouse":
                        spouse_map.setdefault(rel.from_member_id, [])
                        spouse_map.setdefault(rel.to_member_id, [])
                        spouse_map[rel.from_member_id].append(rel.to_member_id)
                        spouse_map[rel.to_member_id].append(rel.from_member_id)

                def pick_parent(member_id: int):
                    ids = parent_map.get(member_id) or []
                    if not ids:
                        return None
                    males = [pid for pid in ids if any(mm.id == pid and mm.gender == "male" for mm in members)]
                    return (males[0] if males else ids[0])

                def pick_spouse(member_id: int):
                    ids = spouse_map.get(member_id) or []
                    return ids[0] if ids else None

                data = []
                for m in members:
                    data.append({
                        "id": str(m.id),
                        "familyId": m.family_id,
                        "name": m.name,
                        "gender": "male" if m.gender == "male" else ("female" if m.gender == "female" else "male"),
                        "birthDate": m.birth_date.isoformat() if m.birth_date else None,
                        "deathDate": m.death_date.isoformat() if m.death_date else None,
                        "generation": m.generation,
                        "parentId": str(pick_parent(m.id)) if pick_parent(m.id) is not None else None,
                        "spouseId": str(pick_spouse(m.id)) if pick_spouse(m.id) is not None else None,
                        "children": [str(cid) for cid in (children_map.get(m.id) or [])]
                    })

                return create_success_response(
                    data=data,
                    message="获取成员扁平结构成功",
                    request_id=get_request_id(request)
                )
            except Exception as e:
                logger.exception(f"Get family members flat error: {e}")
                raise OperationError("获取成员扁平结构失败")


# 创建控制器实例
member_controller = MemberController()
router = member_controller.router


# ==================== 导出 ====================

__all__ = [
    "MemberController",
    "member_controller", 
    "router"
]
