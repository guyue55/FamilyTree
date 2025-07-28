"""
Family应用常量定义

定义家族应用中使用的所有常量，包括选择项、配置参数等。
遵循Django最佳实践和Google Python Style Guide。
"""

from typing import List, Tuple


# ==================== 家族相关常量 ====================

# 家族可见性选择
FAMILY_VISIBILITY_CHOICES = [
    ('public', '公开'),
    ('protected', '受保护'),
    ('private', '私有'),
]

# 家族状态选择
FAMILY_STATUS_CHOICES = [
    ('active', '活跃'),
    ('inactive', '不活跃'),
    ('archived', '已归档'),
]

# 家族标签限制
MAX_FAMILY_TAGS = 10
MAX_TAG_LENGTH = 20
MAX_FAMILY_NAME_LENGTH = 100
MAX_FAMILY_DESCRIPTION_LENGTH = 1000

# 家族成员数量限制
MAX_FAMILY_MEMBERS = 1000
DEFAULT_MEMBER_COUNT = 1

# 家族世代数量限制
MAX_GENERATIONS = 20
DEFAULT_GENERATIONS = 5


# ==================== 家族设置相关常量 ====================

# 族谱布局选择
TREE_LAYOUT_CHOICES = [
    ('horizontal', '水平布局'),
    ('vertical', '垂直布局'),
    ('circular', '圆形布局'),
    ('fan', '扇形布局'),
]

# 主题选择
THEME_CHOICES = [
    ('default', '默认主题'),
    ('classic', '经典主题'),
    ('modern', '现代主题'),
    ('elegant', '优雅主题'),
    ('nature', '自然主题'),
]

# 主题颜色选择
THEME_COLOR_CHOICES = [
    ('#1890ff', '蓝色'),
    ('#52c41a', '绿色'),
    ('#fa8c16', '橙色'),
    ('#eb2f96', '粉色'),
    ('#722ed1', '紫色'),
    ('#13c2c2', '青色'),
    ('#f5222d', '红色'),
]

# 字体大小选择
FONT_SIZE_CHOICES = [
    ('small', '小'),
    ('medium', '中'),
    ('large', '大'),
    ('extra-large', '特大'),
]

# 字体系列选择
FONT_FAMILY_CHOICES = [
    ('system', '系统默认'),
    ('serif', '衬线字体'),
    ('sans-serif', '无衬线字体'),
    ('monospace', '等宽字体'),
]

# 隐私级别选择
PRIVACY_LEVEL_CHOICES = [
    ('public', '完全公开'),
    ('members', '仅成员可见'),
    ('family', '仅家族可见'),
    ('private', '完全私有'),
]

# 默认设置值
DEFAULT_FAMILY_SETTINGS = {
    'tree_layout': 'horizontal',
    'default_generations': 5,
    'show_photos': True,
    'show_birth_dates': True,
    'show_death_dates': True,
    'show_occupation': True,
    'theme': 'default',
    'theme_color': '#1890ff',
    'font_size': 'medium',
    'font_family': 'system',
    'privacy_level': 'members',
    'require_approval': True,
    'allow_member_invite': True,
    'enable_notifications': True,
    'email_notifications': True,
    'push_notifications': True,
    'notify_new_member': True,
    'notify_tree_update': True,
}


# ==================== 邀请相关常量 ====================

# 邀请状态选择
INVITATION_STATUS_CHOICES = [
    ('pending', '待处理'),
    ('accepted', '已接受'),
    ('rejected', '已拒绝'),
    ('expired', '已过期'),
    ('cancelled', '已取消'),
]

# 邀请过期时间（天）
DEFAULT_INVITATION_EXPIRES_DAYS = 7
MAX_INVITATION_EXPIRES_DAYS = 30

# 邀请消息长度限制
MAX_INVITATION_MESSAGE_LENGTH = 500

# 邀请码长度
INVITATION_CODE_LENGTH = 32

# 每个家族同时待处理邀请数量限制
MAX_PENDING_INVITATIONS_PER_FAMILY = 50

