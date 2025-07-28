# Django Ninja 后端框架快速开始指南

## 概述

本指南将帮助您快速上手我们标准化的Django Ninja后端框架。该框架提供了统一的API开发模式，包括服务层、控制器层、权限管理、分页查询等功能。

## 快速开始

### 1. 创建新模块

假设我们要创建一个"成员"(Member)模块：

#### 1.1 定义模型 (`apps/member/models.py`)

```python
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Member(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'members'
```

#### 1.2 创建服务类 (`apps/member/services.py`)

```python
from typing import List, Dict, Any
from apps.common.services import BaseService, CacheableService
from .models import Member

class MemberService(BaseService, CacheableService):
    """成员服务类"""
    model = Member
    
    def get_search_fields(self) -> List[str]:
        """定义可搜索的字段"""
        return ['name', 'email']
    
    def validate_create_data(self, data: Dict[str, Any], user) -> Dict[str, Any]:
        """验证创建数据"""
        # 检查邮箱是否已存在
        if Member.objects.filter(email=data.get('email')).exists():
            from apps.common.exceptions import ValidationError
            raise ValidationError("邮箱已存在")
        return data
    
    def validate_update_data(self, data: Dict[str, Any], obj: Member, user) -> Dict[str, Any]:
        """验证更新数据"""
        # 检查邮箱是否被其他成员使用
        email = data.get('email')
        if email and Member.objects.filter(email=email).exclude(id=obj.id).exists():
            from apps.common.exceptions import ValidationError
            raise ValidationError("邮箱已被其他成员使用")
        return data
    
    def post_create(self, obj: Member, data: Dict[str, Any], user) -> None:
        """创建后的钩子函数"""
        # 发送欢迎邮件等操作
        pass
```

#### 1.3 定义Schema (`apps/member/schemas.py`)

```python
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class MemberCreateSchema(BaseModel):
    """成员创建Schema"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...)
    phone: Optional[str] = Field(None, max_length=20)

class MemberUpdateSchema(BaseModel):
    """成员更新Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None, max_length=20)

class MemberQuerySchema(BaseModel):
    """成员查询Schema"""
    search: Optional[str] = Field(None, description="搜索关键词")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页大小")
```

#### 1.4 创建API控制器 (`apps/member/api.py`)

```python
from typing import Dict, Any, Optional
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from ninja import Query

from apps.common.api import StandardCRUDController, require_auth
from apps.common.schemas import SuccessResponseSchema, PaginatedApiResponseSchema
from .services import MemberService
from .schemas import MemberCreateSchema, MemberUpdateSchema, MemberQuerySchema
from .models import Member

User = get_user_model()

class MemberController(StandardCRUDController[MemberService]):
    """成员API控制器"""
    
    service_class = MemberService
    list_query_schema = MemberQuerySchema
    create_schema = MemberCreateSchema
    update_schema = MemberUpdateSchema
    
    def serialize_object(self, obj: Member, user: Optional[User] = None) -> Dict[str, Any]:
        """序列化成员对象"""
        return {
            'id': obj.id,
            'name': obj.name,
            'email': obj.email,
            'phone': obj.phone,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
            'is_active': obj.is_active
        }

# 创建控制器实例和路由
member_controller = MemberController()
router = member_controller.router

# 自定义路由示例
@router.get("/search", response=PaginatedApiResponseSchema, summary="高级搜索成员")
@require_auth
def advanced_search(request: HttpRequest, query: MemberQuerySchema = Query(...)):
    """高级搜索成员"""
    return member_controller.handle_list(request, query)
```

#### 1.5 注册路由 (`apps/member/urls.py`)

```python
from ninja import Router
from .api import router as member_router

# 创建应用路由
app_router = Router()
app_router.add_router("/members", member_router, tags=["成员管理"])
```

### 2. 权限管理

#### 2.1 定义权限 (`apps/member/permissions.py`)

```python
from enum import Enum
from typing import Optional, Set
from django.contrib.auth import get_user_model
from apps.common.exceptions import PermissionError

User = get_user_model()

class MemberPermission(Enum):
    """成员权限枚举"""
    VIEW_MEMBER = "view_member"
    CREATE_MEMBER = "create_member"
    EDIT_MEMBER = "edit_member"
    DELETE_MEMBER = "delete_member"

class MemberPermissionChecker:
    """成员权限检查器"""
    
    def __init__(self, user: Optional[User]):
        self.user = user
    
    def has_permission(self, permission: MemberPermission) -> bool:
        """检查权限"""
        if not self.user or not self.user.is_authenticated:
            return False
        
        # 这里实现具体的权限逻辑
        # 例如：检查用户角色、组织关系等
        return True
    
    def require_permission(self, permission: MemberPermission) -> None:
        """要求权限，无权限时抛出异常"""
        if not self.has_permission(permission):
            raise PermissionError(f"需要权限: {permission.value}")
```

