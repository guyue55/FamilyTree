"""
族谱系统WSGI配置

该文件包含了WSGI应用的配置，用于部署到生产环境。
遵循Django最佳实践和PEP 3333 WSGI规范。
"""

import os
from django.core.wsgi import get_wsgi_application

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# 获取WSGI应用
application = get_wsgi_application()