# 每个用户每天可发送的邀请数量限制
MAX_INVITATIONS_PER_USER_PER_DAY = 10


# ==================== 权限相关常量 ====================

# 家族角色权重（用于权限比较）
ROLE_WEIGHTS = {
    'owner': 100,
    'admin': 80,
    'moderator': 60,
    'member': 40,
    'guest': 20,
}

# 默认角色权限映射
DEFAULT_ROLE_PERMISSIONS = {
    'owner': [
        'manage_family', 'delete_family', 'manage_settings',
        'invite_members', 'remove_members', 'manage_roles',
        'approve_members', 'manage_tree', 'add_members',
        'edit_members', 'delete_members', 'manage_relationships',
        'upload_media', 'manage_media', 'view_family',
        'view_tree', 'view_members'
    ],
    'admin': [
        'manage_family', 'manage_settings', 'invite_members',
        'remove_members', 'approve_members', 'manage_tree',
        'add_members', 'edit_members', 'delete_members',
        'manage_relationships', 'upload_media', 'manage_media',
        'view_family', 'view_tree', 'view_members'
    ],
    'moderator': [
        'invite_members', 'approve_members', 'add_members',
        'edit_members', 'manage_relationships', 'upload_media',
        'view_family', 'view_tree', 'view_members'
    ],
    'member': [
        'upload_media', 'view_family', 'view_tree', 'view_members'
    ],
    'guest': [
        'view_family', 'view_tree'
    ]
}


# ==================== 缓存相关常量 ====================

# 缓存键前缀
CACHE_KEY_PREFIX = 'family'

# 缓存过期时间（秒）
CACHE_TIMEOUT = {
    'family_detail': 1800,      # 30分钟
    'family_list': 900,         # 15分钟
    'family_settings': 3600,    # 1小时
    'family_permissions': 1800, # 30分钟
    'family_statistics': 1800,  # 30分钟
    'global_statistics': 3600,  # 1小时
}

# 缓存键模板
CACHE_KEYS = {
    'family_detail': f'{CACHE_KEY_PREFIX}_detail_{{family_id}}',
    'family_list': f'{CACHE_KEY_PREFIX}_list_user_{{user_id}}',
    'family_settings': f'{CACHE_KEY_PREFIX}_settings_{{family_id}}',
    'family_permissions': f'{CACHE_KEY_PREFIX}_permissions_{{family_id}}_{{user_id}}',
    'family_statistics': f'{CACHE_KEY_PREFIX}_statistics_{{family_id}}',
    'global_statistics': f'{CACHE_KEY_PREFIX}_global_statistics',
    'user_invitations': f'{CACHE_KEY_PREFIX}_invitations_user_{{user_id}}',
}

# 详细缓存键配置（从config.py合并）
class CacheKeys:
    """缓存键常量类"""
    
    # 家族相关缓存键
    FAMILY_DETAIL = 'family:detail:{}'
    FAMILY_LIST = 'family:list:{}'
    FAMILY_MEMBERS = 'family:members:{}'
    FAMILY_INVITATIONS = 'family:invitations:{}'
    FAMILY_SETTINGS = 'family:settings:{}'
    FAMILY_STATISTICS = 'family:stats:{}'
    FAMILY_PERMISSIONS = 'family:permissions:{}:{}'
    
    # 用户相关缓存键
    USER_FAMILIES = 'user:families:{}'
    USER_FAMILY_ROLES = 'user:family_roles:{}'
    USER_FAMILY_PERMISSIONS = 'user:family_permissions:{}:{}'
    
    # 搜索相关缓存键
    FAMILY_SEARCH = 'family:search:{}'
    POPULAR_FAMILIES = 'families:popular'
    RECENT_FAMILIES = 'families:recent'
    FAMILY_TAGS = 'families:tags'
    
    # 统计相关缓存键
    FAMILY_COUNT = 'families:count'
    MEMBER_COUNT = 'families:member_count'
    INVITATION_COUNT = 'families:invitation_count'


# ==================== 队列相关常量 ====================

