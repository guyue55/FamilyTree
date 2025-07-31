"""
Common应用

提供通用的功能模块，包括schemas、mixins、exceptions等。
"""

__all__ = [
    # Schemas
    'ResponseSchema',
    'PaginatedResponseSchema',
    'FileUploadSchema',
    'ImageUploadSchema',
    'PaginationSchema',
    'MessageResponseSchema',
    'DataResponseSchema',

    # Mixins
    'CacheMixin',
    'PermissionMixin',
    'QuerysetMixin',
    'ContextMixin',
    'ValidationMixin',
    'AuditMixin',
    'ResponseMixin',

    # Exceptions
    'BaseApplicationException',
    'ValidationError',
    'PermissionError',
    'NotFoundError',
    'LimitExceededError',
    'StatusError',
    'ConfigurationError',
    'OperationError',
    'DataError',
    'ServiceUnavailableError',
    'RateLimitError',
    'MaintenanceError',
    'handle_exception',
    'raise_if_not_found',
    'raise_if_permission_denied',
    'raise_if_limit_exceeded',
]