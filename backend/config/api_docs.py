"""
API文档生成器

自动生成符合OpenAPI 3.0规范的API文档。
遵循API设计文档规范。
"""

import json
from typing import Dict, Any, List
from ninja import NinjaAPI
from .api_config import api_config


class APIDocumentationGenerator:
    """API文档生成器"""

    def __init__(self, api: NinjaAPI):
        self.api = api

    def generate_openapi_schema(self) -> Dict[str, Any]:
        """生成OpenAPI 3.0规范的API文档"""
        schema = {
            "openapi": "3.0.0",
            "info": {
                "title": api_config.TITLE,
                "description": api_config.DESCRIPTION,
                "version": api_config.VERSION,
                "contact": {"name": "API Support", "email": "support@familytree.com"},
                "license": {
                    "name": "MIT",
                    "url": "https://opensource.org/licenses/MIT",
                },
            },
            "servers": [{"url": "/api/v1", "description": "API v1.0"}],
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                    }
                },
                "schemas": self._generate_common_schemas(),
                "responses": self._generate_common_responses(),
            },
            "security": [{"bearerAuth": []}],
            "tags": self._generate_tags(),
        }

        return schema

    def _generate_common_schemas(self) -> Dict[str, Any]:
        """生成通用Schema定义"""
        return {
            "ApiResponse": {
                "type": "object",
                "properties": {
                    "code": {"type": "integer", "description": "响应状态码"},
                    "message": {"type": "string", "description": "响应消息"},
                    "data": {"description": "响应数据"},
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "响应时间戳",
                    },
                    "request_id": {"type": "string", "description": "请求ID"},
                },
                "required": ["code", "message", "timestamp", "request_id"],
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "code": {"type": "integer", "description": "错误码"},
                    "message": {"type": "string", "description": "错误消息"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "errors": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "field": {
                                            "type": "string",
                                            "description": "错误字段",
                                        },
                                        "message": {
                                            "type": "string",
                                            "description": "错误消息",
                                        },
                                    },
                                },
                            }
                        },
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "响应时间戳",
                    },
                    "request_id": {"type": "string", "description": "请求ID"},
                },
                "required": ["code", "message", "timestamp", "request_id"],
            },
            "PaginationInfo": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "description": "当前页码"},
                    "page_size": {"type": "integer", "description": "每页大小"},
                    "total": {"type": "integer", "description": "总记录数"},
                    "pages": {"type": "integer", "description": "总页数"},
                    "has_next": {"type": "boolean", "description": "是否有下一页"},
                    "has_prev": {"type": "boolean", "description": "是否有上一页"},
                },
                "required": [
                    "page",
                    "page_size",
                    "total",
                    "pages",
                    "has_next",
                    "has_prev",
                ],
            },
            "PaginatedResponse": {
                "type": "object",
                "properties": {
                    "code": {"type": "integer", "description": "响应状态码"},
                    "message": {"type": "string", "description": "响应消息"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "items": {"type": "array", "description": "数据列表"},
                            "pagination": {
                                "$ref": "#/components/schemas/PaginationInfo"
                            },
                        },
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "响应时间戳",
                    },
                    "request_id": {"type": "string", "description": "请求ID"},
                },
                "required": ["code", "message", "data", "timestamp", "request_id"],
            },
        }

    def _generate_common_responses(self) -> Dict[str, Any]:
        """生成通用响应定义"""
        return {
            "BadRequest": {
                "description": "请求参数错误",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                },
            },
            "Unauthorized": {
                "description": "未授权访问",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                },
            },
            "Forbidden": {
                "description": "禁止访问",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                },
            },
            "NotFound": {
                "description": "资源不存在",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                },
            },
            "ValidationError": {
                "description": "数据验证错误",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                },
            },
            "RateLimitExceeded": {
                "description": "请求频率超限",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                },
            },
            "InternalServerError": {
                "description": "服务器内部错误",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                },
            },
        }

    def _generate_tags(self) -> List[Dict[str, str]]:
        """生成API标签"""
        return [
            {"name": "Authentication", "description": "用户认证相关接口"},
            {"name": "Users", "description": "用户管理相关接口"},
            {"name": "Family", "description": "家族管理相关接口"},
            {"name": "Members", "description": "家族成员相关接口"},
            {"name": "Relationships", "description": "关系管理相关接口"},
            {"name": "Media", "description": "媒体文件相关接口"},
        ]

    def add_custom_schema(self, name: str, schema: Dict[str, Any]) -> None:
        """添加自定义Schema"""
        if not hasattr(self, "_custom_schemas"):
            self._custom_schemas = {}
        self._custom_schemas[name] = schema

    def add_custom_response(self, name: str, response: Dict[str, Any]) -> None:
        """添加自定义响应"""
        if not hasattr(self, "_custom_responses"):
            self._custom_responses = {}
        self._custom_responses[name] = response

    def export_to_file(self, file_path: str) -> None:
        """导出API文档到文件"""
        schema = self.generate_openapi_schema()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)


def create_api_documentation(api: NinjaAPI) -> APIDocumentationGenerator:
    """创建API文档生成器"""
    return APIDocumentationGenerator(api)
