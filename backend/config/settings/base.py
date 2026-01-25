"""
Django基础配置文件

该文件包含了所有环境共用的基础配置项。
遵循Google Python Style Guide和Django最佳实践。
"""

from pathlib import Path
from decouple import config
from config.logging_config import setup_logging

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 安全配置
SECRET_KEY = config("SECRET_KEY", default="django-insecure-change-me-in-production")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

# 应用配置
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "ninja",  # Django Ninja API框架
    "corsheaders",  # CORS处理
]

LOCAL_APPS = [
    "apps.users",  # 用户管理
    "apps.family",  # 家族管理
    "apps.members",  # 成员管理
    "apps.relationships",  # 关系管理
    "apps.kinship",  # 亲属称呼计算
    "apps.media",  # 媒体文件
    "apps.common",  # 公共模块
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 中间件配置
MIDDLEWARE = [
    "apps.common.middleware.RequestTrackingMiddleware",  # 请求跟踪中间件，必须在最前面
    "apps.common.middleware.SecurityHeadersMiddleware",  # 安全头中间件
    "apps.common.middleware.PerformanceMonitoringMiddleware",  # 性能监控中间件
    "corsheaders.middleware.CorsMiddleware",  # CORS中间件
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.common.middleware.RateLimitMiddleware",  # 限流中间件
    "apps.common.middleware.NinjaResponseFormatterMiddleware",  # Django Ninja响应格式化中间件
    "apps.common.middleware.ExceptionHandlingMiddleware",  # 异常处理中间件
    "apps.common.middleware.HealthCheckMiddleware",  # 健康检查中间件，放在最后
]

# URL配置
ROOT_URLCONF = "config.urls"

# 模板配置
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI应用
WSGI_APPLICATION = "config.wsgi.application"

# 数据库配置
DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": config("DB_NAME", default=BASE_DIR / "db.sqlite3"),
        "USER": config("DB_USER", default=""),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default=""),
        "PORT": config("DB_PORT", default=""),
        "OPTIONS": {
            "charset": "utf8mb4",
        }
        if config("DB_ENGINE", default="").endswith("mysql")
        else {},
    }
}

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# 国际化配置
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

# 静态文件配置
STATIC_URL = config("STATIC_URL", default="/static/")
STATIC_ROOT = config("STATIC_ROOT", default=BASE_DIR / "staticfiles")
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# 媒体文件配置
MEDIA_URL = config("MEDIA_URL", default="/media/")
MEDIA_ROOT = config("MEDIA_ROOT", default=BASE_DIR / "media")

# 默认主键字段类型
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 自定义用户模型
AUTH_USER_MODEL = "users.User"

# Redis缓存配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Session配置
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 86400  # 24小时

# CORS配置
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000",
    cast=lambda v: [s.strip() for s in v.split(",")],
)
CORS_ALLOW_CREDENTIALS = True

# CSRF配置
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

# JWT配置
JWT_SECRET_KEY = config("JWT_SECRET_KEY", default=SECRET_KEY)
JWT_ALGORITHM = config("JWT_ALGORITHM", default="HS256")
JWT_ACCESS_TOKEN_LIFETIME = config(
    "JWT_ACCESS_TOKEN_LIFETIME", default=3600, cast=int
)  # 1小时
JWT_REFRESH_TOKEN_LIFETIME = config(
    "JWT_REFRESH_TOKEN_LIFETIME", default=86400, cast=int
)  # 24小时

# 日志配置 - 使用loguru
setup_logging(BASE_DIR)

# Celery配置
CELERY_BROKER_URL = config("CELERY_REDIS_URL", default="redis://127.0.0.1:6379/2")
CELERY_RESULT_BACKEND = config("CELERY_REDIS_URL", default="redis://127.0.0.1:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# 文件上传配置
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644

# 安全配置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# API配置
API_VERSION = "v1"
API_TITLE = "族谱系统API"
API_DESCRIPTION = "族谱系统后端API接口文档"
