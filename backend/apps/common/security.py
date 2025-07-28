"""
API安全模块

提供基础的API安全功能，包括输入验证和基本防护。
遵循Django Ninja最佳实践。
"""

import re
import secrets
from typing import Any, List
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags


class InputValidator:
    """输入验证器"""
    
    # 基本的XSS攻击模式
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
    ]
    
    # 基本的SQL注入模式
    SQL_PATTERNS = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION)\b)',
        r'(--|#|/\*|\*/)',
    ]
    
    @classmethod
    def validate_text_input(cls, value: Any, field_name: str = "input") -> str:
        """
        验证文本输入
        
        Args:
            value: 输入值
            field_name: 字段名称
            
        Returns:
            str: 清理后的值
            
        Raises:
            ValidationError: 验证失败
        """
        if value is None:
            return ""
        
        str_value = str(value).strip()
        
        # 检查基本的XSS攻击
        if cls._contains_xss(str_value):
            raise ValidationError(f"Invalid content in {field_name}")
        
        # 检查基本的SQL注入
        if cls._contains_sql_injection(str_value):
            raise ValidationError(f"Invalid content in {field_name}")
        
        # 移除HTML标签
        cleaned_value = strip_tags(str_value)
        
        return cleaned_value
    
    @classmethod
    def _contains_xss(cls, value: str) -> bool:
        """检查XSS攻击模式"""
        value_lower = value.lower()
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def _contains_sql_injection(cls, value: str) -> bool:
        """检查SQL注入模式"""
        value_upper = value.upper()
        for pattern in cls.SQL_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def validate_file_upload(cls, file_obj, allowed_types: List[str], max_size: int) -> None:
        """
        验证文件上传
        
        Args:
            file_obj: 文件对象
            allowed_types: 允许的文件类型
            max_size: 最大文件大小（字节）
            
        Raises:
            ValidationError: 验证失败
        """
        # 检查文件大小
        if file_obj.size > max_size:
            raise ValidationError(f"File size exceeds maximum {max_size} bytes")
        
        # 检查文件类型
        if file_obj.content_type not in allowed_types:
            raise ValidationError(f"File type {file_obj.content_type} not allowed")


class TokenGenerator:
    """令牌生成器"""
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """生成安全令牌"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def compare_tokens(token1: str, token2: str) -> bool:
        """安全比较令牌"""
        if not token1 or not token2:
            return False
        return secrets.compare_digest(token1, token2)
    
    def is_allowed(self, identifier: str) -> bool:
        """
        检查是否允许请求
        
        Args:
            identifier: 标识符（如IP地址、用户ID）
            
        Returns:
            bool: 是否允许
        """
        import time
        
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        # 清理过期记录
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        # 检查请求数量
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # 记录当前请求
        self.requests[identifier].append(current_time)
        return True
    
    def get_remaining_requests(self, identifier: str) -> int:
        """获取剩余请求数"""
        if identifier not in self.requests:
            return self.max_requests
        
        return max(0, self.max_requests - len(self.requests[identifier]))


class PasswordValidator:
    """密码验证器"""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    @classmethod
    def validate_password(cls, password: str) -> Dict[str, Any]:
        """
        验证密码强度
        
        Args:
            password: 密码
            
        Returns:
            Dict: 验证结果
        """
        errors = []
        score = 0
        
        # 长度检查
        if len(password) < cls.MIN_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_LENGTH} characters long")
        elif len(password) > cls.MAX_LENGTH:
            errors.append(f"Password must not exceed {cls.MAX_LENGTH} characters")
        else:
            score += 1
        
        # 复杂度检查
        if re.search(r'[a-z]', password):
            score += 1
        else:
            errors.append("Password must contain at least one lowercase letter")
        
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            errors.append("Password must contain at least one uppercase letter")
        
        if re.search(r'\d', password):
            score += 1
        else:
            errors.append("Password must contain at least one digit")
        
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        else:
            errors.append("Password must contain at least one special character")
        
        # 常见密码检查
        common_passwords = [
            'password', '123456', 'password123', 'admin', 'qwerty',
            '12345678', '123456789', 'password1', 'abc123'
        ]
        
        if password.lower() in common_passwords:
            errors.append("Password is too common")
            score = 0
        
        # 计算强度等级
        if score >= 5:
            strength = "strong"
        elif score >= 3:
            strength = "medium"
        else:
            strength = "weak"
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'strength': strength,
            'score': score
        }
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """哈希密码"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    @classmethod
    def verify_password(cls, password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            salt, stored_hash = hashed_password.split(':')
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return secrets.compare_digest(password_hash.hex(), stored_hash)
        except ValueError:
            return False


class SecurityHeaders:
    """安全头管理"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """获取安全头"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none';"
            ),
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Permissions-Policy': (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            )
        }


# 全局安全验证器实例
security_validator = SecurityValidator()
csrf_protection = CSRFProtection()
password_validator = PasswordValidator()