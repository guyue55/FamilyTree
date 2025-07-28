"""项目主URL配置

该模块定义了项目的主要URL路由配置，包括API路由和管理后台路由。
使用Django Ninja框架提供RESTful API服务，遵循API设计文档规范。
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .api_v1 import api_v1


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api_v1.urls),
]

# 开发环境下提供静态文件服务和调试工具
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # 添加Django Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls, namespace='djdt')),
        ] + urlpatterns