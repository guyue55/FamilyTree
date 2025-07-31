import os
from celery import Celery
"""
族谱系统Celery配置

该文件包含了Celery异步任务队列的配置。
用于处理后台任务，如文件处理、邮件发送等。
"""

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# 创建Celery应用实例
app = Celery('familytree')

# 从Django设置中加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()

# 任务路由配置
app.conf.task_routes = {
    'apps.media.tasks.*': {'queue': 'media'},
    'apps.users.tasks.*': {'queue': 'users'},
    'apps.family.tasks.*': {'queue': 'family'},
}

# 任务优先级配置
app.conf.task_default_priority = 5
app.conf.worker_prefetch_multiplier = 1
app.conf.task_acks_late = True

# 结果过期时间
app.conf.result_expires = 3600  # 1小时

# 任务时间限制
app.conf.task_soft_time_limit = 300  # 5分钟软限制
app.conf.task_time_limit = 600  # 10分钟硬限制

# 调试任务
@app.task(bind=True)
def debug_task(self):
    """调试任务，用于测试Celery是否正常工作"""
    print(f'Request: {self.request!r}')