"""
公共模型基类

该文件定义了系统中使用的公共模型基类。
遵循Django最佳实践和Google Python Style Guide。
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    """
    基础模型类

    包含所有模型的公共字段，如创建时间、更新时间等。
    所有业务模型都应该继承此类。
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
        db_comment='记录创建的时间戳'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
        db_comment='记录最后更新的时间戳'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

class SoftDeleteManager(models.Manager):
    """软删除管理器"""

    def get_queryset(self):
        """只返回未删除的记录"""
        return super().get_queryset().filter(is_deleted=False)

    def with_deleted(self):
        """返回包含已删除记录的查询集"""
        return super().get_queryset()

class SoftDeleteModel(BaseModel):
    """
    软删除模型基类

    支持软删除功能的基础模型。
    """

    is_deleted = models.BooleanField(
        default=False,
        verbose_name='是否删除',
        db_comment='软删除标记：1-已删除，0-未删除'
    )

    deleted_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='删除时间',
        db_comment='记录删除的时间戳'
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """软删除方法"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        """恢复删除的记录"""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])

# 通用选择类
class StatusChoices(models.TextChoices):
    """通用状态选择"""
    ACTIVE = 'active', _('激活')
    INACTIVE = 'inactive', _('未激活')
    PENDING = 'pending', _('待处理')

class VisibilityChoices(models.TextChoices):
    """可见性选择"""
    PUBLIC = 'public', _('公开')
    PRIVATE = 'private', _('私有')
    FAMILY = 'family', _('仅家族成员')

class GenderChoices(models.TextChoices):
    """性别选择"""
    MALE = 'male', _('男')
    FEMALE = 'female', _('女')
    UNKNOWN = 'unknown', _('未知')