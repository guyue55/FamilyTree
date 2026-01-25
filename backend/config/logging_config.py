"""
日志配置模块

该文件配置系统的日志记录功能。
遵循Django最佳实践和Google Python Style Guide。
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from decouple import config
from loguru import logger
import threading


class LoguruConfig:
    """Loguru日志配置类"""

    def __init__(self, base_dir: Path):
        """
        初始化日志配置

        Args:
            base_dir: 项目根目录
        """
        self.base_dir = base_dir
        self.log_dir = base_dir / "logs"
        self.log_level = config("LOG_LEVEL", default="INFO")
        self.debug_mode = config("DEBUG", default=False, cast=bool)

        # 确保日志目录存在
        self.log_dir.mkdir(exist_ok=True)

        # 初始化日志配置
        self._setup_loguru()
        self._setup_django_integration()

    def _setup_loguru(self) -> None:
        """配置loguru日志系统"""
        # 移除默认处理器
        logger.remove()

        # 控制台输出配置
        if self.debug_mode:
            # 开发环境：彩色输出，详细格式
            logger.add(
                sys.stdout,
                format=(
                    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>{extra[request_id]}</cyan> | "
                    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                    "<level>{message}</level>"
                ),
                level="DEBUG",
                colorize=True,
                filter=self._add_request_id_filter,
                backtrace=True,
                diagnose=True,
            )
        else:
            # 生产环境：简洁输出
            logger.add(
                sys.stdout,
                format=(
                    "{time:YYYY-MM-DD HH:mm:ss} | "
                    "{level} | "
                    "{extra[request_id]} | "
                    "{name}:{function}:{line} | "
                    "{message}"
                ),
                level=self.log_level,
                filter=self._add_request_id_filter,
            )

        # 文件输出配置
        self._setup_file_handlers()

        # 错误日志单独处理
        self._setup_error_handlers()

        # 性能日志
        self._setup_performance_handlers()

        # 审计日志
        self._setup_audit_handlers()

    def _setup_file_handlers(self) -> None:
        """配置文件日志处理器"""
        # 应用日志
        logger.add(
            self.log_dir / "app_{time:YYYY-MM-DD}.log",
            rotation="00:00",  # 每天轮转
            retention="30 days",  # 保留30天
            compression="zip",  # 压缩旧日志
            level="INFO",
            format=self._get_json_format(),
            filter=self._add_request_id_filter,
            enqueue=True,  # 异步写入
            serialize=True,  # JSON序列化
        )

        # 调试日志（仅开发环境）
        if self.debug_mode:
            logger.add(
                self.log_dir / "debug_{time:YYYY-MM-DD}.log",
                rotation="00:00",
                retention="7 days",
                level="DEBUG",
                format=self._get_json_format(),
                filter=self._add_request_id_filter,
                enqueue=True,
                serialize=True,
            )

    def _setup_error_handlers(self) -> None:
        """配置错误日志处理器"""
        logger.add(
            self.log_dir / "error_{time:YYYY-MM-DD}.log",
            rotation="00:00",
            retention="90 days",  # 错误日志保留更久
            compression="zip",
            level="ERROR",
            format=self._get_json_format(),
            filter=self._add_request_id_filter,
            enqueue=True,
            serialize=True,
            backtrace=True,
            diagnose=True,
        )

    def _setup_performance_handlers(self) -> None:
        """配置性能日志处理器"""
        logger.add(
            self.log_dir / "performance_{time:YYYY-MM-DD}.log",
            rotation="00:00",
            retention="30 days",
            compression="zip",
            level="INFO",
            format=self._get_json_format(),
            filter=lambda record: record["extra"].get("log_type") == "performance",
            enqueue=True,
            serialize=True,
        )

    def _setup_audit_handlers(self) -> None:
        """配置审计日志处理器"""
        logger.add(
            self.log_dir / "audit_{time:YYYY-MM-DD}.log",
            rotation="00:00",
            retention="365 days",  # 审计日志保留一年
            compression="zip",
            level="INFO",
            format=self._get_json_format(),
            filter=lambda record: record["extra"].get("log_type") == "audit",
            enqueue=True,
            serialize=True,
        )

    def _get_json_format(self) -> str:
        """获取简化的日志格式"""
        return "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {extra[request_id]} | {name}:{function}:{line} | {message}"

    def _add_request_id_filter(self, record: Dict[str, Any]) -> bool:
        """为日志记录添加请求ID"""
        if "request_id" not in record["extra"]:
            # 尝试从上下文变量获取请求ID
            request_id = self._get_current_request_id()
            record["extra"]["request_id"] = request_id or "no-request"
        return True

    def _get_current_request_id(self) -> Optional[str]:
        """获取当前请求ID"""
        try:
            # 尝试从线程本地存储获取
            local = getattr(threading.current_thread(), "request_context", None)
            if local and hasattr(local, "request_id"):
                return local.request_id
        except:
            pass

        return None

    def _setup_django_integration(self) -> None:
        """配置Django日志集成"""

        class InterceptHandler(logging.Handler):
            """拦截Django日志并转发给loguru"""

            def emit(self, record):
                # 获取对应的loguru级别
                try:
                    level = logger.level(record.levelname).name
                except ValueError:
                    level = record.levelno

                # 查找调用者
                frame, depth = logging.currentframe(), 2
                while frame and frame.f_code.co_filename == logging.__file__:
                    frame = frame.f_back
                    depth += 1

                # 转发到loguru
                logger.opt(depth=depth, exception=record.exc_info).log(
                    level, record.getMessage()
                )

        # 配置Django日志
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

        # 禁用Django默认日志处理器
        for name in logging.root.manager.loggerDict:
            if name.startswith("django"):
                logging.getLogger(name).handlers = []
                logging.getLogger(name).propagate = True


class RequestContextLogger:
    """请求上下文日志记录器"""

    def __init__(
        self,
        request_id: str,
        user_id: Optional[int] = None,
        endpoint: Optional[str] = None,
    ):
        """
        初始化请求上下文日志记录器

        Args:
            request_id: 请求ID
            user_id: 用户ID
            endpoint: API端点
        """
        self.context = {
            "request_id": request_id,
            "user_id": user_id,
            "endpoint": endpoint,
        }

    def bind_logger(self) -> "logger":
        """绑定上下文到logger"""
        return logger.bind(**self.context)

    def info(self, message: str, **kwargs) -> None:
        """记录信息日志"""
        self.bind_logger().info(message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """记录调试日志"""
        self.bind_logger().debug(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """记录警告日志"""
        self.bind_logger().warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """记录错误日志"""
        self.bind_logger().error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """记录严重错误日志"""
        self.bind_logger().critical(message, **kwargs)

    def performance(self, message: str, duration: float, **kwargs) -> None:
        """记录性能日志"""
        self.bind_logger().bind(
            log_type="performance", duration=duration, **kwargs
        ).info(message)

    def audit(self, action: str, resource: str, **kwargs) -> None:
        """记录审计日志"""
        self.bind_logger().bind(
            log_type="audit", action=action, resource=resource, **kwargs
        ).info(f"Audit: {action} on {resource}")


def get_request_logger(
    request_id: str, user_id: Optional[int] = None, endpoint: Optional[str] = None
) -> RequestContextLogger:
    """
    获取请求上下文日志记录器

    Args:
        request_id: 请求ID
        user_id: 用户ID
        endpoint: API端点

    Returns:
        RequestContextLogger: 请求上下文日志记录器
    """
    return RequestContextLogger(request_id, user_id, endpoint)


def setup_logging(base_dir: Path) -> None:
    """
    设置项目日志配置

    Args:
        base_dir: 项目根目录
    """
    LoguruConfig(base_dir)


# 导出常用的日志记录器
__all__ = [
    "LoguruConfig",
    "RequestContextLogger",
    "get_request_logger",
    "setup_logging",
    "logger",
]
