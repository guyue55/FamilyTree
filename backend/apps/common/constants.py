from typing import Dict
"""
通用常量定义

定义项目中使用的所有常量，包括错误码、状态码、配置项等。
遵循Django最佳实践和Google Python Style Guide。
"""

class HttpStatusCode:
    """HTTP状态码常量"""

    # 成功状态码
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    # 客户端错误状态码
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429

    # 服务器错误状态码
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504

class ApiErrorCode:
    """API错误码定义"""

    # 系统错误 (1000-1999)
    SYSTEM_ERROR = "1000"
    INTERNAL_SERVER_ERROR = "1000"  # 别名，与SYSTEM_ERROR相同
    PARAMETER_ERROR = "1001"
    VALIDATION_ERROR = "1002"
    RATE_LIMIT_ERROR = "1003"
    MAINTENANCE_ERROR = "1004"
    SERVICE_UNAVAILABLE = "1005"
    NOT_FOUND = "1006"
    FORBIDDEN = "1007"
    DATA_NOT_FOUND = "1008"
    DATA_CONFLICT = "1009"

    # 认证授权错误 (2000-2999)
    AUTHENTICATION_FAILED = "2000"
    TOKEN_INVALID = "2001"
    TOKEN_EXPIRED = "2002"
    PERMISSION_DENIED = "2003"
    USER_NOT_FOUND = "2004"
    USER_ALREADY_EXISTS = "2005"
    PASSWORD_INCORRECT = "2006"
    ACCOUNT_DISABLED = "2007"
    ACCOUNT_LOCKED = "2008"

    # 家族相关错误 (3000-3999)
    FAMILY_NOT_FOUND = "3000"
    FAMILY_PERMISSION_DENIED = "3001"
    FAMILY_ALREADY_EXISTS = "3002"
    FAMILY_MEMBER_EXISTS = "3003"
    FAMILY_MEMBER_NOT_FOUND = "3004"
    FAMILY_INVITATION_NOT_FOUND = "3005"
    FAMILY_INVITATION_EXPIRED = "3006"
    FAMILY_INVITATION_ALREADY_PROCESSED = "3007"
    FAMILY_LIMIT_EXCEEDED = "3008"

    # 成员相关错误 (4000-4999)
    MEMBER_NOT_FOUND = "4000"
    MEMBER_PERMISSION_DENIED = "4001"
    MEMBER_ALREADY_EXISTS = "4002"
    MEMBER_RELATIONSHIP_INVALID = "4003"
    MEMBER_LIMIT_EXCEEDED = "4004"

    # 关系相关错误 (5000-5999)
    RELATIONSHIP_NOT_FOUND = "5000"
    RELATIONSHIP_INVALID = "5001"
    RELATIONSHIP_ALREADY_EXISTS = "5002"
    RELATIONSHIP_CIRCULAR_REFERENCE = "5003"

    # 媒体文件错误 (6000-6999)
    FILE_NOT_FOUND = "6000"
    FILE_FORMAT_UNSUPPORTED = "6001"
    FILE_SIZE_EXCEEDED = "6002"
    FILE_UPLOAD_FAILED = "6003"
    FILE_PERMISSION_DENIED = "6004"

    # 数据相关错误 (7000-7999)
    DATA_NOT_FOUND = "7000"
    DATA_INVALID = "7001"
    DATA_CONFLICT = "7002"
    DATA_CORRUPTED = "7003"

