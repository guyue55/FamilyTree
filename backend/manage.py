#!/usr/bin/env python
"""
族谱系统Django管理工具

该文件是Django项目的命令行管理工具。
遵循Django最佳实践和Google Python Style Guide。
"""

import os
import sys


def main():
    """运行Django管理任务"""
    # 设置默认的Django设置模块
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入Django。请确保Django已安装并且在PYTHONPATH环境变量中可用。"
            "是否忘记激活虚拟环境？"
        ) from exc
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()