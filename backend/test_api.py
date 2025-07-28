#!/usr/bin/env python
"""
测试Django Ninja API的基本功能（不需要数据库）
"""
import os
import sys

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# 配置Django设置（不连接数据库）
import django
from django.conf import settings
if not settings.configured:
    django.setup()

def test_imports():
    """测试模块导入是否正常"""
    try:
        # 测试基本模块导入
        from apps.family import constants
        print("✓ 成功导入family constants")
        
        from apps.family import exceptions
        print("✓ 成功导入family exceptions")
        
        from apps.family import utils
        print("✓ 成功导入family utils")
        
        from apps.family import permissions
        print("✓ 成功导入family permissions")
        
        from apps.family import mixins
        print("✓ 成功导入family mixins")
        
        from apps.family import services
        print("✓ 成功导入family services")
        
        from apps.family import schemas
        print("✓ 成功导入family schemas")
        
        from apps.family import api
        print("✓ 成功导入family api")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schema_structure():
    """测试Schema结构"""
    try:
        from apps.family.schemas import FamilyCreateSchema, FamilyResponseSchema
        
        print("\n检查Schema结构:")
        print("✓ FamilyCreateSchema字段:", list(FamilyCreateSchema.__annotations__.keys()))
        print("✓ FamilyResponseSchema字段:", list(FamilyResponseSchema.__annotations__.keys()))
        
        return True
    except Exception as e:
        print(f"❌ Schema测试失败: {e}")
        return False

def test_constants():
    """测试常量定义"""
    try:
        from apps.family.constants import (
            FAMILY_VISIBILITY_CHOICES, 
            FAMILY_STATUS_CHOICES,
            CACHE_TIMEOUT,
            ErrorCodes
        )
        
        print("\n检查常量定义:")
        print(f"✓ FAMILY_VISIBILITY_CHOICES: {len(FAMILY_VISIBILITY_CHOICES)} 个选项")
        print(f"✓ FAMILY_STATUS_CHOICES: {len(FAMILY_STATUS_CHOICES)} 个选项")
        print(f"✓ CACHE_TIMEOUT: {len(CACHE_TIMEOUT)} 个配置")
        print(f"✓ ErrorCodes: {len([attr for attr in dir(ErrorCodes) if not attr.startswith('_')])} 个错误码")
        
        return True
    except Exception as e:
        print(f"❌ 常量测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试Django Ninja API模块...")
    
    success = True
    success &= test_imports()
    success &= test_schema_structure()
    success &= test_constants()
    
    if success:
        print("\n✅ 所有测试通过！Django Ninja API模块配置正确。")
    else:
        print("\n❌ 部分测试失败，请检查错误信息。")