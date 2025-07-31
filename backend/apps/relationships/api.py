"""
关系模块API接口定义

基于Django Ninja的API接口，提供家族关系管理相关的所有API服务。
遵循Django Ninja最佳实践和Google Python Style Guide。

设计原则：
- 标准化控制器模式：继承StandardCRUDController，统一API结构
- 路由注册分离：CRUD路由与自定义路由分别注册
- Schema驱动：使用Pydantic Schema进行数据验证和序列化
- 服务层分离：业务逻辑统一在Service层处理，API层只负责请求响应
- 统一异常处理：使用通用异常类型，提供一致的错误响应
- 权限控制：集成JWT认证，确保API安全性
- 响应标准化：使用统一的响应格式和状态码
- 日志记录：记录关键操作和错误信息
"""

# 导入模块
# ==================== 标准库导入 ====================
from typing import Optional, Dict, Any, List

# ==================== Django相关导入 ====================
from django.http import HttpRequest

# ==================== 第三方库导入 ====================
from ninja import Router, Query, Path
from loguru import logger

# ==================== 通用模块导入 ====================
from apps.common.api import StandardCRUDController
from apps.common.schemas import (
    ApiResponseSchema, PaginatedApiResponseSchema, SuccessResponseSchema
)
from apps.common.utils import (
    create_success_response, create_paginated_response, 
    get_request_id
)
from apps.common.authentication import get_current_user, JWTAuth
from apps.common.exceptions import (
    ValidationError, PermissionError, NotFoundError, OperationError
)

# ==================== 本地模块导入 ====================
from .schemas import (
    RelationshipCreateSchema, RelationshipUpdateSchema, RelationshipResponseSchema,
    RelationshipQuerySchema, RelationshipBatchCreateSchema
)
from .services import RelationshipService


