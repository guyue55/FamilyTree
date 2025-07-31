"""
异常处理配置

该模块定义了异常处理相关的配置参数，包括日志级别、监控阈值、
敏感数据过滤规则等。遵循Django最佳实践和Google Python Style Guide。

设计原则：
- 可配置性：支持不同环境的配置差异
- 安全性：敏感信息的适当处理
- 可观测性：详细的监控和告警配置
- 性能优化：合理的阈值设置
"""

from decouple import config

EXCEPTION_HANDLING_CONFIG = {
    # 是否启用详细错误信息（仅开发环境）
    'ENABLE_DETAILED_ERRORS': config('ENABLE_DETAILED_ERRORS', default=False, cast=bool),

    # 是否启用异常告警
    'ENABLE_EXCEPTION_ALERTS': config('ENABLE_EXCEPTION_ALERTS', default=True, cast=bool),

    # 异常日志级别
    'EXCEPTION_LOG_LEVEL': config('EXCEPTION_LOG_LEVEL', default='ERROR'),

    # 是否记录请求体（可能包含敏感信息）
    'LOG_REQUEST_BODY': config('LOG_REQUEST_BODY', default=False, cast=bool),

    # 是否记录响应体
    'LOG_RESPONSE_BODY': config('LOG_RESPONSE_BODY', default=False, cast=bool),

    # 最大日志长度
    'MAX_LOG_LENGTH': config('MAX_LOG_LENGTH', default=10000, cast=int),
}

# 性能监控配置
PERFORMANCE_MONITORING_CONFIG = {
    # 慢请求阈值（秒）
    'SLOW_REQUEST_THRESHOLD': config('SLOW_REQUEST_THRESHOLD', default=2.0, cast=float),

    # 是否启用性能监控
    'ENABLE_PERFORMANCE_MONITORING': config('ENABLE_PERFORMANCE_MONITORING', default=True, cast=bool),

    # 性能日志级别
    'PERFORMANCE_LOG_LEVEL': config('PERFORMANCE_LOG_LEVEL', default='WARNING'),

    # 是否记录所有请求的性能数据
    'LOG_ALL_REQUESTS': config('LOG_ALL_REQUESTS', default=False, cast=bool),
}

# 限流配置
RATE_LIMITING_CONFIG = {
    # 默认限流规则（每分钟请求数）
    'DEFAULT_RATE_LIMIT': config('DEFAULT_RATE_LIMIT', default=60, cast=int),

    # 限流时间窗口（秒）
    'RATE_LIMIT_WINDOW': config('RATE_LIMIT_WINDOW', default=60, cast=int),

    # 是否启用限流
    'ENABLE_RATE_LIMITING': config('ENABLE_RATE_LIMITING', default=True, cast=bool),

    # 限流存储后端
    'RATE_LIMIT_BACKEND': config('RATE_LIMIT_BACKEND', default='memory'),  # memory, redis

    # 特殊路径的限流规则
    'SPECIAL_RATE_LIMITS': {
        '/api/v1/auth/login': config('LOGIN_RATE_LIMIT', default=10, cast=int),
        '/api/v1/auth/register': config('REGISTER_RATE_LIMIT', default=5, cast=int),
        '/api/v1/auth/reset-password': config('RESET_PASSWORD_RATE_LIMIT', default=3, cast=int),
    }
}

# 健康检查配置
HEALTH_CHECK_CONFIG = {
    # 健康检查路径
    'HEALTH_CHECK_PATH': config('HEALTH_CHECK_PATH', default='/health'),

    # 是否启用健康检查
    'ENABLE_HEALTH_CHECK': config('ENABLE_HEALTH_CHECK', default=True, cast=bool),

    # 数据库连接超时（秒）
    'DB_TIMEOUT': config('DB_TIMEOUT', default=5, cast=int),

    # 缓存连接超时（秒）
    'CACHE_TIMEOUT': config('CACHE_TIMEOUT', default=3, cast=int),

    # 健康检查缓存时间（秒）
    'HEALTH_CHECK_CACHE_TIME': config('HEALTH_CHECK_CACHE_TIME', default=30, cast=int),
}

# 敏感数据过滤配置
SENSITIVE_DATA_CONFIG = {
    # 需要过滤的字段名（不区分大小写）
    'SENSITIVE_FIELDS': {
        'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'auth',
        'authorization', 'credential', 'private', 'confidential',
        'ssn', 'social_security', 'credit_card', 'card_number',
        'phone', 'mobile', 'email', 'address', 'location'
    },

    # 需要过滤的HTTP头（不区分大小写）
    'SENSITIVE_HEADERS': {
        'authorization', 'x-api-key', 'x-auth-token', 'cookie',
        'x-csrf-token', 'x-forwarded-for', 'x-real-ip'
    },

    # 过滤替换文本
    'FILTER_REPLACEMENT': '***FILTERED***',

    # 是否启用敏感数据过滤
    'ENABLE_SENSITIVE_FILTERING': config('ENABLE_SENSITIVE_FILTERING', default=True, cast=bool),
}

