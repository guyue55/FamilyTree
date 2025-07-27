# 族谱系统API接口规范

## 文档信息
- **文档名称**: 族谱系统API接口规范
- **版本**: 1.0
- **创建日期**: 2025年7月27日
- **最后更新**: 2025年7月27日
- **维护人员**: 开发团队

## 1. API设计原则

### 1.1 RESTful设计
遵循REST架构风格，使用标准HTTP方法：
- **GET**: 获取资源
- **POST**: 创建资源
- **PUT**: 更新整个资源
- **PATCH**: 部分更新资源
- **DELETE**: 删除资源

### 1.2 URL设计规范   
# 基础格式
https://api.familytree.com/api/v1/{resource}

# 资源集合
GET /api/v1/users                    # 获取用户列表
POST /api/v1/users                   # 创建用户

# 单个资源
GET /api/v1/users/{id}               # 获取用户详情
PUT /api/v1/users/{id}               # 更新用户
DELETE /api/v1/users/{id}            # 删除用户

# 嵌套资源
GET /api/v1/families/{id}/members    # 获取家族成员
POST /api/v1/families/{id}/members   # 添加家族成员

# 资源操作
POST /api/v1/users/{id}/activate     # 激活用户
POST /api/v1/families/{id}/join      # 加入家族
```

### 1.3 版本控制
- 使用URL路径版本控制：`/api/v1/`
- 主版本号变更时创建新路径：`/api/v2/`
- 向后兼容的更新不改变版本号

## 2. 请求规范

### 2.1 请求头
```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer {token}
X-Request-ID: {unique-request-id}
User-Agent: FamilyTree-Client/1.0
```

### 2.2 请求体格式
```json
{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "real_name": "张三",
  "phone": "13800138000"
}
```

### 2.3 查询参数
```
# 分页参数
?page=1&page_size=20

# 排序参数
?ordering=-created_at,name

# 过滤参数
?status=active&role=admin

# 搜索参数
?search=张三

# 字段选择
?fields=id,name,email
```

## 3. 响应规范

### 3.1 统一响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 响应数据
  },
  "timestamp": "2025-07-27T10:30:00Z",
  "request_id": "req_123456789"
}
```

### 3.2 成功响应示例
```json
# 单个资源
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "real_name": "张三",
    "created_at": "2025-07-27T10:30:00Z"
  },
  "timestamp": "2025-07-27T10:30:00Z",
  "request_id": "req_123456789"
}

# 资源列表
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "username": "zhangsan",
        "email": "zhangsan@example.com"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  },
  "timestamp": "2025-07-27T10:30:00Z",
  "request_id": "req_123456789"
}
```

### 3.3 错误响应格式
```json
{
  "code": 400,
  "message": "参数错误",
  "data": null,
  "errors": [
    {
      "field": "email",
      "message": "邮箱格式不正确"
    }
  ],
  "timestamp": "2025-07-27T10:30:00Z",
  "request_id": "req_123456789"
}
```

## 4. HTTP状态码规范

### 4.1 成功状态码
- **200 OK**: 请求成功
- **201 Created**: 资源创建成功
- **204 No Content**: 请求成功，无返回内容（如删除操作）

### 4.2 客户端错误状态码
- **400 Bad Request**: 请求参数错误
- **401 Unauthorized**: 未认证
- **403 Forbidden**: 无权限
- **404 Not Found**: 资源不存在
- **409 Conflict**: 资源冲突
- **422 Unprocessable Entity**: 请求格式正确但语义错误
- **429 Too Many Requests**: 请求频率限制

### 4.3 服务器错误状态码
- **500 Internal Server Error**: 服务器内部错误
- **502 Bad Gateway**: 网关错误
- **503 Service Unavailable**: 服务不可用

## 5. 认证与授权

### 5.1 JWT认证
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 5.2 Token格式
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 5.3 权限控制
```json
# 用户权限
{
  "user_id": 1,
  "permissions": [
    "family.view",
    "family.edit",
    "member.add",
    "member.edit"
  ],
  "roles": ["family_admin"]
}
```

## 6. API接口定义

### 6.1 用户管理接口

#### 6.1.1 用户注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password": "password123",
  "real_name": "张三",
  "phone": "13800138000"
}
```

响应：
```json
{
  "code": 201,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "real_name": "张三"
  }
}
```

#### 6.1.2 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "zhangsan",
  "password": "password123"
}
```

