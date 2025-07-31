# Family应用测试文档

## 概述

本文档描述了Family应用的完整测试套件，包括单元测试、集成测试、性能测试等。

## 测试架构

### 测试层级

1. **单元测试** - 测试单个组件的功能
   - 模型测试 (`test_models.py`)
   - 模式测试 (`test_schemas.py`)
   - 服务测试 (`test_services.py`)
   - 权限测试 (`test_permissions.py`)

2. **集成测试** - 测试组件间的交互
   - API集成测试 (`test_integration.py`)
   - 数据库集成测试
   - 缓存集成测试
   - 外部服务集成测试

3. **接口测试** - 测试API接口
   - API端点测试 (`test_api.py`)
   - 请求/响应测试
   - 认证授权测试
   - 错误处理测试

4. **性能测试** - 测试系统性能
   - API性能测试 (`test_performance.py`)
   - 数据库性能测试
   - 缓存性能测试
   - 并发测试

### 测试配置

- **测试设置**: `config/settings/testing.py`
- **测试配置**: `conftest.py`
- **pytest配置**: `pytest.ini`
- **运行脚本**: `run_tests.py`

## 测试文件说明

### 1. test_api.py - API接口测试

测试所有Family应用的API端点：

- **CRUD操作测试**
  - 创建家族 (`POST /api/families/`)
  - 获取家族列表 (`GET /api/families/`)
  - 获取家族详情 (`GET /api/families/{id}/`)
  - 更新家族 (`PUT /api/families/{id}/`)
  - 删除家族 (`DELETE /api/families/{id}/`)

- **家族设置测试**
  - 获取设置 (`GET /api/families/{id}/settings/`)
  - 更新设置 (`PUT /api/families/{id}/settings/`)

- **邀请管理测试**
  - 发送邀请 (`POST /api/families/{id}/invitations/`)
  - 处理邀请 (`POST /api/families/{id}/invitations/{invitation_id}/process/`)

- **成员管理测试**
  - 获取成员列表 (`GET /api/families/{id}/members/`)
  - 更新成员角色 (`PUT /api/families/{id}/members/{user_id}/`)
  - 移除成员 (`DELETE /api/families/{id}/members/{user_id}/`)

- **统计信息测试**
  - 获取统计 (`GET /api/families/{id}/statistics/`)

- **公开搜索测试**
  - 搜索公开家族 (`GET /api/families/public/search/`)

### 2. test_models.py - 模型测试

测试Django模型的功能：

- **Family模型测试**
  - 字段验证
  - 模型方法
  - 字符串表示
  - 约束检查

- **FamilySettings模型测试**
  - 设置字段验证
  - 默认值测试
  - 关联关系测试

- **FamilyInvitation模型测试**
  - 邀请状态管理
  - 过期时间检查
  - 邀请码生成

### 3. test_schemas.py - 模式测试

测试Pydantic模式的数据验证：

- **枚举测试**
  - `FamilyVisibility`
  - `InvitationStatus`
  - `TreeLayout`
  - `ExportFormat`

- **基础模式测试**
  - `FamilyBaseSchema`
  - `FamilyCreateSchema`
  - `FamilyUpdateSchema`

- **模型模式测试**
  - `FamilyModelSchema`
  - `FamilySettingsModelSchema`
  - `FamilyInvitationModelSchema`

- **查询模式测试**
  - `FamilyFilterSchema`
  - `FamilyQuerySchema`
  - `PublicFamilyQuerySchema`

### 4. test_services.py - 服务层测试

测试业务逻辑服务：

- **FamilyService测试**
  - 家族创建逻辑
  - 权限检查
  - 缓存管理
  - 事务处理

- **FamilyInvitationService测试**
  - 邀请发送
  - 邀请处理
  - 邮件通知

- **FamilyMemberService测试**
  - 成员管理
  - 角色分配
  - 权限验证

### 5. test_permissions.py - 权限测试

测试权限和安全机制：

- **权限枚举测试**
  - `FamilyPermission`

- **权限检查测试**
  - `has_family_permission`
  - `require_family_permission`

- **异常处理测试**
  - 自定义异常类
  - 错误消息
  - 异常链

- **安全机制测试**
  - 数据访问隔离
  - SQL注入防护
  - XSS防护
  - 敏感数据保护

### 6. test_integration.py - 集成测试

测试组件间的集成：

- **API集成测试**
  - 完整的家族生命周期
  - 成员管理流程
  - 权限集成

- **数据库集成测试**
  - 事务回滚
  - 约束检查
  - 并发访问