# 告警配置
ALERT_CONFIG = {
    # 是否启用邮件告警
    'ENABLE_EMAIL_ALERTS': config('ENABLE_EMAIL_ALERTS', default=False, cast=bool),

    # 告警邮件接收者
    'ALERT_EMAIL_RECIPIENTS': config(
        'ALERT_EMAIL_RECIPIENTS',
        default='',
        cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
    ),

    # 告警阈值配置
    'ALERT_THRESHOLDS': {
        # 连续异常次数阈值
        'CONSECUTIVE_ERRORS': config('ALERT_CONSECUTIVE_ERRORS', default=5, cast=int),

        # 异常频率阈值（每分钟）
        'ERROR_RATE_PER_MINUTE': config('ALERT_ERROR_RATE', default=10, cast=int),

        # 慢请求频率阈值（每分钟）
        'SLOW_REQUEST_RATE': config('ALERT_SLOW_REQUEST_RATE', default=5, cast=int),
    },

    # 告警冷却时间（秒）
    'ALERT_COOLDOWN': config('ALERT_COOLDOWN', default=300, cast=int),
}

# 异常分类配置
EXCEPTION_CATEGORIES = {
    # 业务异常
    'BUSINESS_EXCEPTIONS': {
        'apps.common.exceptions.BaseApplicationException',
        'apps.family.exceptions.FamilyNameConflictError',
        'apps.family.exceptions.FamilyMemberLimitError',
    },

    # 数据库异常
    'DATABASE_EXCEPTIONS': {
        'django.db.utils.DatabaseError',
        'django.db.utils.IntegrityError',
        'django.db.utils.OperationalError',
        'django.db.utils.DataError',
    },

    # 验证异常
    'VALIDATION_EXCEPTIONS': {
        'django.core.exceptions.ValidationError',
        'ninja.errors.ValidationError',
        'pydantic.ValidationError',
    },

    # 权限异常
    'PERMISSION_EXCEPTIONS': {
        'django.core.exceptions.PermissionDenied',
        'apps.common.exceptions.PermissionError',
    },

    # 系统异常
    'SYSTEM_EXCEPTIONS': {
        'SystemError',
        'MemoryError',
        'OSError',
        'IOError',
    }
}

# 日志格式配置
LOG_FORMAT_CONFIG = {
    # 异常日志格式
    'EXCEPTION_LOG_FORMAT': (
        "[{timestamp}] {level} | {request_id} | {method} {path} | "
        "{exception_type}: {exception_message} | "
        "User: {user_id} | IP: {client_ip} | "
        "Duration: {duration}ms"
    ),

    # 性能日志格式
    'PERFORMANCE_LOG_FORMAT': (
        "[{timestamp}] {level} | {request_id} | {method} {path} | "
        "Duration: {duration}ms | Status: {status_code} | "
        "User: {user_id} | IP: {client_ip}"
    ),

    # 限流日志格式
    'RATE_LIMIT_LOG_FORMAT': (
        "[{timestamp}] WARNING | Rate limit exceeded | "
        "IP: {client_ip} | Path: {path} | "
        "Current: {current_requests} | Limit: {rate_limit}"
    ),
}

# 监控指标配置
METRICS_CONFIG = {
    # 是否启用指标收集
    'ENABLE_METRICS': config('ENABLE_METRICS', default=True, cast=bool),

    # 指标收集间隔（秒）
    'METRICS_INTERVAL': config('METRICS_INTERVAL', default=60, cast=int),

    # 指标存储后端
    'METRICS_BACKEND': config('METRICS_BACKEND', default='memory'),  # memory, redis, prometheus

    # 指标保留时间（秒）
    'METRICS_RETENTION': config('METRICS_RETENTION', default=86400, cast=int),  # 24小时
}

# 调试配置
DEBUG_CONFIG = {
    # 是否启用调试模式
    'ENABLE_DEBUG_MODE': config('ENABLE_DEBUG_MODE', default=False, cast=bool),

    # 是否记录堆栈跟踪
    'LOG_STACK_TRACE': config('LOG_STACK_TRACE', default=True, cast=bool),

    # 是否记录局部变量
    'LOG_LOCAL_VARIABLES': config('LOG_LOCAL_VARIABLES', default=False, cast=bool),

    # 调试信息最大长度
    'DEBUG_INFO_MAX_LENGTH': config('DEBUG_INFO_MAX_LENGTH', default=5000, cast=int),
}