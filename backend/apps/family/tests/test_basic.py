"""
Family应用测试示例

简单的测试示例，用于验证测试环境配置
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class TestFamilyBasic(TestCase):
    """基础测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """测试用户创建"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_basic_assertion(self):
        """测试基本断言"""
        self.assertEqual(1 + 1, 2)
        self.assertTrue(True)
        self.assertFalse(False)

@pytest.mark.django_db
class TestFamilyPytest:
    """Pytest风格的测试类"""
    
    def test_simple_assertion(self):
        """简单断言测试"""
        assert 1 + 1 == 2
        assert "hello" in "hello world"
    
    def test_user_creation_pytest(self):
        """使用pytest创建用户"""
        user = User.objects.create_user(
            username='pytestuser',
            email='pytest@example.com',
            password='testpass123'
        )
        
        assert user.username == 'pytestuser'
        assert user.email == 'pytest@example.com'
        assert user.check_password('testpass123')