# 队列名称
class QueueNames:
    """队列名称常量"""
    
    # 家族相关队列
    FAMILY_OPERATIONS = 'family_operations'
    FAMILY_NOTIFICATIONS = 'family_notifications'
    FAMILY_STATISTICS = 'family_statistics'
    FAMILY_CLEANUP = 'family_cleanup'
    FAMILY_BACKUP = 'family_backup'
    FAMILY_EXPORT = 'family_export'
    FAMILY_IMPORT = 'family_import'
    
    # 邮件队列
    EMAIL_INVITATIONS = 'email_invitations'
    EMAIL_NOTIFICATIONS = 'email_notifications'
    
    # 文件处理队列
    FILE_PROCESSING = 'file_processing'
    IMAGE_PROCESSING = 'image_processing'


# ==================== 错误代码常量 ====================

class ErrorCodes:
    """错误代码常量"""
    
    # 通用错误 (1000-1099)
    INVALID_REQUEST = 'FAMILY_1001'
    PERMISSION_DENIED = 'FAMILY_1002'
    NOT_FOUND = 'FAMILY_1003'
    VALIDATION_ERROR = 'FAMILY_1004'
    RATE_LIMIT_EXCEEDED = 'FAMILY_1005'
    
    # 家族错误 (1100-1199)
    FAMILY_NOT_FOUND = 'FAMILY_1101'
    FAMILY_ACCESS_DENIED = 'FAMILY_1102'
    FAMILY_ALREADY_EXISTS = 'FAMILY_1103'
    FAMILY_LIMIT_EXCEEDED = 'FAMILY_1104'
    FAMILY_NAME_TAKEN = 'FAMILY_1105'
    FAMILY_SLUG_TAKEN = 'FAMILY_1106'
    
    # 成员错误 (1200-1299)
    MEMBER_NOT_FOUND = 'FAMILY_1201'
    MEMBER_ALREADY_EXISTS = 'FAMILY_1202'
    MEMBER_LIMIT_EXCEEDED = 'FAMILY_1203'
    INSUFFICIENT_ROLE = 'FAMILY_1204'
    CANNOT_REMOVE_OWNER = 'FAMILY_1205'
    CANNOT_CHANGE_OWNER_ROLE = 'FAMILY_1206'
    
    # 邀请错误 (1300-1399)
    INVITATION_NOT_FOUND = 'FAMILY_1301'
    INVITATION_EXPIRED = 'FAMILY_1302'
    INVITATION_ALREADY_SENT = 'FAMILY_1303'
    INVITATION_LIMIT_EXCEEDED = 'FAMILY_1304'
    INVITATION_ALREADY_ACCEPTED = 'FAMILY_1305'
    INVITATION_ALREADY_REJECTED = 'FAMILY_1306'
    
    # 文件错误 (1400-1499)
    FILE_TOO_LARGE = 'FAMILY_1401'
    INVALID_FILE_FORMAT = 'FAMILY_1402'
    UPLOAD_FAILED = 'FAMILY_1403'
    FILE_NOT_FOUND = 'FAMILY_1404'
    
    # 系统错误 (1500-1599)
    DATABASE_ERROR = 'FAMILY_1501'
    CACHE_ERROR = 'FAMILY_1502'
    QUEUE_ERROR = 'FAMILY_1503'
    EMAIL_ERROR = 'FAMILY_1504'
    EXTERNAL_SERVICE_ERROR = 'FAMILY_1505'


# ==================== 文件上传相关常量 ====================

# 允许的图片格式
ALLOWED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'webp']

# 图片大小限制（字节）
MAX_AVATAR_SIZE = 2 * 1024 * 1024      # 2MB
MAX_COVER_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# 图片尺寸限制
MAX_AVATAR_DIMENSIONS = (500, 500)
MAX_COVER_DIMENSIONS = (1920, 1080)

# 上传路径模板
UPLOAD_PATHS = {
    'family_avatar': 'families/{family_id}/avatar/',
    'family_cover': 'families/{family_id}/cover/',
    'family_media': 'families/{family_id}/media/{year}/{month}/',
}