响应：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "zhangsan",
      "email": "zhangsan@example.com",
      "real_name": "张三"
    }
  }
}
```

#### 6.1.3 获取用户信息
```http
GET /api/v1/users/me
Authorization: Bearer {token}
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "real_name": "张三",
    "phone": "13800138000",
    "avatar_url": "http://localhost:8000/avatars/1.jpg",
    "created_at": "2025-07-27T10:30:00Z"
  }
}
```

#### 6.1.4 更新用户信息
```http
PUT /api/v1/users/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "real_name": "张三丰",
  "phone": "13900139000",
  "avatar_url": "http://localhost:8000/avatars/new.jpg"
}
```

### 6.2 家族管理接口

#### 6.2.1 创建家族
```http
POST /api/v1/families
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "张氏家族",
  "description": "张氏家族族谱",
  "origin_place": "山东省济南市",
  "founder_name": "张始祖",
  "founded_year": 1368,
  "family_motto": "忠孝传家",
  "is_public": true
}
```

响应：
```json
{
  "code": 201,
  "message": "家族创建成功",
  "data": {
    "id": 1,
    "name": "张氏家族",
    "description": "张氏家族族谱",
    "origin_place": "山东省济南市",
    "founder_name": "张始祖",
    "founded_year": 1368,
    "family_motto": "忠孝传家",
    "is_public": true,
    "creator_id": 1,
    "created_at": "2025-07-27T10:30:00Z"
  }
}
```

#### 6.2.2 获取家族列表
```http
GET /api/v1/families?page=1&page_size=20&search=张氏
Authorization: Bearer {token}
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "张氏家族",
        "description": "张氏家族族谱",
        "member_count": 25,
        "creator": {
          "id": 1,
          "username": "zhangsan",
          "real_name": "张三"
        },
        "created_at": "2025-07-27T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 1,
      "total_pages": 1
    }
  }
}
```

#### 6.2.3 获取家族详情
```http
GET /api/v1/families/{id}
Authorization: Bearer {token}
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "张氏家族",
    "description": "张氏家族族谱",
    "origin_place": "山东省济南市",
    "founder_name": "张始祖",
    "founded_year": 1368,
    "family_motto": "忠孝传家",
    "family_rules": "家规内容",
    "cover_image_url": "http://localhost:8000/covers/1.jpg",
    "is_public": true,
    "member_count": 25,
    "creator": {
      "id": 1,
      "username": "zhangsan",
      "real_name": "张三"
    },
    "my_role": "admin",
    "created_at": "2025-07-27T10:30:00Z"
  }
}
```

### 6.3 家族成员接口

#### 6.3.1 获取家族成员列表
```http
GET /api/v1/families/{family_id}/members?page=1&page_size=20&role=admin
Authorization: Bearer {token}
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "user": {
          "id": 1,
          "username": "zhangsan",
          "real_name": "张三",
          "avatar_url": "http://localhost:8000/avatars/1.jpg"
        },
        "role": "admin",
        "join_date": "2025-07-27",
        "status": "active"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 1,
      "total_pages": 1
    }
  }
}
```

#### 6.3.2 邀请成员加入家族
```http
POST /api/v1/families/{family_id}/members/invite
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "lisi@example.com",
  "role": "member",
  "message": "邀请您加入张氏家族"
}
```

#### 6.3.3 申请加入家族
```http
POST /api/v1/families/{family_id}/join
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "我是张氏后人，申请加入家族"
}
```

### 6.4 成员关系接口

#### 6.4.1 添加成员关系
```http
POST /api/v1/families/{family_id}/relationships
Authorization: Bearer {token}
Content-Type: application/json

