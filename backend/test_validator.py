"""
测试 @field_validator 是否必须使用 @classmethod
"""
from pydantic import BaseModel, field_validator, ValidationInfo
from typing import Any


class TestWithClassmethod(BaseModel):
    """使用 @classmethod 的正确示例"""
    email: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str, info: ValidationInfo) -> str:
        """正确的验证器写法"""
        if '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v


class TestWithoutClassmethod(BaseModel):
    """不使用 @classmethod 的错误示例"""
    email: str
    
    @field_validator('email')
    def validate_email(self, v: str, info: ValidationInfo) -> str:
        """错误的验证器写法 - 缺少 @classmethod"""
        if '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v


if __name__ == "__main__":
    # 测试正确的写法
    print("测试正确的写法（使用 @classmethod）:")
    try:
        correct = TestWithClassmethod(email="test@example.com")
        print(f"✓ 成功创建: {correct.email}")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    try:
        correct_invalid = TestWithClassmethod(email="invalid-email")
        print(f"✓ 成功创建: {correct_invalid.email}")
    except Exception as e:
        print(f"✓ 验证器正常工作: {e}")
    
    print("\n测试错误的写法（不使用 @classmethod）:")
    try:
        wrong = TestWithoutClassmethod(email="test@example.com")
        print(f"✓ 成功创建: {wrong.email}")
    except Exception as e:
        print(f"✗ 错误: {e}")