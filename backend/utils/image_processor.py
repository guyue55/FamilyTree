"""
图片处理工具类

提供图片处理相关功能。
遵循Django最佳实践和Google Python Style Guide。
"""

import os
import io
from typing import Tuple, Optional, Union
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class ImageProcessor:
    """图片处理器"""

    @staticmethod
    def resize_image(
        image_file: Union[str, io.BytesIO],
        max_size: Tuple[int, int],
        quality: int = 85,
        format: str = "JPEG",
    ) -> io.BytesIO:
        """
        调整图片大小

        Args:
            image_file: 图片文件路径或BytesIO对象
            max_size: 最大尺寸 (width, height)
            quality: 图片质量 (1-100)
            format: 输出格式

        Returns:
            io.BytesIO: 处理后的图片数据
        """
        if isinstance(image_file, str):
            with open(image_file, "rb") as f:
                image_data = io.BytesIO(f.read())
        else:
            image_data = image_file

        with Image.open(image_data) as img:
            # 转换为RGB模式（如果需要）
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            # 计算新尺寸（保持宽高比）
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # 保存到BytesIO
            output = io.BytesIO()
            img.save(output, format=format, quality=quality, optimize=True)
            output.seek(0)

            return output

    @staticmethod
    def create_thumbnail(
        image_file: Union[str, io.BytesIO], size: Tuple[int, int], crop: bool = True
    ) -> io.BytesIO:
        """
        创建缩略图

        Args:
            image_file: 图片文件路径或BytesIO对象
            size: 缩略图尺寸
            crop: 是否裁剪（保持比例）

        Returns:
            io.BytesIO: 缩略图数据
        """
        if isinstance(image_file, str):
            with open(image_file, "rb") as f:
                image_data = io.BytesIO(f.read())
        else:
            image_data = image_file

        with Image.open(image_data) as img:
            # 转换为RGB模式
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            if crop:
                # 裁剪到指定尺寸（居中）
                img = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
            else:
                # 缩放到指定尺寸（保持比例）
                img.thumbnail(size, Image.Resampling.LANCZOS)

            output = io.BytesIO()
            img.save(output, format="JPEG", quality=85, optimize=True)
            output.seek(0)

            return output

    @staticmethod
    def compress_image(
        image_file: Union[str, io.BytesIO],
        quality: int = 85,
        max_size: Optional[Tuple[int, int]] = None,
    ) -> io.BytesIO:
        """
        压缩图片

        Args:
            image_file: 图片文件路径或BytesIO对象
            quality: 压缩质量 (1-100)
            max_size: 最大尺寸（可选）

        Returns:
            io.BytesIO: 压缩后的图片数据
        """
        if isinstance(image_file, str):
            with open(image_file, "rb") as f:
                image_data = io.BytesIO(f.read())
        else:
            image_data = image_file

        with Image.open(image_data) as img:
            # 转换为RGB模式
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            # 如果指定了最大尺寸，先调整大小
            if max_size:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

            output = io.BytesIO()
            img.save(output, format="JPEG", quality=quality, optimize=True)
            output.seek(0)

            return output

    @staticmethod
    def get_image_info(image_file: Union[str, io.BytesIO]) -> dict:
        """
        获取图片信息

        Args:
            image_file: 图片文件路径或BytesIO对象

        Returns:
            dict: 图片信息
        """
        if isinstance(image_file, str):
            with open(image_file, "rb") as f:
                image_data = io.BytesIO(f.read())
        else:
            image_data = image_file

        with Image.open(image_data) as img:
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size": len(image_data.getvalue())
                if hasattr(image_data, "getvalue")
                else None,
            }

    @staticmethod
    def convert_format(
        image_file: Union[str, io.BytesIO],
        target_format: str = "JPEG",
        quality: int = 85,
    ) -> io.BytesIO:
        """
        转换图片格式

        Args:
            image_file: 图片文件路径或BytesIO对象
            target_format: 目标格式
            quality: 图片质量

        Returns:
            io.BytesIO: 转换后的图片数据
        """
        if isinstance(image_file, str):
            with open(image_file, "rb") as f:
                image_data = io.BytesIO(f.read())
        else:
            image_data = image_file

        with Image.open(image_data) as img:
            # 如果目标格式是JPEG，确保是RGB模式
            if target_format.upper() == "JPEG" and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            output = io.BytesIO()
            save_kwargs = {"format": target_format, "optimize": True}

            if target_format.upper() == "JPEG":
                save_kwargs["quality"] = quality

            img.save(output, **save_kwargs)
            output.seek(0)

            return output

    @staticmethod
    def save_processed_image(
        image_data: io.BytesIO, filename: str, upload_path: str = "images/"
    ) -> str:
        """
        保存处理后的图片

        Args:
            image_data: 图片数据
            filename: 文件名
            upload_path: 上传路径

        Returns:
            str: 保存的文件路径
        """
        # 确保文件名有正确的扩展名
        if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
            filename += ".jpg"

        # 构建完整路径
        full_path = os.path.join(upload_path, filename)

        # 保存文件
        content_file = ContentFile(image_data.getvalue(), name=filename)
        saved_path = default_storage.save(full_path, content_file)

        return saved_path

    @staticmethod
    def create_avatar(
        image_file: Union[str, io.BytesIO], size: int = 200
    ) -> io.BytesIO:
        """
        创建头像（正方形裁剪）

        Args:
            image_file: 图片文件路径或BytesIO对象
            size: 头像尺寸

        Returns:
            io.BytesIO: 头像数据
        """
        return ImageProcessor.create_thumbnail(image_file, (size, size), crop=True)