#### 2.2 在API中使用权限

```python
from .permissions import MemberPermissionChecker, MemberPermission

@router.post("/", response=SuccessResponseSchema)
@require_auth
def create_member(request: HttpRequest, data: MemberCreateSchema):
    """创建成员"""
    # 检查权限
    checker = MemberPermissionChecker(request.user)
    checker.require_permission(MemberPermission.CREATE_MEMBER)
    
    # 调用控制器方法
    return member_controller.handle_create(request, data.dict())
```

### 3. 高级功能

#### 3.1 自定义分页查询

```python
from apps.common.pagination import search_and_paginate, FilterConfig, OrderConfig

def custom_member_search(request: HttpRequest):
    """自定义成员搜索"""
    queryset = Member.objects.filter(is_active=True)
    
    # 构建过滤条件
    filters = []
    if request.GET.get('email_domain'):
        filters.append(FilterConfig(
            field='email',
            operator='endswith',
            value=f"@{request.GET.get('email_domain')}"
        ))
    
    # 构建排序条件
    orders = [OrderConfig(field='created_at', direction='desc')]
    
    # 执行搜索和分页
    result = search_and_paginate(
        queryset=queryset,
        search_query=request.GET.get('search'),
        search_fields=['name', 'email'],
        filters=filters,
        orders=orders,
        page=int(request.GET.get('page', 1)),
        page_size=int(request.GET.get('page_size', 20)),
        serializer=lambda obj: {
            'id': obj.id,
            'name': obj.name,
            'email': obj.email
        }
    )
    
    from apps.common.utils import get_request_id
    return result.to_api_response(request_id=get_request_id(request))
```

#### 3.2 缓存使用

```python
class MemberService(BaseService, CacheableService):
    """带缓存的成员服务"""
    
    def get_member_by_email(self, email: str) -> Optional[Member]:
        """根据邮箱获取成员（带缓存）"""
        cache_key = f"member:email:{email}"
        
        # 尝试从缓存获取
        cached_data = self.get_cache(cache_key)
        if cached_data:
            return Member.objects.get(id=cached_data['id'])
        
        # 从数据库查询
        try:
            member = Member.objects.get(email=email, is_active=True)
            # 缓存结果
            self.set_cache(cache_key, {'id': member.id}, timeout=3600)
            return member
        except Member.DoesNotExist:
            return None
```

#### 3.3 异常处理

```python
from apps.common.exceptions import ValidationError, NotFoundError, PermissionError

class MemberService(BaseService):
    
    def delete_member(self, member_id: int, user) -> None:
        """删除成员"""
        member = self.get_by_id(member_id, user)
        
        # 业务逻辑检查
        if member.email == 'admin@example.com':
            raise ValidationError("不能删除管理员账户")
        
        # 软删除
        member.is_active = False
        member.save()
        
        # 清除相关缓存
        self.clear_cache_pattern(f"member:*")
```

## 最佳实践

### 1. 服务层设计
- 继承`BaseService`获得标准CRUD功能
- 使用`CacheableService`混入添加缓存功能
- 重写验证方法实现业务逻辑检查
- 使用钩子函数处理副作用操作

### 2. API设计
- 继承`StandardCRUDController`获得标准API接口
- 实现`serialize_object`方法定义数据序列化
- 使用装饰器添加认证和权限检查
- 保持API接口的一致性

### 3. 权限控制
- 定义清晰的权限枚举
- 实现权限检查器类
- 在API入口处进行权限验证
- 使用装饰器简化权限检查

### 4. 错误处理
- 使用统一的异常类
- 在服务层抛出业务异常
- 让框架自动处理异常响应
- 提供清晰的错误信息

### 5. 性能优化
- 合理使用缓存
- 优化数据库查询
- 实现分页查询
- 监控API性能

## 常见问题

### Q: 如何添加自定义验证？
A: 在服务类中重写`validate_create_data`或`validate_update_data`方法。

### Q: 如何实现复杂的权限控制？
A: 创建自定义权限检查器，实现具体的权限逻辑。

### Q: 如何处理文件上传？
A: 使用`validate_file_upload`工具函数验证文件，在服务层处理文件存储。

### Q: 如何实现软删除？
A: 在模型中添加`is_active`字段，在服务层重写`delete`方法。

### Q: 如何添加API文档？
A: 使用Ninja的自动文档生成功能，在路由装饰器中添加`summary`和`description`。

## 总结

通过遵循本指南，您可以快速创建符合框架标准的API模块。框架提供了丰富的功能和工具，帮助您专注于业务逻辑的实现，而不需要重复编写基础代码。

记住始终遵循框架的设计原则：
- 统一的响应格式
- 标准化的错误处理
- 清晰的权限控制
- 高效的分页查询
- 良好的代码组织

这样可以确保代码的一致性、可维护性和可扩展性。