# 族谱系统后端

基于Django 4.2 + Django-Ninja的现代化族谱管理系统后端API。

## 技术栈

- **框架**: Django 4.2 + Django-Ninja 1.0+
- **数据库**: MySQL 8.0 + Redis 7.0+
- **日志**: loguru 0.7+
- **异步任务**: Celery 5.3+
- **图像处理**: Pillow 10.0+
- **测试**: pytest + factory-boy

## 项目结构

```
backend/
├── familytree_project/    # Django项目配置
├── apps/                  # Django应用
│   ├── users/            # 用户管理
│   ├── families/         # 家族管理
│   ├── relationships/    # 关系管理
│   ├── media/           # 媒体文件管理
│   └── common/          # 公共模块
├── utils/               # 工具函数
├── tests/               # 测试文件
├── requirements/        # 依赖文件
├── static/              # 静态文件
├── media/               # 媒体文件
├── logs/                # 日志文件
└── manage.py            # Django管理脚本
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements/development.txt
```

### 2. 环境配置

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑环境变量
# 配置数据库连接、Redis等
```

### 3. 数据库初始化

```bash
# 创建数据库迁移
python manage.py makemigrations

# 执行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 4. 启动服务

```bash
# 启动开发服务器
python manage.py runserver

# 启动Celery (另开终端)
celery -A familytree_project worker -l info
```

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 开发规范

- 遵循Google Python Style Guide
- 使用loguru进行日志记录
- 所有API使用Django-Ninja框架
- 数据验证使用Pydantic
- 测试覆盖率要求 > 80%

## 部署

详见 [部署文档](../docs/06-部署文档/部署文档.md)

## 许可证

MIT License