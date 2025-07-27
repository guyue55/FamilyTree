# 族谱系统 (FamilyTree System)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-5.0+-green.svg)](https://www.djangoproject.com/)
[![Vue Version](https://img.shields.io/badge/vue-3.4+-brightgreen.svg)](https://vuejs.org/)

一个现代化的数字族谱管理系统，帮助用户创建、管理和分享家族历史。

## 🌟 功能特性

### 核心功能
- **族谱管理**: 创建和管理多个家族族谱
- **成员管理**: 添加、编辑家族成员信息
- **关系建立**: 建立复杂的家族关系网络
- **可视化展示**: 交互式族谱图形展示
- **多媒体支持**: 上传照片、文档等家族资料

### 高级功能
- **权限控制**: 基于角色的访问控制
- **协作编辑**: 多用户协作编辑族谱
- **数据导入导出**: 支持GEDCOM格式
- **搜索功能**: 全文搜索家族成员
- **统计分析**: 家族数据统计和分析

### 技术特性
- **响应式设计**: 支持桌面端和移动端
- **实时更新**: WebSocket实时数据同步
- **国际化**: 多语言支持
- **高性能**: 优化的数据库查询和缓存策略

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Django 5.0+ (Python 3.12+)
- **数据库**: PostgreSQL 15+ / MySQL 8.0+
- **缓存**: Redis 7.0+
- **搜索**: Elasticsearch 8.0+
- **任务队列**: Celery + Redis
- **API**: Django REST Framework
- **认证**: JWT + OAuth2

### 前端技术栈
- **框架**: Vue.js 3.4+
- **UI组件**: Element Plus 2.4+
- **构建工具**: Vite 5.0+
- **状态管理**: Pinia 2.1+
- **路由**: Vue Router 4.2+
- **HTTP客户端**: Axios 1.6+
- **图形可视化**: G6 (AntV) 4.8+
- **类型系统**: TypeScript 5.0+

### 开发工具
- **代码规范**: ESLint + Prettier
- **测试框架**: Vitest + Cypress
- **容器化**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **监控**: Prometheus + Grafana

## 🚀 快速开始

### 环境要求
- Python 3.12+
- Node.js 18.0+
- PostgreSQL 15+ 或 MySQL 8.0+
- Redis 7.0+

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/guyueju/FamilyTree.git
cd FamilyTree
```

#### 2. 后端设置
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库等信息

# 数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动后端服务
python manage.py runserver
```

#### 3. 前端设置
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 4. 使用Docker（推荐）
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 访问应用
- 前端应用: http://localhost:3000
- 后端API: http://localhost:8000
- 管理后台: http://localhost:8000/admin
- API文档: http://localhost:8000/docs

## 📖 文档

### 项目文档
- [项目章程](docs/01-项目管理/项目章程.md)
- [产品需求文档](docs/02-需求文档/产品需求文档(PRD).md)
- [系统架构设计](docs/03-设计文档/系统架构设计文档.md)
- [数据库设计](docs/03-设计文档/数据库设计文档.md)
- [API接口设计](docs/03-设计文档/API接口设计文档.md)

### 开发规范
- [系统开发规范](docs/04-开发规范/系统开发规范.md)
- [前端开发规范](docs/04-开发规范/前端开发规范.md)
- [后端开发规范](docs/04-开发规范/后端开发规范.md)
- [API接口规范](docs/04-开发规范/API接口规范.md)
- [代码审查规范](docs/04-开发规范/代码审查规范.md)

### 运维文档
- [部署文档](docs/06-部署文档/部署文档.md)
- [运维手册](docs/07-运维文档/运维手册.md)
- [用户手册](docs/08-用户文档/用户手册.md)

## 🧪 测试

### 运行测试
```bash
# 后端测试
python manage.py test

# 前端测试
cd frontend
npm run test

# E2E测试
npm run test:e2e

# 测试覆盖率
npm run test:coverage
```

### 测试要求
- 单元测试覆盖率 ≥ 70%
- 集成测试覆盖核心功能
- E2E测试覆盖主要用户流程

## 🚀 部署

### 生产环境部署
```bash
# 使用Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# 或使用Kubernetes
kubectl apply -f k8s/
```

### 环境配置
- **开发环境**: 本地开发和调试
- **测试环境**: 功能测试和集成测试
- **预生产环境**: 性能测试和用户验收测试
- **生产环境**: 正式运行环境

## 🤝 贡献指南

### 开发流程
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '[feature](scope): add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 提交规范
请遵循 [Git Commit 规范](参考/Git%20Commit%20规范.md)：

```
[type](scope): subject

# 示例
[feature](family): 添加族谱可视化功能
[bugfix](auth): 修复用户登录验证问题
[docs]: 更新API文档
```

### 代码规范
- 遵循项目的代码规范和最佳实践
- 确保所有测试通过
- 添加必要的测试用例
- 更新相关文档

## 📊 项目状态

### 开发进度
- [x] 项目架构设计
- [x] 数据库设计
- [x] API接口设计
- [x] 前端框架搭建
- [x] 用户认证系统
- [ ] 族谱管理功能
- [ ] 可视化展示
- [ ] 多媒体支持
- [ ] 权限控制系统
- [ ] 数据导入导出

### 版本历史
- **v1.0.0** (计划中): 基础功能完成
- **v0.1.0** (开发中): 项目初始化和架构搭建

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👥 团队

- **项目发起人**: 古月居
- **项目经理**: 古月
- **技术负责人**: 古月
- **开发工程师**: 古月

## 📞 联系我们

- **邮箱**: guyuecw@qq.com
- **项目主页**: https://github.com/guyue55/FamilyTree
- **问题反馈**: https://github.com/guyue55/FamilyTree/issues

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户。

---

**族谱系统** - 传承家族历史，连接血脉亲情 ❤️