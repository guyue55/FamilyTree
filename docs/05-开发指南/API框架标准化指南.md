# API框架标准化指南

## 概述

本项目已完成后端API框架的标准化，基于Django Ninja框架构建纯API服务，不提供UI界面。所有API遵循RESTful设计原则和统一的响应格式。

## 架构特点

### 1. 纯API服务
- 基于Django Ninja框架
- 仅提供API接口，不包含前端UI
- 支持OpenAPI 3.0文档自动生成
- 统一的错误处理和响应格式

### 2. 模块化设计
- 认证授权模块 (`apps.auth`)
- 用户管理模块 (`apps.users`)
- 家族管理模块 (`apps.family`)
- 成员管理模块 (`apps.members`)
- 关系管理模块 (`apps.relationships`)
- 媒体管理模块 (`apps.media`)
- 公共工具模块 (`apps.common`)

### 3. 标准化组件
- 统一配置管理 (`config.api_config`)
- 自动文档生成 (`config.api_docs`)
- 标准化测试工具 (`config.api_test`)
- 中间件支持 (`apps.common.middleware`)
- 异常处理器 (`apps.common.handlers`)

## API访问

### 基础URL
```
http://127.0.0.1:8000/api/v1/
```

### 主要端点

#### 系统检查
- `GET /api/v1/system/health` - 系统健康检查
- `GET /api/v1/system/ping` - 服务可用性检查
- `GET /api/v1/system/version` - 版本信息

#### 认证授权
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新Token
- `POST /api/v1/auth/logout` - 用户登出

#### 用户管理
- `GET /api/v1/users/` - 用户列表
- `GET /api/v1/users/me` - 当前用户信息
- `PUT /api/v1/users/me` - 更新用户信息

#### 家族管理
- `GET /api/v1/family/` - 家族列表
- `POST /api/v1/family/` - 创建家族
- `GET /api/v1/family/{id}` - 家族详情
- `PUT /api/v1/family/{id}` - 更新家族

#### 成员管理
- `GET /api/v1/members/` - 成员列表
- `POST /api/v1/members/` - 添加成员
- `GET /api/v1/members/{id}` - 成员详情
- `PUT /api/v1/members/{id}` - 更新成员

#### 关系管理
- `GET /api/v1/relationships/` - 关系列表
- `POST /api/v1/relationships/` - 创建关系
- `GET /api/v1/relationships/{id}` - 关系详情
- `PUT /api/v1/relationships/{id}` - 更新关系

#### 媒体管理
- `GET /api/v1/media/` - 媒体文件列表
- `POST /api/v1/media/upload` - 文件上传
- `GET /api/v1/media/{id}` - 媒体文件详情

### API文档
- Swagger UI: `http://127.0.0.1:8000/api/v1/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/api/v1/openapi.json`

## 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    // 响应数据
  },
  "timestamp": "2025-07-28T19:20:45.123456Z",
  "request_id": "req_abc123def456"
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "Bad Request",
  "data": {
    "errors": [
      {
        "field": "username",
        "message": "This field is required."
      }
    ]
  },
  "timestamp": "2025-07-28T19:20:45.123456Z",
  "request_id": "req_abc123def456"
}
```

### 分页响应
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      // 数据列表
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "pages": 5,
      "has_next": true,
      "has_prev": false
    }
  },
  "timestamp": "2025-07-28T19:20:45.123456Z",
  "request_id": "req_abc123def456"
}
```

## 认证方式

### JWT Token认证
1. 通过登录接口获取access_token
2. 在请求头中添加Authorization字段：
   ```
   Authorization: Bearer <access_token>
   ```

### Token刷新
- access_token有效期：30分钟
- refresh_token有效期：7天
- 使用refresh_token获取新的access_token

## 错误码说明

### HTTP状态码
- `200` - 成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未授权
- `403` - 禁止访问
- `404` - 资源不存在
- `422` - 数据验证错误
- `429` - 请求频率超限
- `500` - 服务器内部错误

### 业务错误码
- `40001` - 用户不存在
- `40002` - 用户已存在
- `40003` - 登录凭证无效
- `40004` - Token已过期
- `40005` - Token无效
- `40101` - 家族不存在
- `40201` - 成员不存在
- `40301` - 关系不存在
- `40302` - 权限不足
- `40401` - 文件过大
- `40402` - 文件类型不支持

## 开发指南

### 添加新的API端点
1. 在对应的app中创建API路由
2. 定义请求/响应Schema
3. 实现业务逻辑
4. 添加异常处理
5. 编写测试用例

### 测试API
使用提供的测试工具类：
```python
from config.api_test import APITestCase

class MyAPITest(APITestCase):
    def test_my_endpoint(self):
        response = self.api_get('/my-endpoint')
        self.assert_api_success(response)
```

### 配置管理
所有API相关配置集中在 `config.api_config` 模块中，包括：
- JWT配置
- 分页配置
- 文件上传配置
- 限流配置
- CORS配置

## 最佳实践

1. **遵循RESTful设计原则**
2. **使用统一的响应格式**
3. **实现完整的错误处理**
4. **添加适当的日志记录**
5. **编写完整的测试用例**
6. **保持API文档更新**
7. **实施安全最佳实践**

## 部署说明

### 开发环境
```bash
python manage.py runserver --settings=config.settings.development
```

### 生产环境
- 禁用DEBUG模式
- 配置HTTPS
- 设置适当的CORS策略
- 配置日志记录
- 实施监控和告警

## 监控和维护

### 健康检查
定期检查 `/api/v1/system/health` 端点，监控：
- 数据库连接状态
- 缓存服务状态
- 磁盘空间使用情况

### 性能监控
- 响应时间监控
- 错误率统计
- 请求频率分析
- 资源使用情况

### 日志管理
- 请求/响应日志
- 错误日志
- 性能日志
- 安全日志