class ApiErrorMessage:
    """API错误消息定义"""

    ERROR_MESSAGES: Dict[str, str] = {
        # 系统错误
        ApiErrorCode.SYSTEM_ERROR: "系统内部错误",
        ApiErrorCode.PARAMETER_ERROR: "请求参数错误",
        ApiErrorCode.VALIDATION_ERROR: "数据验证失败",
        ApiErrorCode.RATE_LIMIT_ERROR: "请求频率过高，请稍后再试",
        ApiErrorCode.MAINTENANCE_ERROR: "系统维护中，请稍后再试",
        ApiErrorCode.SERVICE_UNAVAILABLE: "服务暂时不可用",
        ApiErrorCode.NOT_FOUND: "资源不存在",
        ApiErrorCode.FORBIDDEN: "访问被禁止",
        ApiErrorCode.DATA_NOT_FOUND: "数据不存在",
        ApiErrorCode.DATA_CONFLICT: "数据冲突",

        # 认证授权错误
        ApiErrorCode.AUTHENTICATION_FAILED: "身份认证失败",
        ApiErrorCode.TOKEN_INVALID: "访问令牌无效",
        ApiErrorCode.TOKEN_EXPIRED: "访问令牌已过期",
        ApiErrorCode.PERMISSION_DENIED: "权限不足",
        ApiErrorCode.USER_NOT_FOUND: "用户不存在",
        ApiErrorCode.USER_ALREADY_EXISTS: "用户已存在",
        ApiErrorCode.PASSWORD_INCORRECT: "密码错误",
        ApiErrorCode.ACCOUNT_DISABLED: "账户已被禁用",
        ApiErrorCode.ACCOUNT_LOCKED: "账户已被锁定",

        # 家族相关错误
        ApiErrorCode.FAMILY_NOT_FOUND: "家族不存在",
        ApiErrorCode.FAMILY_PERMISSION_DENIED: "无权限访问该家族",
        ApiErrorCode.FAMILY_ALREADY_EXISTS: "家族已存在",
        ApiErrorCode.FAMILY_MEMBER_EXISTS: "已是家族成员",
        ApiErrorCode.FAMILY_MEMBER_NOT_FOUND: "家族成员不存在",
        ApiErrorCode.FAMILY_INVITATION_NOT_FOUND: "家族邀请不存在",
        ApiErrorCode.FAMILY_INVITATION_EXPIRED: "家族邀请已过期",
        ApiErrorCode.FAMILY_INVITATION_ALREADY_PROCESSED: "家族邀请已处理",
        ApiErrorCode.FAMILY_LIMIT_EXCEEDED: "家族数量已达上限",

        # 成员相关错误
        ApiErrorCode.MEMBER_NOT_FOUND: "成员不存在",
        ApiErrorCode.MEMBER_PERMISSION_DENIED: "无权限操作该成员",
        ApiErrorCode.MEMBER_ALREADY_EXISTS: "成员已存在",
        ApiErrorCode.MEMBER_RELATIONSHIP_INVALID: "成员关系无效",
        ApiErrorCode.MEMBER_LIMIT_EXCEEDED: "成员数量已达上限",

        # 关系相关错误
        ApiErrorCode.RELATIONSHIP_NOT_FOUND: "关系不存在",
        ApiErrorCode.RELATIONSHIP_INVALID: "关系无效",
        ApiErrorCode.RELATIONSHIP_ALREADY_EXISTS: "关系已存在",
        ApiErrorCode.RELATIONSHIP_CIRCULAR_REFERENCE: "存在循环引用",

        # 媒体文件错误
        ApiErrorCode.FILE_NOT_FOUND: "文件不存在",
        ApiErrorCode.FILE_FORMAT_UNSUPPORTED: "文件格式不支持",
        ApiErrorCode.FILE_SIZE_EXCEEDED: "文件大小超出限制",
        ApiErrorCode.FILE_UPLOAD_FAILED: "文件上传失败",
        ApiErrorCode.FILE_PERMISSION_DENIED: "无权限访问文件",

        # 数据相关错误
        ApiErrorCode.DATA_NOT_FOUND: "数据不存在",
        ApiErrorCode.DATA_INVALID: "数据无效",
        ApiErrorCode.DATA_CONFLICT: "数据冲突",
        ApiErrorCode.DATA_CORRUPTED: "数据损坏",
    }

    @classmethod
    def get_message(cls, error_code: str) -> str:
        """获取错误消息"""
        return cls.ERROR_MESSAGES.get(error_code, "未知错误")

class PaginationDefaults:
    """分页默认配置"""

    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    MIN_PAGE_SIZE = 1

class CacheTimeout:
    """缓存超时时间配置（秒）"""

    SHORT = 300      # 5分钟
    MEDIUM = 1800    # 30分钟
    LONG = 3600      # 1小时
    VERY_LONG = 86400  # 24小时

class RateLimitDefaults:
    """限流默认配置"""

    # 每分钟请求次数限制
    USER_RATE_LIMIT = 100
    IP_RATE_LIMIT = 200
    ANONYMOUS_RATE_LIMIT = 50

    # 特殊接口限制
    LOGIN_RATE_LIMIT = 10
    REGISTER_RATE_LIMIT = 5
    UPLOAD_RATE_LIMIT = 20

class FileUploadLimits:
    """文件上传限制"""

    # 文件大小限制（字节）
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50MB

    # 支持的文件格式
    ALLOWED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    ALLOWED_VIDEO_FORMATS = ['mp4', 'avi', 'mov', 'wmv']
    ALLOWED_DOCUMENT_FORMATS = ['pdf', 'doc', 'docx', 'txt']

class BusinessLimits:
    """业务限制常量"""

    # 家族相关限制
    MAX_FAMILIES_PER_USER = 10
    MAX_MEMBERS_PER_FAMILY = 1000
    MAX_INVITATIONS_PER_DAY = 50

    # 成员相关限制
    MAX_RELATIONSHIPS_PER_MEMBER = 100
    MAX_MEDIA_PER_MEMBER = 500

    # 文本长度限制
    MAX_FAMILY_NAME_LENGTH = 100
    MAX_FAMILY_DESCRIPTION_LENGTH = 1000
    MAX_MEMBER_NAME_LENGTH = 50
    MAX_MEMBER_BIOGRAPHY_LENGTH = 2000

__all__ = [
    'HttpStatusCode',
    'ApiErrorCode',
    'ApiErrorMessage',
    'PaginationDefaults',
    'CacheTimeout',
    'RateLimitDefaults',
    'FileUploadLimits',
    'BusinessLimits',
]