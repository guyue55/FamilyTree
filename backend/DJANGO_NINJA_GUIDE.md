# Django Ninja API框架标准化指南

## 概述

本项目已完成从传统Django Views到Django Ninja API框架的迁移，实现了统一的API接口设计和异常处理机制。

## 架构特点

### 1. 统一的异常处理系统

项目在 `apps/common/handlers.py` 中定义了完整的异常处理器，所有API模块都使用统一的异常处理：

- **ValidationError**: 数据验证错误 (400)
- **PermissionError**: 权限错误 (403) 
- **NotFoundError**: 资源不存在 (404)
- **OperationError**: 操作失败 (500)

### 2. 标准化的API控制器

所有API模块都继承自 `StandardCRUDController`，提供：

- 统一的响应格式
- 标准的CRUD操作
- 一致的错误处理
- 规范的日志记录

### 3. 完整的API模块

项目现在包含以下API模块：

- **users**: 用户管理API
- **family**: 家族管理API  
- **members**: 成员管理API
- **relationships**: 关系管理API
- **media**: 媒体管理API

## API设计规范

### 1. 路由设计

```python
# 基础CRUD路由
POST   /api/{module}/           # 创建资源
GET    /api/{module}/           # 获取资源列表
GET    /api/{module}/{id}       # 获取单个资源
PUT    /api/{module}/{id}       # 更新资源
DELETE /api/{module}/{id}       # 删除资源

# 批量操作路由
POST   /api/{module}/batch      # 批量创建
DELETE /api/{module}/batch      # 批量删除

# 特殊功能路由
GET    /api/{module}/search     # 搜索
GET    /api/{module}/statistics # 统计信息
```

### 2. 响应格式

所有API响应都遵循统一格式：

```json
{
    "success": true,
    "message": "操作成功",
    "data": {},
    "request_id": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

分页响应格式：

```json
{
    "success": true,
    "message": "获取数据成功",
    "data": [],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total": 100,
        "total_pages": 5
    },
    "request_id": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### 3. 异常处理最佳实践

在API控制器中使用标准异常处理：

```python
try:
    # 业务逻辑
    result = self.service.some_operation(data, user)
    
    return create_success_response(
        data=self.serialize_object(result, user),
        message="操作成功",
        request_id=get_request_id(request)
    )
    
except (ValidationError, PermissionError, NotFoundError) as e:
    # 业务异常直接抛出，由全局异常处理器处理
    raise e
except Exception as e:
    # 未知异常记录日志并转换为OperationError
    logger.error(f"Operation error: {e}")
    raise OperationError("操作失败")
```

## 使用指南

### 1. 创建新的API模块

1. 在对应app目录下创建 `api.py` 文件
2. 继承 `StandardCRUDController` 类
3. 实现 `serialize_object` 方法
4. 注册路由到 `config/urls.py`

### 2. 异常处理

使用项目定义的标准异常类型：

```python
from apps.common.exceptions import (
    ValidationError, PermissionError, NotFoundError, OperationError
)

# 数据验证失败
if not data.is_valid():
    raise ValidationError("数据验证失败")

# 权限检查失败  
if not user.has_permission():
    raise PermissionError("无权限执行此操作")

# 资源不存在
if not obj.exists():
    raise NotFoundError("资源不存在")

# 操作失败
if not operation_success:
    raise OperationError("操作失败")
```

### 3. 日志记录

使用loguru进行统一日志记录：

```python
from loguru import logger

try:
    # 业务逻辑
    pass
except Exception as e:
    logger.error(f"Operation failed: {e}")
    raise OperationError("操作失败")
```

## 优势

1. **统一性**: 所有API模块使用相同的设计模式和异常处理
2. **可维护性**: 标准化的代码结构便于维护和扩展
3. **可测试性**: 清晰的异常处理和响应格式便于编写测试
4. **文档化**: Django Ninja自动生成OpenAPI文档
5. **性能**: 相比传统Django Views有更好的性能表现

## 迁移完成状态

✅ **已完成的模块**:
- `apps/common/handlers.py` - 全局异常处理器
- `apps/users/api.py` - 用户管理API
- `apps/family/api.py` - 家族管理API (已存在)
- `apps/members/api.py` - 成员管理API
- `apps/relationships/api.py` - 关系管理API  
- `apps/media/api.py` - 媒体管理API
- `config/urls.py` - 统一路由配置

✅ **异常处理器使用情况**:
- 所有API模块都正确使用了全局异常处理器
- 统一的错误响应格式
- 完整的异常类型覆盖

## 下一步建议

1. **服务层完善**: 为每个API模块创建对应的Service类
2. **权限系统**: 完善基于角色的权限控制
3. **缓存策略**: 为频繁查询的API添加缓存
4. **API版本控制**: 为未来的API升级做准备
5. **监控和指标**: 添加API性能监控和业务指标统计

## 总结

项目现在拥有了完整、统一、标准化的Django Ninja API框架，所有定义的全局异常处理器都得到了充分利用。这为项目提供了：

- 高质量的API接口
- 一致的用户体验  
- 良好的开发体验
- 便于维护的代码结构
- 完整的错误处理机制

这个架构为项目的长期发展奠定了坚实的基础。