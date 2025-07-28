"""
成员模块服务层

提供家族成员管理相关的业务逻辑处理。
遵循Django最佳实践和Google Python Style Guide。
"""

from typing import Dict, Any, List, Optional, Tuple
from django.db import transaction
from django.db.models import Q, QuerySet
from django.contrib.auth import get_user_model
from loguru import logger

from apps.common.services import BaseService, CacheableService
from apps.common.exceptions import (
    ValidationError, PermissionError, NotFoundError, OperationError
)
from .models import Member
from apps.family.models import Family

User = get_user_model()


class MemberService(BaseService, CacheableService):
    """
    成员服务类
    
    提供家族成员管理相关的所有业务逻辑，包括成员的增删改查、关系管理等。
    """
    
    model = Member
    
    def get_search_fields(self) -> List[str]:
        """定义可搜索的字段"""
        return ['name', 'english_name', 'nickname', 'occupation', 'birth_place', 'current_location']
    
    def validate_create_data(self, data: Dict[str, Any], user=None) -> Dict[str, Any]:
        """验证成员创建数据"""
        # 检查家族权限
        family_id = data.get('family_id')
        if family_id:
            try:
                family = Family.objects.get(id=family_id)
                if not family.can_user_manage(user):
                    raise PermissionError("无权限在此家族中创建成员")
            except Family.DoesNotExist:
                raise NotFoundError("家族不存在")
        
        # 验证出生和死亡日期
        birth_date = data.get('birth_date')
        death_date = data.get('death_date')
        if birth_date and death_date and birth_date >= death_date:
            raise ValidationError("出生日期不能晚于或等于死亡日期")
        
        # 如果有死亡日期，则设置为已故
        if death_date:
            data['is_alive'] = False
        
        return data
    
    def validate_update_data(self, obj, data: Dict[str, Any], user=None) -> Dict[str, Any]:
        """验证成员更新数据"""
        # 检查权限
        if not obj.family.can_user_manage(user):
            raise PermissionError("无权限修改此成员信息")
        
        # 验证出生和死亡日期
        birth_date = data.get('birth_date', obj.birth_date)
        death_date = data.get('death_date', obj.death_date)
        if birth_date and death_date and birth_date >= death_date:
            raise ValidationError("出生日期不能晚于或等于死亡日期")
        
        # 如果有死亡日期，则设置为已故
        if death_date:
            data['is_alive'] = False
        elif 'death_date' in data and data['death_date'] is None:
            data['is_alive'] = True
        
        return data
    
    def check_permissions(self, obj, user, action: str) -> bool:
        """检查成员权限"""
        if action == 'view':
            # 根据隐私级别检查查看权限
            return obj.can_user_view(user)
        elif action in ['update', 'delete']:
            # 检查管理权限
            return obj.family.can_user_manage(user)
        return False
    
    @transaction.atomic
    def create_member(self, data: Dict[str, Any], user: User) -> Member:
        """创建成员"""
        try:
            # 验证数据
            validated_data = self.validate_create_data(data, user)
            
            # 设置创建者
            validated_data['created_by'] = user
            
            # 创建成员
            member = Member.objects.create(**validated_data)
            
            logger.info(f"Member created: {member.name} by {user.username}")
            return member
            
        except (ValidationError, PermissionError, NotFoundError) as e:
            raise e
        except Exception as e:
            logger.error(f"Create member error: {e}")
            raise OperationError("创建成员失败")
    
    def list_members(self, user: User, family_id: int = None, keyword: str = None,
                     gender: str = None, generation: int = None, is_alive: bool = None,
                     ordering: str = None, page: int = 1, page_size: int = 20) -> Tuple[List[Member], int]:
        """获取成员列表"""
        try:
            queryset = self.get_queryset(user)
            
            # 家族过滤
            if family_id:
                family = Family.objects.get(id=family_id)
                if not family.can_user_view(user):
                    raise PermissionError("无权限查看此家族成员")
                queryset = queryset.filter(family_id=family_id)
            else:
                # 只显示用户有权限查看的家族成员
                accessible_families = Family.objects.filter(
                    Q(created_by=user) | Q(members__user=user) | Q(visibility='public')
                ).distinct()
                queryset = queryset.filter(family__in=accessible_families)
            
            # 搜索过滤
            if keyword:
                search_q = Q()
                for field in self.get_search_fields():
                    search_q |= Q(**{f"{field}__icontains": keyword})
                queryset = queryset.filter(search_q)
            
            # 其他过滤条件
            if gender:
                queryset = queryset.filter(gender=gender)
            
            if generation is not None:
                queryset = queryset.filter(generation=generation)
            
            if is_alive is not None:
                queryset = queryset.filter(is_alive=is_alive)
            
            # 排序
            if ordering:
                queryset = queryset.order_by(ordering)
            else:
                queryset = queryset.order_by('generation', 'sort_order', 'name')
            
            # 分页
            total = queryset.count()
            start = (page - 1) * page_size
            end = start + page_size
            members = list(queryset.select_related('family', 'created_by')[start:end])
            
            return members, total
            
        except (PermissionError, NotFoundError) as e:
            raise e
        except Exception as e:
            logger.error(f"List members error: {e}")
            raise OperationError("获取成员列表失败")
    
    def search_members(self, user: User, **filters) -> Tuple[List[Member], int]:
        """搜索成员"""
        return self.list_members(user, **filters)
    
    def batch_create_members(self, members_data: List[Dict[str, Any]], user: User) -> Dict[str, Any]:
        """批量创建成员"""
        created_members = []
        errors = []
        
        for i, data in enumerate(members_data):
            try:
                member = self.create_member(data, user)
                created_members.append(member)
            except Exception as e:
                errors.append({
                    'index': i,
                    'data': data,
                    'error': str(e)
                })
        
        return {
            'created_count': len(created_members),
            'failed_count': len(errors),
            'created_members': created_members,
            'errors': errors
        }
    
    def batch_delete_members(self, member_ids: List[int], user: User) -> Dict[str, Any]:
        """批量删除成员"""
        deleted_count = 0
        errors = []
        
        for member_id in member_ids:
            try:
                member = Member.objects.get(id=member_id)
                if self.check_permissions(member, user, 'delete'):
                    member.delete()
                    deleted_count += 1
                else:
                    errors.append({
                        'member_id': member_id,
                        'error': '无权限删除此成员'
                    })
            except Member.DoesNotExist:
                errors.append({
                    'member_id': member_id,
                    'error': '成员不存在'
                })
            except Exception as e:
                errors.append({
                    'member_id': member_id,
                    'error': str(e)
                })
        
        return {
            'deleted_count': deleted_count,
            'failed_count': len(errors),
            'errors': errors
        }
    
    def get_family_tree(self, family_id: int, user: User) -> Dict[str, Any]:
        """获取家族树结构"""
        try:
            family = Family.objects.get(id=family_id)
            if not family.can_user_view(user):
                raise PermissionError("无权限查看此家族树")
            
            # 获取所有成员
            members = Member.objects.filter(family_id=family_id).order_by('generation', 'sort_order')
            
            # 构建树形结构
            tree_data = {
                'family': {
                    'id': family.id,
                    'name': family.name,
                    'description': family.description
                },
                'members': [],
                'generations': {}
            }
            
            for member in members:
                member_data = {
                    'id': member.id,
                    'name': member.name,
                    'gender': member.gender,
                    'birth_date': member.birth_date.isoformat() if member.birth_date else None,
                    'death_date': member.death_date.isoformat() if member.death_date else None,
                    'is_alive': member.is_alive,
                    'generation': member.generation,
                    'avatar': member.avatar
                }
                
                tree_data['members'].append(member_data)
                
                # 按世代分组
                if member.generation not in tree_data['generations']:
                    tree_data['generations'][member.generation] = []
                tree_data['generations'][member.generation].append(member_data)
            
            return tree_data
            
        except (Family.DoesNotExist, PermissionError) as e:
            raise e
        except Exception as e:
            logger.error(f"Get family tree error: {e}")
            raise OperationError("获取家族树失败")


# ==================== 导出 ====================

__all__ = [
    'MemberService'
]