- **缓存集成测试**
  - 缓存操作
  - 缓存失效
  - 性能对比

- **外部服务集成测试**
  - 邮件服务
  - 文件存储
  - 通知服务

### 7. test_performance.py - 性能测试

测试系统性能指标：

- **API性能测试**
  - 响应时间
  - 并发处理
  - 分页性能

- **数据库性能测试**
  - 查询优化
  - 批量操作
  - 索引效果

- **缓存性能测试**
  - 缓存命中率
  - 内存使用
  - 过期处理

- **并发性能测试**
  - 并发创建
  - 竞态条件
  - 死锁预防

## 测试工具和配置

### conftest.py - 测试配置

提供测试所需的fixtures和工具：

- **数据工厂**
  - `UserFactory`
  - `FamilyFactory`
  - `FamilySettingsFactory`
  - `FamilyInvitationFactory`

- **测试工具**
  - `FamilyTestDataGenerator`
  - `FamilyTestUtils`
  - `FamilyTestConfig`

- **pytest fixtures**
  - 数据库设置
  - 认证用户
  - Mock服务

### run_tests.py - 测试运行脚本

提供便捷的测试执行方式：

```bash
# 运行所有测试
python run_tests.py

# 运行特定模块
python run_tests.py --module api

# 生成覆盖率报告
python run_tests.py --coverage

# 运行性能测试
python run_tests.py --performance

# 并行运行测试
python run_tests.py --parallel

# 详细输出
python run_tests.py --verbose

# 按套件运行
python run_tests.py --suites
```

## 测试最佳实践

### 1. 测试命名

- 使用描述性的测试名称
- 遵循 `test_<功能>_<条件>_<期望结果>` 格式
- 使用中文注释说明测试目的

### 2. 测试数据

- 使用Factory Boy生成测试数据
- 每个测试独立创建所需数据
- 测试后自动清理数据

### 3. 测试隔离

- 每个测试方法独立运行
- 使用事务回滚确保数据隔离
- Mock外部依赖

### 4. 断言

- 使用具体的断言方法
- 提供清晰的错误消息
- 验证所有相关状态

### 5. 性能测试

- 设置合理的性能基准
- 监控关键性能指标
- 在CI中跳过耗时测试

## 运行测试

### 环境准备

1. 安装测试依赖：
```bash
pip install pytest pytest-django factory-boy pytest-cov pytest-mock
```

2. 设置测试环境变量：
```bash
export DJANGO_SETTINGS_MODULE=config.settings.testing
```

### 运行方式

1. **使用pytest直接运行**：
```bash
pytest apps/family/tests/
```

2. **使用Django管理命令**：
```bash
python manage.py test apps.family.tests
```

3. **使用测试脚本**：
```bash
python apps/family/tests/run_tests.py
```

### 测试报告

- **覆盖率报告**: `htmlcov/index.html`
- **HTML测试报告**: `test_report.html`
- **JUnit XML报告**: `test_results.xml`

## 持续集成

### GitHub Actions配置

```yaml
name: Family App Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-django factory-boy pytest-cov
      - name: Run tests
        run: |
          python apps/family/tests/run_tests.py --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 故障排除

### 常见问题

1. **数据库连接错误**
   - 检查测试数据库配置
   - 确保测试设置正确

2. **导入错误**
   - 检查Python路径
   - 确保Django应用已注册

3. **权限错误**
   - 检查测试用户权限
   - 确保认证配置正确

4. **性能测试失败**
   - 调整性能基准
   - 检查系统资源

### 调试技巧

1. 使用 `pytest -s` 查看打印输出
2. 使用 `pytest --pdb` 进入调试器
3. 使用 `pytest -v` 查看详细信息
4. 使用 `pytest --tb=long` 查看完整错误信息

## 扩展测试

### 添加新测试

1. 在相应的测试文件中添加测试方法
2. 使用适当的测试标记
3. 更新测试文档
4. 运行测试确保通过

### 自定义断言

```python
def assert_family_response(response, expected_family):
    """自定义家族响应断言"""
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == expected_family.name
    assert data['description'] == expected_family.description
```

### 测试数据生成

```python
def create_test_family_with_members(member_count=5):
    """创建带成员的测试家族"""
    family = FamilyFactory()
    members = UserFactory.create_batch(member_count)
    for member in members:
        FamilyMembershipFactory(family=family, user=member)
    return family, members
```

这个测试套件提供了Family应用的全面测试覆盖，确保代码质量和系统稳定性。