{
  "parent_id": 1,
  "child_id": 2,
  "relationship_type": "father"
}
```

#### 6.4.2 获取家族关系图
```http
GET /api/v1/families/{family_id}/tree
Authorization: Bearer {token}
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "nodes": [
      {
        "id": 1,
        "user_id": 1,
        "name": "张三",
        "gender": "male",
        "birth_date": "1980-01-01",
        "generation": 1
      }
    ],
    "edges": [
      {
        "source": 1,
        "target": 2,
        "relationship": "father"
      }
    ]
  }
}
```

### 6.5 媒体文件接口

#### 6.5.1 上传文件
```http
POST /api/v1/media/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [binary data]
family_id: 1
member_id: 1
description: "家族合影"
```

响应：
```json
{
  "code": 201,
  "message": "文件上传成功",
  "data": {
    "id": 1,
    "filename": "family_photo_20250727.jpg",
    "original_filename": "合影.jpg",
    "file_path": "/media/images/2025/07/27/family_photo_20250727.jpg",
    "file_size": 1024000,
    "mime_type": "image/jpeg",
    "file_type": "image",
    "width": 1920,
    "height": 1080,
    "description": "家族合影",
    "upload_url": "http://localhost:8000/media/images/2025/07/27/family_photo_20250727.jpg"
  }
}
```

#### 6.5.2 获取媒体文件列表
```http
GET /api/v1/media?family_id=1&file_type=image&page=1&page_size=20
Authorization: Bearer {token}
```

## 7. 错误处理

### 7.1 错误码定义
```json
{
  "1000": "系统错误",
  "1001": "参数错误",
  "1002": "数据验证失败",
  "2001": "用户不存在",
  "2002": "密码错误",
  "2003": "用户已存在",
  "3001": "家族不存在",
  "3002": "无权限访问家族",
  "3003": "已是家族成员",
  "4001": "文件格式不支持",
  "4002": "文件大小超限"
}
```

### 7.2 错误响应示例
```json
{
  "code": 1002,
  "message": "数据验证失败",
  "data": null,
  "errors": [
    {
      "field": "email",
      "message": "邮箱格式不正确"
    },
    {
      "field": "phone",
      "message": "手机号格式不正确"
    }
  ],
  "timestamp": "2025-07-27T10:30:00Z",
  "request_id": "req_123456789"
}
```

## 8. 分页规范

### 8.1 分页参数
```
page: 页码，从1开始
page_size: 每页数量，默认20，最大100
```

### 8.2 分页响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

## 9. 搜索与过滤

### 9.1 搜索参数
```
# 全文搜索
?search=张三

# 字段搜索
?name=张三&email=zhangsan@example.com

# 范围搜索
?created_at_gte=2025-01-01&created_at_lte=2025-12-31

# 包含搜索
?status_in=active,pending
```

### 9.2 排序参数
```
# 单字段排序
?ordering=created_at          # 升序
?ordering=-created_at         # 降序

# 多字段排序
?ordering=-created_at,name    # 先按创建时间降序，再按姓名升序
```

## 10. 限流规范

### 10.1 限流策略
- **用户级限流**: 每用户每分钟100次请求
- **IP级限流**: 每IP每分钟200次请求
- **接口级限流**: 特殊接口单独限制

### 10.2 限流响应头
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642694400
```

### 10.3 限流错误响应
```json
{
  "code": 429,
  "message": "请求频率过高，请稍后再试",
  "data": null,
  "timestamp": "2025-07-27T10:30:00Z",
  "request_id": "req_123456789"
}
```

## 11. API文档

### 11.1 OpenAPI规范
使用OpenAPI 3.0规范生成API文档

### 11.2 文档访问
- **开发环境**: http://localhost:8000/docs
- **测试环境**: https://test-api.familytree.com/docs
- **生产环境**: https://api.familytree.com/docs

### 11.3 文档内容
- 接口列表
- 请求参数说明
- 响应格式说明
- 错误码说明
- 示例代码

## 12. 测试规范

### 12.1 API测试
```python
import pytest
from django.test import TestCase
from rest_framework.test import APIClient

class UserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }
    
    def test_user_registration(self):
        response = self.client.post('/api/v1/auth/register', self.user_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['code'], 201)
    
    def test_user_login(self):
        # 先注册用户
        self.client.post('/api/v1/auth/register', self.user_data)
        
        # 登录测试
        login_data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = self.client.post('/api/v1/auth/login', login_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json()['data'])
```

### 12.2 性能测试
使用工具如Locust进行API性能测试

### 12.3 安全测试
- SQL注入测试
- XSS攻击测试
- 权限绕过测试
- 参数篡改测试

---

**注意**: 本规范是族谱系统项目的API接口设计指导文档，所有API开发都应严格遵守。如有疑问或建议，请及时与团队沟通。