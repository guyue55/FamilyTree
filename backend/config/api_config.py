from typing import Dict, List, Any
from django.conf import settings

"""
API配置模块

集中管理API相关配置，包括版本、认证、限流等。
遵循API设计文档规范。
"""


class APIConfig:
    """API配置类"""

    # API版本配置
    VERSION = getattr(settings, "API_VERSION", "1.0.0")
    TITLE = "Family Tree API"
    DESCRIPTION = "家族树管理系统API接口"

    # 认证配置
    JWT_SECRET_KEY = getattr(settings, "SECRET_KEY", "")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # 文件上传配置
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    ALLOWED_DOCUMENT_TYPES = ["application/pdf", "text/plain", "application/msword"]

    # 限流配置
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 3600  # 1小时

    # CORS配置
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://familytree.example.com",
    ]

    # API响应配置
    RESPONSE_FORMATS = {
        "success": {
            "code": 200,
            "message": "Success",
            "data": None,
            "timestamp": None,
            "request_id": None,
        },
        "error": {
            "code": None,
            "message": None,
            "data": None,
            "timestamp": None,
            "request_id": None,
        },
        "validation_error": {
            "code": 400,
            "message": "Validation Error",
            "data": {"errors": []},
            "timestamp": None,
            "request_id": None,
        },
    }

    # 错误码映射
    ERROR_CODE_MAPPING = {
        # 通用错误码
        "INVALID_REQUEST": 400,
        "UNAUTHORIZED": 401,
        "FORBIDDEN": 403,
        "NOT_FOUND": 404,
        "METHOD_NOT_ALLOWED": 405,
        "VALIDATION_ERROR": 422,
        "RATE_LIMIT_EXCEEDED": 429,
        "INTERNAL_SERVER_ERROR": 500,
        # 业务错误码
        "USER_NOT_FOUND": 40001,
        "USER_ALREADY_EXISTS": 40002,
        "INVALID_CREDENTIALS": 40003,
        "TOKEN_EXPIRED": 40004,
        "TOKEN_INVALID": 40005,
        "FAMILY_NOT_FOUND": 40101,
        "MEMBER_NOT_FOUND": 40201,
        "RELATIONSHIP_NOT_FOUND": 40301,
        "PERMISSION_DENIED": 40302,
        "FILE_TOO_LARGE": 40401,
        "INVALID_FILE_TYPE": 40402,
    }

    # HTTP状态码映射
    HTTP_STATUS_MAPPING = {
        200: "OK",
        201: "Created",
        204: "No Content",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
        500: "Internal Server Error",
    }

    @classmethod
    def get_jwt_config(cls) -> Dict[str, Any]:
        """获取JWT配置"""
        return {
            "secret_key": cls.JWT_SECRET_KEY,
            "algorithm": cls.JWT_ALGORITHM,
            "access_token_expire_minutes": cls.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": cls.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
        }

    @classmethod
    def get_pagination_config(cls) -> Dict[str, int]:
        """获取分页配置"""
        return {
            "default_page_size": cls.DEFAULT_PAGE_SIZE,
            "max_page_size": cls.MAX_PAGE_SIZE,
        }

    @classmethod
    def get_file_upload_config(cls) -> Dict[str, Any]:
        """获取文件上传配置"""
        return {
            "max_file_size": cls.MAX_FILE_SIZE,
            "allowed_image_types": cls.ALLOWED_IMAGE_TYPES,
            "allowed_document_types": cls.ALLOWED_DOCUMENT_TYPES,
        }

    @classmethod
    def get_rate_limit_config(cls) -> Dict[str, Any]:
        """获取限流配置"""
        return {
            "enabled": cls.RATE_LIMIT_ENABLED,
            "requests": cls.RATE_LIMIT_REQUESTS,
            "window": cls.RATE_LIMIT_WINDOW,
        }

    @classmethod
    def get_cors_config(cls) -> Dict[str, List[str]]:
        """获取CORS配置"""
        return {
            "allowed_origins": cls.CORS_ALLOWED_ORIGINS,
        }

    @classmethod
    def get_error_code(cls, error_type: str) -> int:
        """获取错误码"""
        return cls.ERROR_CODE_MAPPING.get(error_type, 500)

    @classmethod
    def get_http_status_text(cls, status_code: int) -> str:
        """获取HTTP状态码文本"""
        return cls.HTTP_STATUS_MAPPING.get(status_code, "Unknown")


# 导出配置实例
api_config = APIConfig()
