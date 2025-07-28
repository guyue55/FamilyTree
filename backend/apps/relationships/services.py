"""
关系模块服务层

提供家族关系管理相关的业务逻辑处理。
遵循Django最佳实践和Google Python Style Guide。
"""

from typing import Dict, Any, List, Optional, Tuple
from django.db import transaction
from django.db.models import Q, QuerySet, Count
from django.contrib.auth import get_user_model
from loguru import logger

from apps.common.services import BaseService, CacheableService
from apps.common.exceptions import (
    ValidationError, PermissionError, NotFoundError, OperationError
)
from .models import Relationship
from apps.members.models import Member
from apps.family.models import Family

User = get_user_model()


class RelationshipService(BaseService, CacheableService):
    """
    关系服务类
    
    提供家族关系管理相关的所有业务逻辑，包括关系的增删改查、关系图谱生成等。
    """
    
    model = Relationship
    
    # 关系类型映射
    RELATIONSHIP_TYPES = {
        'parent': '父母',
        'child': '子女',
        'spouse': '配偶',
        'sibling': '兄弟姐妹',
        'grandparent': '祖父母',
        'grandchild': '孙子女',
        'uncle_aunt': '叔伯姑姨',
        'nephew_niece': '侄子侄女',
        'cousin': '堂兄弟姐妹',
        'other': '其他'
    }
    
    @classmethod
    def get_search_fields(cls) -> List[str]:
        """获取搜索字段列表"""
        return ['relationship_type', 'notes', 'from_member__name', 'to_member__name']
    
    def validate_create_data(self, data: Dict[str, Any], user=None) -> Dict[str, Any]:
        """验证关系创建数据"""
        from_member_id = data.get('from_member_id')
        to_member_id = data.get('to_member_id')
        relationship_type = data.get('relationship_type')
        
        # 检查成员是否存在
        try:
            from_member = Member.objects.get(id=from_member_id)
            to_member = Member.objects.get(id=to_member_id)
        except Member.DoesNotExist:
            raise NotFoundError("成员不存在")
        
        # 检查权限
        if not from_member.family.can_user_manage(user) or not to_member.family.can_user_manage(user):
            raise PermissionError("无权限创建此关系")
        
        # 检查是否为同一人
        if from_member_id == to_member_id:
            raise ValidationError("不能为同一人创建关系")
        
        # 检查关系类型
        if relationship_type not in self.RELATIONSHIP_TYPES:
            raise ValidationError("无效的关系类型")
        
        # 检查是否已存在相同关系
        existing = Relationship.objects.filter(
            from_member_id=from_member_id,
            to_member_id=to_member_id,
            relationship_type=relationship_type
        ).exists()
        
        if existing:
            raise ValidationError("此关系已存在")
        
        return data
    
    def validate_update_data(self, obj, data: Dict[str, Any], user=None) -> Dict[str, Any]:
        """验证关系更新数据"""
        # 检查权限
        if not obj.from_member.family.can_user_manage(user):
            raise PermissionError("无权限修改此关系")
        
        # 如果修改了关系类型，需要验证
        if 'relationship_type' in data:
            relationship_type = data['relationship_type']
            if relationship_type not in self.RELATIONSHIP_TYPES:
                raise ValidationError("无效的关系类型")
        
        return data
    
    def check_permissions(self, obj, user, action: str) -> bool:
        """检查关系权限"""
        if action == 'view':
            return (obj.from_member.can_user_view(user) and 
                   obj.to_member.can_user_view(user))
        elif action in ['update', 'delete']:
            return obj.from_member.family.can_user_manage(user)
        return False
    
    @transaction.atomic
    def create_relationship(self, data: Dict[str, Any], user: User) -> Relationship:
        """创建关系"""
        try:
            # 验证数据
            validated_data = self.validate_create_data(data, user)
            
            # 设置创建者
            validated_data['created_by'] = user
            
            # 创建关系
            relationship = Relationship.objects.create(**validated_data)
            
            # 根据关系类型自动创建反向关系
            self._create_reverse_relationship(relationship, user)
            
            logger.info(f"Relationship created: {relationship.from_member.name} -> {relationship.to_member.name} ({relationship.relationship_type}) by {user.username}")
            return relationship
            
        except (ValidationError, PermissionError, NotFoundError) as e:
            raise e
        except Exception as e:
            logger.error(f"Create relationship error: {e}")
            raise OperationError("创建关系失败")
    
    def _create_reverse_relationship(self, relationship: Relationship, user: User):
        """创建反向关系"""
        reverse_type_map = {
            'parent': 'child',
            'child': 'parent',
            'spouse': 'spouse',
            'sibling': 'sibling',
            'grandparent': 'grandchild',
            'grandchild': 'grandparent',
            'uncle_aunt': 'nephew_niece',
            'nephew_niece': 'uncle_aunt',
            'cousin': 'cousin'
        }
        
        reverse_type = reverse_type_map.get(relationship.relationship_type)
        if reverse_type:
            # 检查反向关系是否已存在
            existing = Relationship.objects.filter(
                from_member=relationship.to_member,
                to_member=relationship.from_member,
                relationship_type=reverse_type
            ).exists()
            
            if not existing:
                Relationship.objects.create(
                    from_member=relationship.to_member,
                    to_member=relationship.from_member,
                    relationship_type=reverse_type,
                    created_by=user
                )
    
    def list_relationships(self, user: User, family_id: int = None, member_id: int = None,
                          relationship_type: str = None, ordering: str = None,
                          page: int = 1, page_size: int = 20) -> Tuple[List[Relationship], int]:
        """获取关系列表"""
        try:
            queryset = self.get_queryset(user)
            
            # 家族过滤
            if family_id:
                family = Family.objects.get(id=family_id)
                if not family.can_user_view(user):
                    raise PermissionError("无权限查看此家族关系")
                queryset = queryset.filter(from_member__family_id=family_id)
            else:
                # 只显示用户有权限查看的家族关系
                accessible_families = Family.objects.filter(
                    Q(created_by=user) | Q(members__user=user) | Q(visibility='public')
                ).distinct()
                queryset = queryset.filter(from_member__family__in=accessible_families)
            
            # 成员过滤
            if member_id:
                queryset = queryset.filter(
                    Q(from_member_id=member_id) | Q(to_member_id=member_id)
                )
            
            # 关系类型过滤
            if relationship_type:
                queryset = queryset.filter(relationship_type=relationship_type)
            
            # 排序
            if ordering:
                queryset = queryset.order_by(ordering)
            else:
                queryset = queryset.order_by('from_member__generation', 'created_at')
            
            # 分页
            total = queryset.count()
            start = (page - 1) * page_size
            end = start + page_size
            relationships = list(queryset.select_related(
                'from_member', 'to_member', 'created_by'
            )[start:end])
            
            return relationships, total
            
        except (PermissionError, NotFoundError) as e:
            raise e
        except Exception as e:
            logger.error(f"List relationships error: {e}")
            raise OperationError("获取关系列表失败")
    
    def get_member_relationships(self, member_id: int, user: User) -> Dict[str, Any]:
        """获取成员的所有关系"""
        try:
            member = Member.objects.get(id=member_id)
            if not member.can_user_view(user):
                raise PermissionError("无权限查看此成员关系")
            
            # 获取所有相关关系
            outgoing = Relationship.objects.filter(from_member=member).select_related('to_member')
            incoming = Relationship.objects.filter(to_member=member).select_related('from_member')
            
            relationships = {
                'member': {
                    'id': member.id,
                    'name': member.name,
                    'gender': member.gender
                },
                'outgoing': [],
                'incoming': [],
                'by_type': {}
            }
            
            # 处理出向关系
            for rel in outgoing:
                rel_data = {
                    'id': rel.id,
                    'to_member': {
                        'id': rel.to_member.id,
                        'name': rel.to_member.name,
                        'gender': rel.to_member.gender
                    },
                    'relationship_type': rel.relationship_type,
                    'relationship_name': self.RELATIONSHIP_TYPES.get(rel.relationship_type, rel.relationship_type)
                }
                relationships['outgoing'].append(rel_data)
                
                # 按类型分组
                if rel.relationship_type not in relationships['by_type']:
                    relationships['by_type'][rel.relationship_type] = []
                relationships['by_type'][rel.relationship_type].append(rel_data)
            
            # 处理入向关系
            for rel in incoming:
                rel_data = {
                    'id': rel.id,
                    'from_member': {
                        'id': rel.from_member.id,
                        'name': rel.from_member.name,
                        'gender': rel.from_member.gender
                    },
                    'relationship_type': rel.relationship_type,
                    'relationship_name': self.RELATIONSHIP_TYPES.get(rel.relationship_type, rel.relationship_type)
                }
                relationships['incoming'].append(rel_data)
            
            return relationships
            
        except (Member.DoesNotExist, PermissionError) as e:
            raise e
        except Exception as e:
            logger.error(f"Get member relationships error: {e}")
            raise OperationError("获取成员关系失败")
    
    def get_family_graph(self, family_id: int, user: User) -> Dict[str, Any]:
        """获取家族关系图谱"""
        try:
            family = Family.objects.get(id=family_id)
            if not family.can_user_view(user):
                raise PermissionError("无权限查看此家族关系图谱")
            
            # 获取所有成员和关系
            members = Member.objects.filter(family_id=family_id)
            relationships = Relationship.objects.filter(
                from_member__family_id=family_id
            ).select_related('from_member', 'to_member')
            
            # 构建图谱数据
            graph_data = {
                'family': {
                    'id': family.id,
                    'name': family.name
                },
                'nodes': [],
                'edges': [],
                'statistics': {
                    'total_members': members.count(),
                    'total_relationships': relationships.count(),
                    'generations': members.values('generation').distinct().count()
                }
            }
            
            # 添加节点（成员）
            for member in members:
                node = {
                    'id': member.id,
                    'name': member.name,
                    'gender': member.gender,
                    'generation': member.generation,
                    'birth_date': member.birth_date.isoformat() if member.birth_date else None,
                    'is_alive': member.is_alive,
                    'avatar': member.avatar
                }
                graph_data['nodes'].append(node)
            
            # 添加边（关系）
            for relationship in relationships:
                edge = {
                    'id': relationship.id,
                    'from': relationship.from_member.id,
                    'to': relationship.to_member.id,
                    'type': relationship.relationship_type,
                    'label': self.RELATIONSHIP_TYPES.get(relationship.relationship_type, relationship.relationship_type)
                }
                graph_data['edges'].append(edge)
            
            return graph_data
            
        except (Family.DoesNotExist, PermissionError) as e:
            raise e
        except Exception as e:
            logger.error(f"Get family graph error: {e}")
            raise OperationError("获取家族关系图谱失败")
    
    def get_relationship_statistics(self, family_id: int, user: User) -> Dict[str, Any]:
        """获取关系统计信息"""
        try:
            family = Family.objects.get(id=family_id)
            if not family.can_user_view(user):
                raise PermissionError("无权限查看此家族统计")
            
            # 统计各种关系类型的数量
            relationship_stats = {}
            for rel_type, rel_name in self.RELATIONSHIP_TYPES.items():
                count = Relationship.objects.filter(
                    from_member__family_id=family_id,
                    relationship_type=rel_type
                ).count()
                relationship_stats[rel_type] = {
                    'name': rel_name,
                    'count': count
                }
            
            # 统计世代信息
            generation_stats = Member.objects.filter(
                family_id=family_id
            ).values('generation').annotate(
                count=Count('id')
            ).order_by('generation')
            
            # 统计性别分布
            gender_stats = Member.objects.filter(
                family_id=family_id
            ).values('gender').annotate(
                count=Count('id')
            )
            
            return {
                'family_id': family_id,
                'relationship_types': relationship_stats,
                'generations': list(generation_stats),
                'gender_distribution': list(gender_stats),
                'total_members': Member.objects.filter(family_id=family_id).count(),
                'total_relationships': Relationship.objects.filter(from_member__family_id=family_id).count()
            }
            
        except (Family.DoesNotExist, PermissionError) as e:
            raise e
        except Exception as e:
            logger.error(f"Get relationship statistics error: {e}")
            raise OperationError("获取关系统计失败")
    
    def validate_relationship(self, from_member_id: int, to_member_id: int, 
                            relationship_type: str, user: User) -> Dict[str, Any]:
        """验证关系的合理性"""
        try:
            from_member = Member.objects.get(id=from_member_id)
            to_member = Member.objects.get(id=to_member_id)
            
            if not from_member.can_user_view(user) or not to_member.can_user_view(user):
                raise PermissionError("无权限验证此关系")
            
            validation_result = {
                'is_valid': True,
                'warnings': [],
                'errors': []
            }
            
            # 检查年龄逻辑
            if from_member.birth_date and to_member.birth_date:
                age_diff = (from_member.birth_date - to_member.birth_date).days / 365.25
                
                if relationship_type == 'parent' and age_diff < 15:
                    validation_result['warnings'].append("父母与子女年龄差异过小")
                elif relationship_type == 'child' and age_diff > -15:
                    validation_result['warnings'].append("子女与父母年龄差异过小")
                elif relationship_type == 'spouse' and abs(age_diff) > 20:
                    validation_result['warnings'].append("配偶年龄差异较大")
            
            # 检查世代逻辑
            if relationship_type == 'parent' and from_member.generation <= to_member.generation:
                validation_result['warnings'].append("父母世代应该高于子女世代")
            elif relationship_type == 'child' and from_member.generation >= to_member.generation:
                validation_result['warnings'].append("子女世代应该低于父母世代")
            elif relationship_type == 'sibling' and from_member.generation != to_member.generation:
                validation_result['warnings'].append("兄弟姐妹应该在同一世代")
            
            # 检查性别逻辑（如果需要）
            # 这里可以添加更多的性别相关验证
            
            return validation_result
            
        except (Member.DoesNotExist, PermissionError) as e:
            raise e
        except Exception as e:
            logger.error(f"Validate relationship error: {e}")
            raise OperationError("验证关系失败")
    
    def batch_create_relationships(self, relationships_data: List[Dict[str, Any]], user: User) -> Dict[str, Any]:
        """批量创建关系"""
        created_relationships = []
        errors = []
        
        for i, data in enumerate(relationships_data):
            try:
                relationship = self.create_relationship(data, user)
                created_relationships.append(relationship)
            except Exception as e:
                errors.append({
                    'index': i,
                    'data': data,
                    'error': str(e)
                })
        
        return {
            'created_count': len(created_relationships),
            'failed_count': len(errors),
            'created_relationships': created_relationships,
            'errors': errors
        }
    
    def batch_delete_relationships(self, relationship_ids: List[int], user: User) -> Dict[str, Any]:
        """批量删除关系"""
        deleted_count = 0
        errors = []
        
        for relationship_id in relationship_ids:
            try:
                relationship = Relationship.objects.get(id=relationship_id)
                if self.check_permissions(relationship, user, 'delete'):
                    relationship.delete()
                    deleted_count += 1
                else:
                    errors.append({
                        'relationship_id': relationship_id,
                        'error': '无权限删除此关系'
                    })
            except Relationship.DoesNotExist:
                errors.append({
                    'relationship_id': relationship_id,
                    'error': '关系不存在'
                })
            except Exception as e:
                errors.append({
                    'relationship_id': relationship_id,
                    'error': str(e)
                })
        
        return {
            'deleted_count': deleted_count,
            'failed_count': len(errors),
            'errors': errors
        }


# ==================== 导出 ====================

__all__ = [
    'RelationshipService'
]