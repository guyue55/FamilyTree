# 族谱系统API接口设计文档

## 文档信息
- **文档版本**: v1.0
- **创建日期**: 2025年7月27日
- **最后更新**: 2025年7月27日
- **文档状态**: 草稿
- **编写人**: 古月
- **审核人**: 古月

## 1. 接口设计规范

### 1.1 RESTful设计原则
- **资源导向**: URI表示资源，HTTP方法表示操作
- **无状态**: 每个请求包含完整信息
- **统一接口**: 标准HTTP方法和状态码
- **分层系统**: 客户端无需了解服务器内部结构

### 1.2 URL设计规范
- **基础URL**: `https://api.familytree.com/v1`
- **资源命名**: 使用复数名词，如 `/users`, `/families`
- **层级关系**: `/families/{id}/members`
- **查询参数**: `?page=1&page_size=20&ordering=-created_at`

### 1.3 HTTP方法使用
- **GET**: 获取资源
- **POST**: 创建资源
- **PUT**: 完整更新资源
- **PATCH**: 部分更新资源
- **DELETE**: 删除资源

### 1.4 状态码规范
- **200**: 成功
- **201**: 创建成功
- **204**: 删除成功
- **400**: 请求参数错误
- **401**: 未认证
- **403**: 无权限
- **404**: 资源不存在
- **500**: 服务器错误

## 2. 通用接口规范

### 2.1 请求头规范
```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer {token}
X-Request-ID: {unique-request-id}
User-Agent: FamilyTree-Client/1.0
```

### 2.2 响应格式规范

#### 2.2.1 成功响应
```json
{
    "code": 200,
    "message": "success",
    "data": {
        // 具体数据
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

#### 2.2.2 错误响应
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
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

#### 2.2.3 分页响应
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 100,
            "total_pages": 5
        }
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### 2.3 分页参数
- `page`: 页码，从1开始
- `page_size`: 每页数量，默认20，最大100
- `ordering`: 排序字段，如 `-created_at,name`

### 2.4 时间格式
- 统一使用ISO 8601格式: `2025-08-01T12:00:00Z`
- 日期格式: `2025-08-01`

## 3. 认证授权接口

### 3.1 用户注册
```http
POST /api/v1/auth/register
```

**请求参数:**
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "real_name": "string",
    "phone": "string"
}
```

