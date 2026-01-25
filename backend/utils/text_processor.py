"""
文本处理工具类

提供文本处理相关功能。
遵循Django最佳实践和Google Python Style Guide。
"""

import re
import unicodedata
from typing import List, Optional, Dict, Any
from django.utils.text import slugify
from django.utils.html import strip_tags


class TextProcessor:
    """文本处理器"""

    @staticmethod
    def clean_text(
        text: str,
        remove_html: bool = True,
        normalize_whitespace: bool = True,
        strip_whitespace: bool = True,
    ) -> str:
        """
        清理文本

        Args:
            text: 原始文本
            remove_html: 是否移除HTML标签
            normalize_whitespace: 是否规范化空白字符
            strip_whitespace: 是否去除首尾空白

        Returns:
            str: 清理后的文本
        """
        if not text:
            return ""

        # 移除HTML标签
        if remove_html:
            text = strip_tags(text)

        # 规范化空白字符
        if normalize_whitespace:
            text = re.sub(r"\s+", " ", text)

        # 去除首尾空白
        if strip_whitespace:
            text = text.strip()

        return text

    @staticmethod
    def truncate_text(
        text: str, max_length: int, suffix: str = "...", word_boundary: bool = True
    ) -> str:
        """
        截断文本

        Args:
            text: 原始文本
            max_length: 最大长度
            suffix: 后缀
            word_boundary: 是否在单词边界截断

        Returns:
            str: 截断后的文本
        """
        if not text or len(text) <= max_length:
            return text

        if word_boundary:
            # 在单词边界截断
            truncated = text[: max_length - len(suffix)]
            last_space = truncated.rfind(" ")
            if last_space > 0:
                truncated = truncated[:last_space]
            return truncated + suffix
        else:
            # 直接截断
            return text[: max_length - len(suffix)] + suffix

    @staticmethod
    def generate_slug(
        text: str, max_length: int = 50, allow_unicode: bool = False
    ) -> str:
        """
        生成URL友好的slug

        Args:
            text: 原始文本
            max_length: 最大长度
            allow_unicode: 是否允许Unicode字符

        Returns:
            str: slug字符串
        """
        if not text:
            return ""

        slug = slugify(text, allow_unicode=allow_unicode)

        if len(slug) > max_length:
            slug = slug[:max_length].rstrip("-")

        return slug

    @staticmethod
    def extract_keywords(
        text: str,
        min_length: int = 3,
        max_keywords: int = 10,
        stop_words: Optional[List[str]] = None,
    ) -> List[str]:
        """
        提取关键词

        Args:
            text: 原始文本
            min_length: 最小词长
            max_keywords: 最大关键词数
            stop_words: 停用词列表

        Returns:
            List[str]: 关键词列表
        """
        if not text:
            return []

        if stop_words is None:
            stop_words = [
                "the",
                "a",
                "an",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
                "is",
                "are",
                "was",
                "were",
                "be",
                "been",
                "being",
                "have",
                "has",
                "had",
                "do",
                "does",
                "did",
                "will",
                "would",
                "could",
                "should",
                "may",
                "might",
                "must",
                "can",
                "this",
                "that",
                "these",
                "those",
                "i",
                "you",
                "he",
                "she",
                "it",
                "we",
                "they",
                "me",
                "him",
                "her",
                "us",
                "them",
            ]

        # 清理文本
        clean_text = TextProcessor.clean_text(text)

        # 提取单词
        words = re.findall(r"\b\w+\b", clean_text.lower())

        # 过滤单词
        keywords = []
        for word in words:
            if (
                len(word) >= min_length
                and word not in stop_words
                and word not in keywords
            ):
                keywords.append(word)

        return keywords[:max_keywords]

    @staticmethod
    def normalize_unicode(text: str, form: str = "NFKC") -> str:
        """
        规范化Unicode文本

        Args:
            text: 原始文本
            form: 规范化形式 (NFC, NFKC, NFD, NFKD)

        Returns:
            str: 规范化后的文本
        """
        if not text:
            return ""

        return unicodedata.normalize(form, text)

    @staticmethod
    def remove_accents(text: str) -> str:
        """
        移除重音符号

        Args:
            text: 原始文本

        Returns:
            str: 移除重音后的文本
        """
        if not text:
            return ""

        # 规范化为NFD形式，然后移除组合字符
        nfd = unicodedata.normalize("NFD", text)
        return "".join(char for char in nfd if unicodedata.category(char) != "Mn")

    @staticmethod
    def mask_sensitive_info(
        text: str, patterns: Optional[Dict[str, str]] = None
    ) -> str:
        """
        掩码敏感信息

        Args:
            text: 原始文本
            patterns: 自定义模式字典

        Returns:
            str: 掩码后的文本
        """
        if not text:
            return ""

        if patterns is None:
            patterns = {
                # 邮箱
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b": lambda m: m.group(
                    0
                )[:2]
                + "*" * (len(m.group(0)) - 4)
                + m.group(0)[-2:],
                # 手机号
                r"\b1[3-9]\d{9}\b": lambda m: m.group(0)[:3]
                + "*" * 4
                + m.group(0)[-4:],
                # 身份证号
                r"\b\d{17}[\dXx]\b": lambda m: m.group(0)[:6]
                + "*" * 8
                + m.group(0)[-4:],
            }

        masked_text = text
        for pattern, replacement in patterns.items():
            if callable(replacement):
                masked_text = re.sub(pattern, replacement, masked_text)
            else:
                masked_text = re.sub(pattern, replacement, masked_text)

        return masked_text

    @staticmethod
    def highlight_keywords(
        text: str, keywords: List[str], highlight_format: str = "<mark>{}</mark>"
    ) -> str:
        """
        高亮关键词

        Args:
            text: 原始文本
            keywords: 关键词列表
            highlight_format: 高亮格式

        Returns:
            str: 高亮后的文本
        """
        if not text or not keywords:
            return text

        highlighted_text = text
        for keyword in keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted_text = pattern.sub(
                lambda m: highlight_format.format(m.group(0)), highlighted_text
            )

        return highlighted_text

    @staticmethod
    def count_words(text: str, count_chinese: bool = True) -> Dict[str, int]:
        """
        统计文本信息

        Args:
            text: 原始文本
            count_chinese: 是否统计中文字符

        Returns:
            Dict[str, int]: 统计信息
        """
        if not text:
            return {"characters": 0, "words": 0, "lines": 0, "chinese_chars": 0}

        # 字符数
        char_count = len(text)

        # 行数
        line_count = len(text.splitlines())

        # 英文单词数
        english_words = re.findall(r"\b[A-Za-z]+\b", text)
        word_count = len(english_words)

        # 中文字符数
        chinese_count = 0
        if count_chinese:
            chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
            chinese_count = len(chinese_chars)
            # 中文字符也算作"词"
            word_count += chinese_count

        return {
            "characters": char_count,
            "words": word_count,
            "lines": line_count,
            "chinese_chars": chinese_count,
        }

    @staticmethod
    def format_phone_number(
        phone: str, country_code: str = "+86", format_style: str = "standard"
    ) -> str:
        """
        格式化手机号

        Args:
            phone: 手机号
            country_code: 国家代码
            format_style: 格式样式 (standard, dots, spaces)

        Returns:
            str: 格式化后的手机号
        """
        if not phone:
            return ""

        # 移除所有非数字字符
        digits_only = re.sub(r"\D", "", phone)

        # 中国手机号处理
        if country_code == "+86" and len(digits_only) == 11:
            if format_style == "dots":
                return f"{digits_only[:3]}.{digits_only[3:7]}.{digits_only[7:]}"
            elif format_style == "spaces":
                return f"{digits_only[:3]} {digits_only[3:7]} {digits_only[7:]}"
            else:  # standard
                return f"{digits_only[:3]}-{digits_only[3:7]}-{digits_only[7:]}"

        return phone
