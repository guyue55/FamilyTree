"""
Kinship App Configuration
"""

from django.apps import AppConfig


class KinshipConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.kinship"
    verbose_name = "亲属关系计算"