# ==================== 通知相关常量 ====================

# 通知类型
NOTIFICATION_TYPES = [
    ('invitation_received', '收到邀请'),
    ('invitation_accepted', '邀请被接受'),
    ('invitation_rejected', '邀请被拒绝'),
    ('member_joined', '新成员加入'),
    ('member_left', '成员离开'),
    ('tree_updated', '族谱更新'),
    ('settings_changed', '设置变更'),
]

# 通知优先级
NOTIFICATION_PRIORITY = {
    'low': 1,
    'normal': 2,
    'high': 3,
    'urgent': 4,
}

# 默认通知设置
DEFAULT_NOTIFICATION_SETTINGS = {
    'email_notifications': True,
    'push_notifications': True,
    'sms_notifications': False,
    'notify_new_member': True,
    'notify_tree_update': True,
    'notify_invitation': True,
    'notify_settings_change': False,
}


# ==================== API相关常量 ====================

# 注意：分页相关常量已移至 apps.common.constants.PaginationDefaults
# 请使用 from apps.common.constants import PaginationDefaults

# 搜索相关
MIN_SEARCH_LENGTH = 2
MAX_SEARCH_LENGTH = 100

# 排序选项
SORT_OPTIONS = [
    ('created_at', '创建时间'),
    ('-created_at', '创建时间倒序'),
    ('name', '名称'),
    ('-name', '名称倒序'),
    ('member_count', '成员数量'),
    ('-member_count', '成员数量倒序'),
    ('updated_at', '更新时间'),
    ('-updated_at', '更新时间倒序'),
]

# 过滤选项
FILTER_OPTIONS = {
    'visibility': FAMILY_VISIBILITY_CHOICES,
    'status': INVITATION_STATUS_CHOICES,
    'layout': TREE_LAYOUT_CHOICES,
    'theme': THEME_CHOICES,
}


# ==================== 错误消息常量 ====================

ERROR_MESSAGES = {
    'family_not_found': '家族不存在',
    'family_name_exists': '家族名称已存在',
    'permission_denied': '权限不足',
    'invitation_not_found': '邀请不存在',
    'invitation_expired': '邀请已过期',
    'invitation_already_processed': '邀请已处理',
    'max_members_reached': '家族成员数量已达上限',
    'max_invitations_reached': '待处理邀请数量已达上限',
    'invalid_invitation_code': '无效的邀请码',
    'user_already_member': '用户已是家族成员',
    'settings_not_found': '家族设置不存在',
    'invalid_file_format': '不支持的文件格式',
    'file_too_large': '文件大小超出限制',
}


# ==================== 成功消息常量 ====================

SUCCESS_MESSAGES = {
    'family_created': '家族创建成功',
    'family_updated': '家族信息更新成功',
    'family_deleted': '家族删除成功',
    'invitation_sent': '邀请发送成功',
    'invitation_accepted': '邀请接受成功',
    'invitation_rejected': '邀请拒绝成功',
    'settings_updated': '设置更新成功',
    'member_added': '成员添加成功',
    'member_removed': '成员移除成功',
    'file_uploaded': '文件上传成功',
}


# ==================== 辅助函数 ====================

def get_choice_display(choices: List[Tuple[str, str]], value: str) -> str:
    """
    获取选择项的显示文本
    
    Args:
        choices: 选择项列表
        value: 选择值
        
    Returns:
        str: 显示文本
    """
    for choice_value, choice_display in choices:
        if choice_value == value:
            return choice_display
    return value


def validate_choice(choices: List[Tuple[str, str]], value: str) -> bool:
    """
    验证选择项是否有效
    
    Args:
        choices: 选择项列表
        value: 选择值
        
    Returns:
        bool: 是否有效
    """
    return value in [choice[0] for choice in choices]


def get_cache_key(template: str, **kwargs) -> str:
    """
    生成缓存键
    
    Args:
        template: 缓存键模板
        **kwargs: 模板参数
        
    Returns:
        str: 缓存键
    """
    return template.format(**kwargs)