"""
Django测试环境配置文件

该文件包含了测试环境特有的配置项。
继承自base.py的基础配置。
"""

from .base import *

# 测试环境标识
DEBUG = False

# 测试环境主机配置
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# 测试环境数据库配置（内存SQLite）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 测试环境缓存配置（本地内存）
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}

# 测试环境密码验证（简化）
AUTH_PASSWORD_VALIDATORS = []

# 测试环境邮件配置（内存后端）
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 测试环境日志配置（静默）
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': False,
        },
        'apps': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
}

# 测试环境静态文件配置
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# 测试环境媒体文件配置
MEDIA_ROOT = '/tmp/familytree_test_media'

# 测试环境安全配置（宽松）
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = 'SAMEORIGIN'

# 测试环境Session配置
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# 测试环境Celery配置（同步执行）
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 测试环境CORS配置
CORS_ALLOW_ALL_ORIGINS = True

# 测试环境API配置
API_DEBUG = True

# 测试环境性能优化
MIGRATION_MODULES = {
    'users': None,
    'family': None,
    'members': None,
    'relationships': None,
    'media': None,
    'common': None,
}

# 禁用迁移以加速测试
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

# 在测试时禁用迁移
import sys
if 'test' in sys.argv:
    MIGRATION_MODULES = DisableMigrations()

# 测试数据库配置优化
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        }
    }

# 测试环境JWT配置（短期有效）
JWT_ACCESS_TOKEN_LIFETIME = 300  # 5分钟
JWT_REFRESH_TOKEN_LIFETIME = 600  # 10分钟