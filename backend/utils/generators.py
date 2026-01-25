"""
代码生成器工具类

提供各种代码生成功能，包括邀请码、slug、二维码等。
遵循Django最佳实践和Google Python Style Guide。
"""

import random
import string
from typing import Optional
from urllib.parse import urljoin

import qrcode
from qrcode.image.styledpil import StyledPilImage
from PIL import Image
from django.utils.text import slugify


class CodeGenerator:
    """通用代码生成器"""

    @staticmethod
    def generate_random_code(
        length: int = 32,
        include_uppercase: bool = True,
        include_lowercase: bool = True,
        include_digits: bool = True,
        include_symbols: bool = False,
    ) -> str:
        """
        生成随机代码

        Args:
            length: 代码长度
            include_uppercase: 是否包含大写字母
            include_lowercase: 是否包含小写字母
            include_digits: 是否包含数字
            include_symbols: 是否包含符号

        Returns:
            str: 生成的随机代码
        """
        characters = ""

        if include_uppercase:
            characters += string.ascii_uppercase
        if include_lowercase:
            characters += string.ascii_lowercase
        if include_digits:
            characters += string.digits
        if include_symbols:
            characters += "!@#$%^&*"

        if not characters:
            raise ValueError("至少需要选择一种字符类型")

        return "".join(random.choices(characters, k=length))

    @staticmethod
    def generate_invitation_code(length: int = 32) -> str:
        """
        生成邀请码

        Args:
            length: 邀请码长度

        Returns:
            str: 邀请码
        """
        return CodeGenerator.generate_random_code(
            length=length,
            include_uppercase=True,
            include_lowercase=True,
            include_digits=True,
            include_symbols=False,
        )

    @staticmethod
    def generate_slug(name: str, max_length: int = 50, suffix_length: int = 6) -> str:
        """
        生成URL友好的slug

        Args:
            name: 原始名称
            max_length: 最大长度
            suffix_length: 随机后缀长度

        Returns:
            str: 生成的slug
        """
        base_slug = slugify(name)
        if not base_slug:
            base_slug = "item"

        # 确保基础slug不超过限制
        available_length = max_length - suffix_length - 1  # -1 for hyphen
        if len(base_slug) > available_length:
            base_slug = base_slug[:available_length]

        # 添加随机后缀确保唯一性
        suffix = "".join(random.choices(string.digits, k=suffix_length))
        return f"{base_slug}-{suffix}"

    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """
        生成验证码（纯数字）

        Args:
            length: 验证码长度

        Returns:
            str: 验证码
        """
        return "".join(random.choices(string.digits, k=length))

    @staticmethod
    def generate_api_key(prefix: str = "", length: int = 40) -> str:
        """
        生成API密钥

        Args:
            prefix: 前缀
            length: 密钥长度（不包括前缀）

        Returns:
            str: API密钥
        """
        key = CodeGenerator.generate_random_code(
            length=length,
            include_uppercase=True,
            include_lowercase=True,
            include_digits=True,
            include_symbols=False,
        )

        if prefix:
            return f"{prefix}_{key}"
        return key


class QRCodeGenerator:
    """二维码生成器"""

    @staticmethod
    def generate_qr_code(
        data: str,
        size: int = 200,
        error_correction: int = qrcode.constants.ERROR_CORRECT_L,
        box_size: int = 10,
        border: int = 4,
        fill_color: str = "black",
        back_color: str = "white",
    ) -> bytes:
        """
        生成二维码

        Args:
            data: 二维码数据
            size: 二维码大小
            error_correction: 错误纠正级别
            box_size: 每个方块的像素数
            border: 边框大小
            fill_color: 前景色
            back_color: 背景色

        Returns:
            bytes: 二维码图片数据
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_correction,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(
            image_factory=StyledPilImage, fill_color=fill_color, back_color=back_color
        )

        # 调整大小
        img = img.resize((size, size), Image.Resampling.LANCZOS)

        # 转换为bytes
        import io

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    @staticmethod
    def generate_qr_code_with_logo(
        data: str, logo_path: str, size: int = 200, logo_size_ratio: float = 0.3
    ) -> bytes:
        """
        生成带Logo的二维码

        Args:
            data: 二维码数据
            logo_path: Logo图片路径
            size: 二维码大小
            logo_size_ratio: Logo大小比例

        Returns:
            bytes: 二维码图片数据
        """
        # 生成基础二维码
        qr_img_bytes = QRCodeGenerator.generate_qr_code(data, size)

        # 打开二维码图片
        import io

        qr_img = Image.open(io.BytesIO(qr_img_bytes))

        # 打开Logo图片
        logo = Image.open(logo_path)

        # 计算Logo大小
        logo_size = int(size * logo_size_ratio)
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        # 将Logo粘贴到二维码中心
        logo_pos = ((size - logo_size) // 2, (size - logo_size) // 2)
        qr_img.paste(logo, logo_pos)

        # 转换为bytes
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        return buffer.getvalue()
