"""
通用验证器工具类

提供各种数据验证功能。
遵循Django最佳实践和Google Python Style Guide。
"""

import re
from typing import Tuple, List, Optional, Any
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from PIL import Image


class CommonValidator:
    """通用验证器"""
    
    @staticmethod
    def validate_name(name: str, min_length: int = 2, max_length: int = 100) -> bool:
        """
        验证名称
        
        Args:
            name: 名称
            min_length: 最小长度
            max_length: 最大长度
            
        Returns:
            bool: 是否有效
        """
        if not name or not isinstance(name, str):
            return False
        
        name = name.strip()
        if len(name) < min_length or len(name) > max_length:
            return False
        
        # 检查是否包含特殊字符
        forbidden_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
        return not any(char in name for char in forbidden_chars)
    
    @staticmethod
    def validate_email_or_phone(contact: str) -> Tuple[bool, str]:
        """
        验证邮箱或手机号
        
        Args:
            contact: 联系方式
            
        Returns:
            Tuple[bool, str]: (是否有效, 类型)
        """
        if not contact or not isinstance(contact, str):
            return False, 'unknown'
        
        contact = contact.strip()
        
        # 尝试验证邮箱
        try:
            validate_email(contact)
            return True, 'email'
        except ValidationError:
            pass
        
        # 验证手机号（支持多种格式）
        phone_patterns = [
            r'^1[3-9]\d{9}$',  # 中国手机号
            r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$',  # 美国手机号
            r'^\+?[1-9]\d{1,14}$',  # 国际格式
        ]
        
        for pattern in phone_patterns:
            if re.match(pattern, contact.replace('-', '').replace(' ', '')):
                return True, 'phone'
        
        return False, 'unknown'
    
    @staticmethod
    def validate_password(password: str, 
                         min_length: int = 8,
                         require_uppercase: bool = True,
                         require_lowercase: bool = True,
                         require_digit: bool = True,
                         require_special: bool = True) -> Tuple[bool, List[str]]:
        """
        验证密码强度
        
        Args:
            password: 密码
            min_length: 最小长度
            require_uppercase: 是否需要大写字母
            require_lowercase: 是否需要小写字母
            require_digit: 是否需要数字
            require_special: 是否需要特殊字符
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        errors = []
        
        if not password or not isinstance(password, str):
            errors.append("密码不能为空")
            return False, errors
        
        if len(password) < min_length:
            errors.append(f"密码长度不能少于{min_length}位")
        
        if require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("密码必须包含大写字母")
        
        if require_lowercase and not re.search(r'[a-z]', password):
            errors.append("密码必须包含小写字母")
        
        if require_digit and not re.search(r'\d', password):
            errors.append("密码必须包含数字")
        
        if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("密码必须包含特殊字符")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        验证URL格式
        
        Args:
            url: URL字符串
            
        Returns:
            bool: 是否有效
        """
        if not url or not isinstance(url, str):
            return False
        
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return url_pattern.match(url) is not None
    
    @staticmethod
    def validate_code_format(code: str, length: int, allowed_chars: str = None) -> bool:
        """
        验证代码格式
        
        Args:
            code: 代码
            length: 期望长度
            allowed_chars: 允许的字符集
            
        Returns:
            bool: 是否有效
        """
        if not code or not isinstance(code, str):
            return False
        
        if len(code) != length:
            return False
        
        if allowed_chars is None:
            # 默认允许字母和数字
            allowed_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        return all(char in allowed_chars for char in code)


class FileValidator:
    """文件验证器"""
    
    @staticmethod
    def validate_file_size(file_obj: Any, max_size: int) -> Tuple[bool, str]:
        """
        验证文件大小
        
        Args:
            file_obj: 文件对象
            max_size: 最大文件大小（字节）
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not hasattr(file_obj, 'size'):
            return False, "无效的文件对象"
        
        if file_obj.size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            return False, f"文件大小不能超过{max_size_mb:.1f}MB"
        
        return True, ""
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> Tuple[bool, str]:
        """
        验证文件扩展名
        
        Args:
            filename: 文件名
            allowed_extensions: 允许的扩展名列表
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not filename or '.' not in filename:
            return False, "无效的文件名"
        
        file_extension = filename.split('.')[-1].lower()
        allowed_extensions = [ext.lower() for ext in allowed_extensions]
        
        if file_extension not in allowed_extensions:
            return False, f"不支持的文件格式，支持的格式：{', '.join(allowed_extensions)}"
        
        return True, ""
    
    @staticmethod
    def validate_image_file(file_obj: Any, 
                           max_size: int,
                           max_dimensions: Tuple[int, int],
                           allowed_formats: List[str] = None) -> Tuple[bool, str]:
        """
        验证图片文件
        
        Args:
            file_obj: 文件对象
            max_size: 最大文件大小
            max_dimensions: 最大尺寸 (width, height)
            allowed_formats: 允许的格式列表
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if allowed_formats is None:
            allowed_formats = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        
        # 检查文件大小
        is_valid, error_msg = FileValidator.validate_file_size(file_obj, max_size)
        if not is_valid:
            return False, error_msg
        
        # 检查文件扩展名
        if hasattr(file_obj, 'name'):
            is_valid, error_msg = FileValidator.validate_file_extension(
                file_obj.name, allowed_formats
            )
            if not is_valid:
                return False, error_msg
        
        try:
            # 检查图片尺寸
            with Image.open(file_obj) as img:
                width, height = img.size
                max_width, max_height = max_dimensions
                
                if width > max_width or height > max_height:
                    return False, f"图片尺寸不能超过 {max_width}x{max_height}"
                
                # 验证图片格式
                if img.format.lower() not in [fmt.upper() for fmt in allowed_formats]:
                    return False, f"不支持的图片格式：{img.format}"
                
                return True, ""
                
        except Exception as e:
            return False, f"无效的图片文件：{str(e)}"
    
    @staticmethod
    def validate_mime_type(file_obj: Any, allowed_mime_types: List[str]) -> Tuple[bool, str]:
        """
        验证MIME类型
        
        Args:
            file_obj: 文件对象
            allowed_mime_types: 允许的MIME类型列表
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not hasattr(file_obj, 'content_type'):
            return False, "无法获取文件MIME类型"
        
        if file_obj.content_type not in allowed_mime_types:
            return False, f"不支持的文件类型：{file_obj.content_type}"
        
        return True, ""