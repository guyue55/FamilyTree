"""
API测试工具

提供标准化的API测试功能。
遵循Django测试最佳实践。
"""

import json
from typing import Dict, Any, Optional, Union
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from .api_config import api_config

User = get_user_model()


class APITestCase(TestCase):
    """API测试基类"""
    
    def setUp(self):
        """测试初始化"""
        self.client = Client()
        self.api_base_url = "/api/v1"
        self.test_user = None
        self.auth_token = None
    
    def create_test_user(self, **kwargs) -> User:
        """创建测试用户"""
        default_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        default_data.update(kwargs)
        
        user = User.objects.create_user(**default_data)
        self.test_user = user
        return user
    
    def authenticate_user(self, user: Optional[User] = None) -> str:
        """用户认证，获取JWT token"""
        if user is None:
            user = self.test_user or self.create_test_user()
        
        # 登录获取token
        login_data = {
            'username': user.username,
            'password': 'testpass123'
        }
        
        response = self.api_post('/auth/login', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        token = response.json()['data']['access_token']
        self.auth_token = token
        return token
    
    def get_auth_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """获取认证头"""
        if token is None:
            token = self.auth_token or self.authenticate_user()
        
        return {
            'HTTP_AUTHORIZATION': f'Bearer {token}',
            'HTTP_X_REQUEST_ID': f'test_{self.id()}'
        }
    
    def api_request(
        self, 
        method: str, 
        url: str, 
        data: Optional[Dict[str, Any]] = None,
        authenticated: bool = True,
        **kwargs
    ) -> Any:
        """发送API请求"""
        if not url.startswith('/'):
            url = f"{self.api_base_url}/{url.lstrip('/')}"
        
        headers = kwargs.pop('headers', {})
        if authenticated:
            headers.update(self.get_auth_headers())
        
        # 设置Content-Type
        if data is not None and method.upper() in ['POST', 'PUT', 'PATCH']:
            headers['CONTENT_TYPE'] = 'application/json'
            data = json.dumps(data)
        
        client_method = getattr(self.client, method.lower())
        return client_method(url, data=data, **headers, **kwargs)
    
    def api_get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """GET请求"""
        if params:
            url += '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
        return self.api_request('GET', url, **kwargs)
    
    def api_post(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """POST请求"""
        return self.api_request('POST', url, data=data, **kwargs)
    
    def api_put(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """PUT请求"""
        return self.api_request('PUT', url, data=data, **kwargs)
    
    def api_patch(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """PATCH请求"""
        return self.api_request('PATCH', url, data=data, **kwargs)
    
    def api_delete(self, url: str, **kwargs) -> Any:
        """DELETE请求"""
        return self.api_request('DELETE', url, **kwargs)
    
    def assert_api_success(self, response: Any, expected_code: int = 200) -> Dict[str, Any]:
        """断言API成功响应"""
        self.assertEqual(response.status_code, expected_code)
        
        data = response.json()
        self.assertIn('code', data)
        self.assertIn('message', data)
        self.assertIn('data', data)
        self.assertIn('timestamp', data)
        self.assertIn('request_id', data)
        
        self.assertEqual(data['code'], expected_code)
        return data
    
    def assert_api_error(
        self, 
        response: Any, 
        expected_status: int = 400,
        expected_code: Optional[int] = None
    ) -> Dict[str, Any]:
        """断言API错误响应"""
        self.assertEqual(response.status_code, expected_status)
        
        data = response.json()
        self.assertIn('code', data)
        self.assertIn('message', data)
        self.assertIn('timestamp', data)
        self.assertIn('request_id', data)
        
        if expected_code:
            self.assertEqual(data['code'], expected_code)
        
        return data
    
    def assert_validation_error(self, response: Any, field: Optional[str] = None) -> Dict[str, Any]:
        """断言验证错误响应"""
        data = self.assert_api_error(response, 422, 422)
        
        self.assertIn('data', data)
        self.assertIn('errors', data['data'])
        
        if field:
            errors = data['data']['errors']
            field_errors = [error for error in errors if error.get('field') == field]
            self.assertTrue(len(field_errors) > 0, f"No validation error found for field: {field}")
        
        return data
    
    def assert_pagination_response(self, response: Any) -> Dict[str, Any]:
        """断言分页响应"""
        data = self.assert_api_success(response)
        
        self.assertIn('data', data)
        response_data = data['data']
        
        self.assertIn('items', response_data)
        self.assertIn('pagination', response_data)
        
        pagination = response_data['pagination']
        required_fields = ['page', 'page_size', 'total', 'pages', 'has_next', 'has_prev']
        for field in required_fields:
            self.assertIn(field, pagination)
        
        return data
    
    def create_test_data(self, model_class, count: int = 1, **kwargs) -> Union[Any, list]:
        """创建测试数据"""
        objects = []
        for i in range(count):
            data = kwargs.copy()
            # 为重复字段添加序号
            for key, value in data.items():
                if isinstance(value, str) and '{i}' in value:
                    data[key] = value.format(i=i)
            
            obj = model_class.objects.create(**data)
            objects.append(obj)
        
        return objects[0] if count == 1 else objects


class APIPerformanceTestCase(APITestCase):
    """API性能测试基类"""
    
    def setUp(self):
        super().setUp()
        self.performance_threshold = 1.0  # 1秒
    
    def assert_response_time(self, response: Any, max_time: Optional[float] = None) -> None:
        """断言响应时间"""
        if max_time is None:
            max_time = self.performance_threshold
        
        # 从响应头获取处理时间
        process_time_header = response.get('X-Process-Time', '0s')
        process_time = float(process_time_header.rstrip('s'))
        
        self.assertLessEqual(
            process_time, 
            max_time, 
            f"Response time {process_time}s exceeds threshold {max_time}s"
        )
    
    def benchmark_endpoint(self, method: str, url: str, iterations: int = 10) -> Dict[str, float]:
        """基准测试端点"""
        import time
        
        times = []
        for _ in range(iterations):
            start_time = time.time()
            response = self.api_request(method, url)
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            times.append(end_time - start_time)
        
        return {
            'min': min(times),
            'max': max(times),
            'avg': sum(times) / len(times),
            'total': sum(times)
        }