class RelationshipController(StandardCRUDController):
    """
    关系API控制器
    
    提供完整的家族关系管理API接口，包括关系的增删改查、关系图谱等功能。
    继承自StandardCRUDController，遵循统一的API设计模式。
    
    主要功能：
    - 标准CRUD操作：创建、查询、更新、删除关系
    - 批量操作：批量创建和删除关系
    - 关系分析：获取成员关系、关系图谱、关系统计
    - 关系验证：验证关系的合理性和一致性
    """
    
    # 配置服务类和Schema
    service_class = RelationshipService
    list_query_schema = RelationshipQuerySchema
    create_schema = RelationshipCreateSchema
    update_schema = RelationshipUpdateSchema
    
    def __init__(self):
        """初始化控制器"""
        self.router = Router(auth=JWTAuth(), tags=["关系管理"])
        self.register_routes()
    
    def serialize_object(self, obj, user=None) -> Dict[str, Any]:
        """
        序列化关系对象
        
        Args:
            obj: 关系对象
            user: 当前用户（用于权限控制）
            
        Returns:
            Dict[str, Any]: 序列化后的数据
        """
        return {
            "id": obj.id,
            "family_id": obj.family_id,
            "from_member_id": obj.from_member_id,
            "to_member_id": obj.to_member_id,
            "relationship_type": obj.relationship_type,
            "start_date": obj.start_date.isoformat() if obj.start_date else None,
            "end_date": obj.end_date.isoformat() if obj.end_date else None,
            "description": obj.description,
            "is_confirmed": obj.is_confirmed,
            "created_by": obj.created_by_id,
            "created_at": obj.created_at.isoformat(),
            "updated_at": obj.updated_at.isoformat(),
            # 关联对象信息
            "from_member": {
                "id": obj.from_member.id,
                "name": obj.from_member.name,
                "gender": obj.from_member.gender,
                "avatar": obj.from_member.avatar
            } if hasattr(obj, 'from_member') and obj.from_member else None,
            "to_member": {
                "id": obj.to_member.id,
                "name": obj.to_member.name,
                "gender": obj.to_member.gender,
                "avatar": obj.to_member.avatar
            } if hasattr(obj, 'to_member') and obj.to_member else None
        }
    
    def register_routes(self) -> None:
        """注册所有路由"""
        self.register_crud_routes()
        self.register_custom_routes()
    
    def register_crud_routes(self) -> None:
        """注册标准CRUD路由"""
        
        @self.router.get("/", response=PaginatedApiResponseSchema, summary="获取关系列表", tags=["关系管理"])
        def list_relationships(request: HttpRequest, query: RelationshipQuerySchema = Query(...)):
            """获取家族关系列表"""
            try:
                user = get_current_user(request)
                
                filters = {
                    'family_id': query.family_id,
                    'member_id': query.member_id,
                    'relationship_type': query.relationship_type,
                    'is_confirmed': query.is_confirmed,
                    'ordering': query.ordering,
                    'page': query.page,
                    'page_size': query.page_size
                }
                
                relationships, total = self.service_class.list_relationships(user, **filters)
                
                data = [self.serialize_object(r, user) for r in relationships]
                
                return create_paginated_response(
                    data=data,
                    total=total,
                    page=query.page,
                    page_size=query.page_size,
                    message="获取关系列表成功",
                    request_id=get_request_id(request)
                )
                
            except (PermissionError, ValidationError) as e:
                raise e
            except Exception as e:
                logger.error(f"List relationships error: {e}")
                raise OperationError("获取关系列表失败")
        
        @self.router.post("/", response=ApiResponseSchema, summary="创建关系", tags=["关系管理"])
        def create_relationship(request: HttpRequest, data: RelationshipCreateSchema):
            """创建家族关系"""
            try:
                user = get_current_user(request)
                
                relationship = self.service_class.create_relationship(data.dict(), user)
                
                return create_success_response(
                    data=self.serialize_object(relationship, user),
                    message="关系创建成功",
                    request_id=get_request_id(request)
                )
                
            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Create relationship error: {e}")
                raise OperationError("创建关系失败")
        
        @self.router.get("/{relationship_id}", response=ApiResponseSchema, summary="获取关系详情", tags=["关系管理"])
        def get_relationship(request: HttpRequest, relationship_id: int = Path(...)):
            """获取关系详情"""
            try:
                user = get_current_user(request)
                
                relationship = self.service_class.get_relationship(relationship_id, user)
                
                return create_success_response(
                    data=self.serialize_object(relationship, user),
                    message="获取关系详情成功",
                    request_id=get_request_id(request)
                )
                
            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get relationship error: {e}")
                raise OperationError("获取关系详情失败")
        
        @self.router.put("/{relationship_id}", response=ApiResponseSchema, summary="更新关系信息", tags=["关系管理"])
        def update_relationship(request: HttpRequest, relationship_id: int = Path(...), data: RelationshipUpdateSchema = ...):
            """更新关系信息"""
            try:
                user = get_current_user(request)
                
                relationship = self.service_class.update_relationship(
                    relationship_id, data.dict(exclude_unset=True), user
                )
                
                return create_success_response(
                    data=self.serialize_object(relationship, user),
                    message="关系信息更新成功",
                    request_id=get_request_id(request)
                )
                
            except (NotFoundError, ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Update relationship error: {e}")
                raise OperationError("更新关系信息失败")
        
        @self.router.delete("/{relationship_id}", response=SuccessResponseSchema, summary="删除关系", tags=["关系管理"])
        def delete_relationship(request: HttpRequest, relationship_id: int = Path(...)):
            """删除关系"""
            try:
                user = get_current_user(request)
                
                self.service_class.delete_relationship(relationship_id, user)
                
                return create_success_response(
                    message="关系删除成功",
                    request_id=get_request_id(request)
                )
                
            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Delete relationship error: {e}")
                raise OperationError("删除关系失败")
    
    def register_custom_routes(self) -> None:
        """注册自定义路由"""
        
        @self.router.post("/batch", response=ApiResponseSchema, summary="批量创建关系", tags=["关系管理"])
        def batch_create_relationships(request: HttpRequest, data: RelationshipBatchCreateSchema):
            """批量创建家族关系"""
            try:
                user = get_current_user(request)
                
                result = self.service_class.batch_create_relationships(data.relationships, user)
                
                return create_success_response(
                    data={
                        "created_count": result['created_count'],
                        "failed_count": result['failed_count'],
                        "created_relationships": [
                            self.serialize_object(r, user) for r in result['created_relationships']
                        ],
                        "errors": result['errors']
                    },
                    message=f"批量创建完成，成功{result['created_count']}个，失败{result['failed_count']}个",
                    request_id=get_request_id(request)
                )
                
            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Batch create relationships error: {e}")
                raise OperationError("批量创建关系失败")
        
        @self.router.delete("/batch", response=SuccessResponseSchema, summary="批量删除关系", tags=["关系管理"])
        def batch_delete_relationships(request: HttpRequest, relationship_ids: List[int]):
            """批量删除关系"""
            try:
                user = get_current_user(request)
                
                result = self.service_class.batch_delete_relationships(relationship_ids, user)
                
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
                logger.error(f"Batch delete relationships error: {e}")
                raise OperationError("批量删除关系失败")
        
        @self.router.get("/member/{member_id}/relationships", response=ApiResponseSchema, summary="获取成员关系", tags=["关系管理"])
        def get_member_relationships(request: HttpRequest, member_id: int = Path(...)):
            """获取指定成员的所有关系"""
            try:
                user = get_current_user(request)
                
                relationships = self.service_class.get_member_relationships(member_id, user)
                
                data = [self.serialize_object(r, user) for r in relationships]
                
                return create_success_response(
                    data=data,
                    message="获取成员关系成功",
                    request_id=get_request_id(request)
                )
                
            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get member relationships error: {e}")
                raise OperationError("获取成员关系失败")
        
        @self.router.get("/family/{family_id}/graph", response=ApiResponseSchema, summary="获取关系图谱", tags=["关系管理"])
        def get_relationship_graph(request: HttpRequest, family_id: int = Path(...)):
            """获取家族关系图谱"""
            try:
                user = get_current_user(request)
                
                graph_data = self.service_class.get_relationship_graph(family_id, user)
                
                return create_success_response(
                    data=graph_data,
                    message="获取关系图谱成功",
                    request_id=get_request_id(request)
                )
                
            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get relationship graph error: {e}")
                raise OperationError("获取关系图谱失败")
        
        @self.router.get("/family/{family_id}/statistics", response=ApiResponseSchema, summary="获取关系统计", tags=["关系管理"])
        def get_relationship_statistics(request: HttpRequest, family_id: int = Path(...)):
            """获取家族关系统计信息"""
            try:
                user = get_current_user(request)
                
                stats = self.service_class.get_relationship_statistics(family_id, user)
                
                return create_success_response(
                    data=stats,
                    message="获取关系统计成功",
                    request_id=get_request_id(request)
                )
                
            except (NotFoundError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Get relationship statistics error: {e}")
                raise OperationError("获取关系统计失败")
        
        @self.router.post("/validate", response=ApiResponseSchema, summary="验证关系", tags=["关系管理"])
        def validate_relationship(request: HttpRequest, data: RelationshipCreateSchema):
            """验证关系的合理性"""
            try:
                user = get_current_user(request)
                
                validation_result = self.service_class.validate_relationship(data.dict(), user)
                
                return create_success_response(
                    data=validation_result,
                    message="关系验证完成",
                    request_id=get_request_id(request)
                )
                
            except (ValidationError, PermissionError) as e:
                raise e
            except Exception as e:
                logger.error(f"Validate relationship error: {e}")
                raise OperationError("关系验证失败")


# 实例化控制器
relationship_controller = RelationshipController()
router = relationship_controller.router

# 导出
__all__ = [
    "RelationshipController",
    "relationship_controller",
    "router"
]