"""
媒体管理模块数据模型

该模块定义了家族媒体文件相关的数据模型，包括照片、视频、文档等。
遵循Django最佳实践和Google Python Style Guide。
"""

from django.db import models
from django.core.validators import MinLengthValidator
from apps.common.models import BaseModel, SoftDeleteModel, VisibilityChoices


class MediaFile(SoftDeleteModel):
    """
    媒体文件模型
    
    存储家族相关的媒体文件信息，包括照片、视频、文档等。
    """
    
    # 家族ID（逻辑关联）
    family_id = models.BigIntegerField(
        verbose_name='家族ID',
        help_text='所属家族ID，逻辑关联families.id',
        db_comment='所属家族ID，逻辑关联families.id'
    )
    
    # 上传者ID（逻辑关联）
    uploader_id = models.BigIntegerField(
        verbose_name='上传者ID',
        help_text='上传者的用户ID，逻辑关联users.id',
        db_comment='上传者的用户ID，逻辑关联users.id'
    )
    
    # 文件基础信息
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(1)],
        verbose_name='标题',
        help_text='媒体文件的标题',
        db_comment='媒体文件的标题'
    )
    
    description = models.TextField(
        max_length=1000,
        blank=True,
        verbose_name='描述',
        help_text='媒体文件的描述信息',
        db_comment='媒体文件的描述信息'
    )
    
    # 文件信息
    file = models.FileField(
        upload_to='family_media/%Y/%m/',
        verbose_name='文件',
        help_text='媒体文件',
        db_comment='媒体文件'
    )
    
    file_name = models.CharField(
        max_length=255,
        verbose_name='文件名',
        help_text='原始文件名',
        db_comment='原始文件名'
    )
    
    file_size = models.BigIntegerField(
        verbose_name='文件大小',
        help_text='文件大小（字节）',
        db_comment='文件大小（字节）'
    )
    
    file_type = models.CharField(
        max_length=20,
        choices=[
            ('image', '图片'),
            ('video', '视频'),
            ('audio', '音频'),
            ('document', '文档'),
            ('other', '其他'),
        ],
        verbose_name='文件类型',
        db_comment='文件类型'
    )
    
    mime_type = models.CharField(
        max_length=100,
        verbose_name='MIME类型',
        help_text='文件的MIME类型',
        db_comment='文件的MIME类型'
    )
    
    # 图片/视频特有属性
    width = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='宽度',
        help_text='图片或视频的宽度（像素）',
        db_comment='图片或视频的宽度（像素）'
    )
    
    height = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='高度',
        help_text='图片或视频的高度（像素）',
        db_comment='图片或视频的高度（像素）'
    )
    
    duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='时长',
        help_text='视频或音频的时长（秒）',
        db_comment='视频或音频的时长（秒）'
    )
    
    # 缩略图
    thumbnail = models.ImageField(
        upload_to='family_media/thumbnails/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='缩略图',
        help_text='媒体文件的缩略图',
        db_comment='媒体文件的缩略图'
    )
    
    # 标签和分类
    tags = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='标签',
        help_text='媒体文件的标签，用逗号分隔',
        db_comment='媒体文件的标签，用逗号分隔'
    )
    
    category = models.CharField(
        max_length=50,
        choices=[
            ('family_photo', '家庭照片'),
            ('portrait', '人物肖像'),
            ('event', '事件记录'),
            ('document', '文档资料'),
            ('genealogy', '族谱资料'),
            ('memorial', '纪念资料'),
            ('celebration', '庆祝活动'),
            ('daily_life', '日常生活'),
            ('other', '其他'),
        ],
        default='other',
        verbose_name='分类',
        db_comment='媒体文件的分类'
    )
    
    # 时间和地点信息
    taken_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='拍摄时间',
        help_text='照片或视频的拍摄时间',
        db_comment='照片或视频的拍摄时间'
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='拍摄地点',
        help_text='照片或视频的拍摄地点',
        db_comment='照片或视频的拍摄地点'
    )
    
    # GPS坐标
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
        verbose_name='纬度',
        db_comment='拍摄地点的纬度坐标'
    )
    
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
        verbose_name='经度',
        db_comment='拍摄地点的经度坐标'
    )
    
    # 可见性和权限
    visibility = models.CharField(
        max_length=20,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.FAMILY,
        verbose_name='可见性',
        db_comment='媒体文件的可见性设置'
    )
    
    is_featured = models.BooleanField(
        default=False,
        verbose_name='是否精选',
        help_text='是否为精选媒体文件',
        db_comment='是否为精选媒体文件'
    )
    
    # 统计信息
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='查看次数',
        db_comment='媒体文件的查看次数'
    )
    
    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name='下载次数',
        db_comment='媒体文件的下载次数'
    )
    
    # 处理状态
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '待处理'),
            ('processing', '处理中'),
            ('completed', '已完成'),
            ('failed', '处理失败'),
        ],
        default='pending',
        verbose_name='处理状态',
        help_text='媒体文件的处理状态',
        db_comment='媒体文件的处理状态'
    )
    
    class Meta:
        db_table = 'family_media_files'
        verbose_name = '媒体文件'
        verbose_name_plural = '媒体文件'
        indexes = [
            models.Index(fields=['family_id']),
            models.Index(fields=['uploader_id']),
            models.Index(fields=['file_type']),
            models.Index(fields=['category']),
            models.Index(fields=['taken_date']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['processing_status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-taken_date', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_tags_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags_list(self, tags_list):
        """设置标签列表"""
        self.tags = ','.join(tags_list) if tags_list else ''
    
    def increment_view_count(self):
        """增加查看次数"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_download_count(self):
        """增加下载次数"""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def get_file_size_display(self):
        """获取文件大小的友好显示"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class MediaMemberTag(BaseModel):
    """
    媒体文件成员标记模型
    
    记录媒体文件中标记的家族成员。
    """
    
    # 媒体文件ID（逻辑关联）
    media_id = models.BigIntegerField(
        verbose_name='媒体文件ID',
        help_text='媒体文件ID，逻辑关联family_media_files.id',
        db_comment='媒体文件ID，逻辑关联family_media_files.id'
    )
    
    # 成员ID（逻辑关联）
    member_id = models.BigIntegerField(
        verbose_name='成员ID',
        help_text='被标记的成员ID，逻辑关联family_members.id',
        db_comment='被标记的成员ID，逻辑关联family_members.id'
    )
    
    # 标记者ID（逻辑关联）
    tagger_id = models.BigIntegerField(
        verbose_name='标记者ID',
        help_text='标记者的用户ID，逻辑关联users.id',
        db_comment='标记者的用户ID，逻辑关联users.id'
    )
    
    # 标记位置（用于图片中的人脸标记）
    x_coordinate = models.FloatField(
        blank=True,
        null=True,
        verbose_name='X坐标',
        help_text='标记在图片中的X坐标（百分比）',
        db_comment='标记在图片中的X坐标（百分比）'
    )
    
    y_coordinate = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Y坐标',
        help_text='标记在图片中的Y坐标（百分比）',
        db_comment='标记在图片中的Y坐标（百分比）'
    )
    
    width = models.FloatField(
        blank=True,
        null=True,
        verbose_name='标记宽度',
        help_text='标记区域的宽度（百分比）',
        db_comment='标记区域的宽度（百分比）'
    )
    
    height = models.FloatField(
        blank=True,
        null=True,
        verbose_name='标记高度',
        help_text='标记区域的高度（百分比）',
        db_comment='标记区域的高度（百分比）'
    )
    
    # 标记确认状态
    is_confirmed = models.BooleanField(
        default=False,
        verbose_name='是否确认',
        help_text='标记是否已被相关成员确认',
        db_comment='标记是否已被相关成员确认'
    )
    
    # 确认者ID
    confirmed_by_id = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name='确认者ID',
        help_text='确认标记的用户ID，逻辑关联users.id',
        db_comment='确认标记的用户ID，逻辑关联users.id'
    )
    
    # 确认时间
    confirmed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='确认时间',
        db_comment='标记确认的时间'
    )
    
    class Meta:
        db_table = 'media_member_tags'
        verbose_name = '媒体成员标记'
        verbose_name_plural = '媒体成员标记'
        indexes = [
            models.Index(fields=['media_id']),
            models.Index(fields=['member_id']),
            models.Index(fields=['tagger_id']),
            models.Index(fields=['is_confirmed']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [
            ('media_id', 'member_id'),  # 同一媒体文件中同一成员只能被标记一次
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"媒体{self.media_id}中的成员{self.member_id}标记"
    
    def confirm_tag(self, confirmed_by_id):
        """确认标记"""
        from django.utils import timezone
        self.is_confirmed = True
        self.confirmed_by_id = confirmed_by_id
        self.confirmed_at = timezone.now()
        self.save(update_fields=['is_confirmed', 'confirmed_by_id', 'confirmed_at'])


class MediaAlbum(SoftDeleteModel):
    """
    媒体相册模型
    
    用于组织和管理媒体文件的相册。
    """
    
    # 家族ID（逻辑关联）
    family_id = models.BigIntegerField(
        verbose_name='家族ID',
        help_text='所属家族ID，逻辑关联families.id',
        db_comment='所属家族ID，逻辑关联families.id'
    )
    
    # 创建者ID（逻辑关联）
    creator_id = models.BigIntegerField(
        verbose_name='创建者ID',
        help_text='相册创建者的用户ID，逻辑关联users.id',
        db_comment='相册创建者的用户ID，逻辑关联users.id'
    )
    
    # 相册基础信息
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(1)],
        verbose_name='相册名称',
        db_comment='相册名称'
    )
    
    description = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='相册描述',
        db_comment='相册描述'
    )
    
    # 相册封面
    cover_image = models.ImageField(
        upload_to='family_albums/covers/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='封面图片',
        db_comment='封面图片'
    )
    
    # 相册类型
    album_type = models.CharField(
        max_length=20,
        choices=[
            ('general', '通用相册'),
            ('event', '事件相册'),
            ('person', '个人相册'),
            ('year', '年度相册'),
            ('generation', '世代相册'),
            ('memorial', '纪念相册'),
        ],
        default='general',
        verbose_name='相册类型',
        db_comment='相册类型：general-通用相册，event-事件相册，person-个人相册，year-年度相册，generation-世代相册，memorial-纪念相册'
    )
    
    # 相册标签
    tags = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='标签',
        help_text='相册标签，用逗号分隔',
        db_comment='相册标签，用逗号分隔'
    )
    
    # 时间范围
    start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='开始日期',
        help_text='相册内容的开始日期',
        db_comment='相册内容的开始日期'
    )
    
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='结束日期',
        help_text='相册内容的结束日期',
        db_comment='相册内容的结束日期'
    )
    
    # 可见性设置
    visibility = models.CharField(
        max_length=20,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.FAMILY,
        verbose_name='可见性',
        db_comment='可见性：public-公开，family-家族内，private-私有'
    )
    
    # 统计信息
    media_count = models.PositiveIntegerField(
        default=0,
        verbose_name='媒体数量',
        help_text='相册中的媒体文件数量',
        db_comment='相册中的媒体文件数量'
    )
    
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='查看次数',
        db_comment='查看次数'
    )
    
    # 排序权重
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name='排序权重',
        help_text='相册的排序权重，数值越大越靠前',
        db_comment='相册的排序权重，数值越大越靠前'
    )
    
    class Meta:
        db_table = 'family_media_albums'
        verbose_name = '媒体相册'
        verbose_name_plural = '媒体相册'
        indexes = [
            models.Index(fields=['family_id']),
            models.Index(fields=['creator_id']),
            models.Index(fields=['album_type']),
            models.Index(fields=['start_date']),
            models.Index(fields=['sort_order']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-sort_order', '-created_at']
    
    def __str__(self):
        return self.name
    
    def get_tags_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags_list(self, tags_list):
        """设置标签列表"""
        self.tags = ','.join(tags_list) if tags_list else ''
    
    def increment_view_count(self):
        """增加查看次数"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def update_media_count(self):
        """更新媒体数量"""
        count = MediaAlbumItem.objects.filter(album_id=self.id).count()
        self.media_count = count
        self.save(update_fields=['media_count'])


class MediaAlbumItem(BaseModel):
    """
    相册媒体项模型
    
    记录相册中包含的媒体文件。
    """
    
    # 相册ID（逻辑关联）
    album_id = models.BigIntegerField(
        verbose_name='相册ID',
        help_text='相册ID，逻辑关联family_media_albums.id',
        db_comment='相册ID，逻辑关联family_media_albums.id'
    )
    
    # 媒体文件ID（逻辑关联）
    media_id = models.BigIntegerField(
        verbose_name='媒体文件ID',
        help_text='媒体文件ID，逻辑关联family_media_files.id',
        db_comment='媒体文件ID，逻辑关联family_media_files.id'
    )
    
    # 添加者ID（逻辑关联）
    added_by_id = models.BigIntegerField(
        verbose_name='添加者ID',
        help_text='添加者的用户ID，逻辑关联users.id',
        db_comment='添加者的用户ID，逻辑关联users.id'
    )
    
    # 在相册中的排序
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name='排序序号',
        help_text='在相册中的排序序号',
        db_comment='在相册中的排序序号'
    )
    
    # 在相册中的描述
    caption = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='说明',
        help_text='媒体在相册中的说明文字',
        db_comment='媒体在相册中的说明文字'
    )
    
    class Meta:
        db_table = 'media_album_items'
        verbose_name = '相册媒体项'
        verbose_name_plural = '相册媒体项'
        indexes = [
            models.Index(fields=['album_id']),
            models.Index(fields=['media_id']),
            models.Index(fields=['sort_order']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [
            ('album_id', 'media_id'),  # 同一媒体文件在同一相册中只能出现一次
        ]
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f"相册{self.album_id}中的媒体{self.media_id}"


class MediaComment(BaseModel):
    """
    媒体评论模型
    
    记录用户对媒体文件的评论。
    """
    
    # 媒体文件ID（逻辑关联）
    media_id = models.BigIntegerField(
        verbose_name='媒体文件ID',
        help_text='媒体文件ID，逻辑关联family_media_files.id',
        db_comment='媒体文件ID，逻辑关联family_media_files.id'
    )
    
    # 评论者ID（逻辑关联）
    commenter_id = models.BigIntegerField(
        verbose_name='评论者ID',
        help_text='评论者的用户ID，逻辑关联users.id',
        db_comment='评论者的用户ID，逻辑关联users.id'
    )
    
    # 父评论ID（用于回复）
    parent_comment_id = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name='父评论ID',
        help_text='父评论ID，用于回复功能',
        db_comment='父评论ID，用于回复功能'
    )
    
    # 评论内容
    content = models.TextField(
        max_length=1000,
        verbose_name='评论内容',
        db_comment='评论内容'
    )
    
    # 评论状态
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', '正常'),
            ('hidden', '隐藏'),
            ('deleted', '已删除'),
        ],
        default='active',
        verbose_name='状态',
        db_comment='状态：active-正常，hidden-隐藏，deleted-已删除'
    )
    
    # 点赞数
    like_count = models.PositiveIntegerField(
        default=0,
        verbose_name='点赞数',
        db_comment='点赞数'
    )
    
    class Meta:
        db_table = 'media_comments'
        verbose_name = '媒体评论'
        verbose_name_plural = '媒体评论'
        indexes = [
            models.Index(fields=['media_id']),
            models.Index(fields=['commenter_id']),
            models.Index(fields=['parent_comment_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"媒体{self.media_id}的评论"
    
    def increment_like_count(self):
        """增加点赞数"""
        self.like_count += 1
        self.save(update_fields=['like_count'])
    
    def decrement_like_count(self):
        """减少点赞数"""
        if self.like_count > 0:
            self.like_count -= 1
            self.save(update_fields=['like_count'])