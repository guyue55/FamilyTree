"""
Django开发环境配置文件

该文件包含了开发环境特有的配置项。
继承自base.py的基础配置。
"""

from .base import *


# 开发环境标识
DEBUG = True

# 允许的主机
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', 'testserver']

# 开发环境数据库配置（使用SQLite）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 开发环境缓存配置（使用本地内存）
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# 开发环境CORS配置
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 开发环境CSRF配置
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# 开发环境邮件配置（控制台输出）
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 开发环境日志配置
LOG_LEVEL = 'DEBUG'

# 开发工具
INSTALLED_APPS += [
    'debug_toolbar',      # Debug工具栏
    'django_extensions',  # Django扩展工具
]

# 开发环境中间件
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',  # Debug工具栏
]

# Debug工具栏配置
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# 开发环境静态文件配置
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# 开发环境媒体文件配置
MEDIA_ROOT = BASE_DIR / 'media'

# 开发环境安全配置（较宽松）
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = 'SAMEORIGIN'

# 开发环境Session配置
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# 开发环境Celery配置（同步执行）
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 开发环境API配置
API_DEBUG = True