**响应示例:**
```json
{
    "code": 201,
    "message": "注册成功",
    "data": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "real_name": "测试用户",
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "Bearer",
        "expires_in": 3600
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### 3.2 用户登录
```http
POST /api/v1/auth/login
```

**请求参数:**
```json
{
    "username": "string",
    "password": "string"
}
```

**响应示例:**
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
            "username": "testuser",
            "email": "test@example.com",
            "real_name": "测试用户"
        }
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### 3.3 刷新Token
```http
POST /api/v1/auth/refresh
```

**请求头:**
```http
Authorization: Bearer {refresh_token}
```

**响应示例:**
```json
{
    "code": 200,
    "message": "Token刷新成功",
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "Bearer",
        "expires_in": 3600
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### 3.4 用户登出
```http
POST /api/v1/auth/logout
```

**响应示例:**
```json
{
    "code": 200,
    "message": "登出成功",
    "data": null,
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

## 4. 用户管理接口

### 4.1 获取用户信息
```http
GET /api/v1/users/me
```

**响应示例:**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "real_name": "测试用户",
        "avatar_url": "http://localhost:8000/avatar.jpg",
        "gender": 1,
        "birth_date": "1990-01-01",
        "create_time": "2025-08-01T12:00:00Z"
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### 4.2 更新用户信息
```http
PUT /api/v1/users/me
```

**请求参数:**
```json
{
    "real_name": "string",
    "avatar_url": "string",
    "gender": 1,
    "birth_date": "1990-01-01"
}
```

### 4.3 修改密码
```http
POST /api/v1/users/me/change-password
```

**请求参数:**
```json
{
    "old_password": "string",
    "new_password": "string"
}
```

## 5. 族谱管理接口

### 5.1 创建族谱
```http
POST /api/v1/families
```

**请求参数:**
```json
{
    "name": "string",
    "description": "string",
    "family_name": "string",
    "origin_place": "string",
    "visibility": 1
}
```

**响应示例:**
```json
{
    "code": 201,
    "message": "族谱创建成功",
    "data": {
        "id": 1,
        "name": "张氏族谱",
        "description": "张氏家族族谱",
        "family_name": "张",
        "creator_id": 1,
        "visibility": 1,
        "member_count": 0,
        "generation_count": 0,
        "create_time": "2025-08-01T12:00:00Z"
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### 5.2 获取族谱列表
```http
GET /api/v1/families?page=1&page_size=20&ordering=-created_at
```

**查询参数:**
- `page`: 页码
- `page_size`: 每页数量
- `ordering`: 排序方式
- `family_name`: 家族姓氏筛选
- `visibility`: 可见性筛选

**响应示例:**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [
            {
                "id": 1,
                "name": "张氏族谱",
                "family_name": "张",
                "member_count": 50,
                "generation_count": 5,
                "create_time": "2025-08-01T12:00:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 1,
            "total_pages": 1
        }
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### 5.3 获取族谱详情
```http
GET /api/v1/families/{family_id}
```

**响应示例:**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "name": "张氏族谱",
        "description": "张氏家族族谱",
        "family_name": "张",
        "origin_place": "山东济南",
        "creator_id": 1,
        "visibility": 1,
        "member_count": 50,
        "generation_count": 5,
        "create_time": "2025-08-01T12:00:00Z",
        "creator": {
            "id": 1,
            "username": "creator",
            "real_name": "创建者"
        }
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### 5.4 更新族谱信息
```http
PUT /api/v1/families/{family_id}
```

**请求参数:**
```json
{
    "name": "string",
    "description": "string",
    "origin_place": "string",
    "visibility": 1
}
```

### 5.5 删除族谱
```http
DELETE /api/v1/families/{family_id}
```

## 6. 族谱成员接口

### 6.1 添加成员
```http
POST /api/v1/families/{family_id}/members
```

**请求参数:**
```json
{
    "name": "string",
    "gender": 1,
    "generation": 1,
    "birth_date": "1990-01-01",
    "death_date": "2020-01-01",
    "birth_place": "string",
    "current_address": "string",
    "occupation": "string",
    "education": "string",
    "biography": "string",
    "is_alive": 1
}
```

**响应示例:**
```json
{
    "code": 201,
    "message": "成员添加成功",
    "data": {
        "id": 1,
        "name": "张三",
        "gender": 1,
        "generation": 1,
        "birth_date": "1990-01-01",
        "is_alive": 1,
        "create_time": "2025-08-01T12:00:00Z"
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### 6.2 获取成员列表
```http
GET /api/v1/families/{family_id}/members?page=1&page_size=20
```

**查询参数:**
- `page`: 页码
- `page_size`: 每页数量
- `generation`: 世代筛选
- `gender`: 性别筛选
- `is_alive`: 是否在世筛选
- `search`: 姓名搜索

**响应示例:**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [
            {
                "id": 1,
                "name": "张三",
                "gender": 1,
                "generation": 1,
                "birth_date": "1990-01-01",
                "is_alive": 1,
                "photo_url": "http://localhost:8000/photo.jpg"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 1,
            "total_pages": 1
        }
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### 6.3 获取成员详情
```http
GET /api/v1/families/{family_id}/members/{member_id}
```

**响应示例:**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "name": "张三",
        "gender": 1,
        "generation": 1,
        "birth_date": "1990-01-01",
        "birth_place": "山东济南",
        "current_address": "北京市朝阳区",
        "occupation": "工程师",
        "education": "本科",
        "biography": "个人简介",
        "is_alive": 1,
        "photo_url": "http://localhost:8000/photo.jpg",
        "relationships": [
            {
                "related_member": {
                    "id": 2,
                    "name": "李四"
                },
                "relationship_type": 3,
                "relationship_desc": "夫妻"
            }
        ]
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### 6.4 更新成员信息
```http
PUT /api/v1/families/{family_id}/members/{member_id}
```

### 6.5 删除成员
```http
DELETE /api/v1/families/{family_id}/members/{member_id}
```

## 7. 关系管理接口

### 7.1 建立关系
```http
POST /api/v1/families/{family_id}/relationships
```

**请求参数:**
```json
{
    "person_a_id": 1,
    "person_b_id": 2,
    "relationship_type": 3,
    "relationship_desc": "夫妻",
    "marriage_date": "2020-01-01"
}
```

### 7.2 获取关系列表
```http
GET /api/v1/families/{family_id}/relationships
```

### 7.3 更新关系
```http
PUT /api/v1/families/{family_id}/relationships/{relationship_id}
```

### 7.4 删除关系
```http
DELETE /api/v1/families/{family_id}/relationships/{relationship_id}
```

## 8. 称呼计算接口

### 8.1 计算称呼
```http
POST /api/v1/kinship/calculate
```

**请求参数:**
```json
{
    "family_tree_id": 1,
    "from_member_id": 1,
    "to_member_id": 2,
    "dialect": "standard"
}
```

**响应示例:**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "relationship_path": "father",
        "title": "父亲",
        "reverse_title": "儿子",
        "generation_diff": 1,
        "is_direct": true,
        "path_details": [
            {
                "from_id": 1,
                "to_id": 2,
                "relationship": "father"
            }
        ]
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### 8.2 获取称呼字典
```http
GET /api/v1/kinship/titles?dialect=standard
```

**响应示例:**
```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "relationship_path": "father",
            "title": "父亲",
            "dialect": "standard",
            "generation_diff": 1,
            "is_direct": true
        }
    ],
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

## 9. 文件管理接口

### 9.1 上传文件
```http
POST /api/v1/files/upload
```

**请求参数:** (multipart/form-data)
- `file`: 文件
- `related_type`: 关联类型 (avatar, photo, document)
- `related_id`: 关联ID

**响应示例:**
```json
{
    "code": 201,
    "message": "文件上传成功",
    "data": {
        "id": 1,
        "original_name": "photo.jpg",
        "file_name": "20240101_123456_photo.jpg",
        "file_url": "http://localhost:8000/files/20240101_123456_photo.jpg",
        "file_size": 1024000,
        "file_type": "image"
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### 9.2 获取文件信息
```http
GET /api/v1/files/{file_id}
```

### 9.3 删除文件
```http
DELETE /api/v1/files/{file_id}
```

## 10. 族谱可视化接口

### 10.1 获取族谱图数据
```http
GET /api/v1/families/{family_id}/graph
```

**查询参数:**
- `layout`: 布局类型 (tree, force, circular)
- `generation_range`: 世代范围 "1-5"
- `center_member_id`: 中心成员ID

**响应示例:**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "nodes": [
            {
                "id": "member_1",
                "name": "张三",
                "gender": 1,
                "generation": 1,
                "is_alive": 1,
                "photo_url": "http://localhost:8000/photo.jpg",
                "x": 100,
                "y": 200
            }
        ],
        "edges": [
            {
                "id": "rel_1",
                "source": "member_1",
                "target": "member_2",
                "relationship_type": 3,
                "relationship_desc": "夫妻"
            }
        ],
        "layout_config": {
            "type": "tree",
            "direction": "TB"
        }
    },
    "timestamp": "2025-08-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

## 11. 权限管理接口

### 11.1 邀请用户
```http
POST /api/v1/families/{family_id}/invitations
```

**请求参数:**
```json
{
    "email": "string",
    "role_type": 3,
    "message": "string"
}
```

### 11.2 获取权限列表
```http
GET /api/v1/families/{family_id}/permissions
```

### 11.3 更新用户权限
```http
PUT /api/v1/families/{family_id}/permissions/{user_id}
```

### 11.4 移除用户权限
```http
DELETE /api/v1/families/{family_id}/permissions/{user_id}
```

## 12. 系统管理接口

### 12.1 获取系统配置
```http
GET /api/v1/system/configs
```

### 12.2 获取操作日志
```http
GET /api/v1/system/logs?page=1&page_size=20
```

## 13. 错误码定义

### 13.1 通用错误码
- `10001`: 参数错误
- `10002`: 数据不存在
- `10003`: 权限不足
- `10004`: 操作失败

### 13.2 用户相关错误码
- `20001`: 用户名已存在
- `20002`: 邮箱已存在
- `20003`: 密码错误
- `20004`: 用户不存在

### 13.3 族谱相关错误码
- `30001`: 族谱不存在
- `30002`: 成员不存在
- `30003`: 关系已存在
- `30004`: 关系不存在

### 13.4 文件相关错误码
- `40001`: 文件类型不支持
- `40002`: 文件大小超限
- `40003`: 文件上传失败

## 14. 接口版本管理

### 14.1 版本策略
- URL路径版本: `/api/v1/`, `/api/v2/`
- 向后兼容: 旧版本保持可用
- 废弃通知: 提前通知版本废弃

### 14.2 版本变更
- 主版本: 不兼容变更
- 次版本: 新增功能
- 修订版本: 错误修复

## 15. 接口测试

### 15.1 测试环境
- 开发环境: `https://dev-api.familytree.com`
- 测试环境: `https://test-api.familytree.com`
- 生产环境: `https://api.familytree.com`

### 15.2 测试工具
- Postman集合
- Swagger文档
- 自动化测试脚本

### 15.3 测试数据
- 测试用户账号
- 示例族谱数据
- 测试文件资源