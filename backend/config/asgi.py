import os
from django.core.asgi import get_asgi_application
"""
族谱系统ASGI配置

该文件包含了ASGI应用的配置，用于支持异步功能和WebSocket。
遵循Django最佳实践和ASGI规范。
"""

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# 获取ASGI应用
application = get_asgi_application()