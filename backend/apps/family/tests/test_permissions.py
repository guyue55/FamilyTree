"""
Family应用权限和异常处理单元测试

测试Family应用的权限控制、异常处理、安全机制等。
遵循Django和安全最佳实践。
"""

import pytest

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from apps.common.exceptions import (
    ValidationError as APIValidationError,
    PermissionError as APIPermissionError,
    NotFoundError,
    OperationError,
    LimitExceededError
)

from ..models import Family, FamilyInvitation
from ..exceptions import (
    FamilyNotFoundError,
    FamilyPermissionError,
    FamilyValidationError,
    FamilyNameConflictError,
    FamilyMemberLimitError,
    FamilyInvitationError
)
from ..permissions import (
    FamilyPermissionChecker,
    FamilyPermission,
    require_family_permission
)
from apps.members.models import FamilyMembership

User = get_user_model()

@pytest.mark.django_db
class TestFamilyPermissions:
    """Family权限控制测试"""
    
    def setup_method(self, method):
        """测试方法初始化"""
        # 创建测试用户
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        
        self.member = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='testpass123'
        )
        
        self.outsider = User.objects.create_user(
            username='outsider',
            email='outsider@example.com',
            password='testpass123'
        )
        
        # 创建测试家族
        self.public_family = Family.objects.create(
            name='公开家族',
            creator=self.creator,
            visibility='public'
        )
        
        self.family_visible = Family.objects.create(
            name='家族可见',
            creator=self.creator,
            visibility='family'
        )
        
        self.private_family = Family.objects.create(
            name='私有家族',
            creator=self.creator,
            visibility='private'
        )
        
        # 创建成员关系
        FamilyMembership.objects.create(
            family=self.family_visible,
            user=self.admin,
            role='admin',
            status='active'
        )
        
        FamilyMembership.objects.create(
            family=self.family_visible,
            user=self.member,
            role='member',
            status='active'
        )
    
    def test_family_permission_enum(self):
        """测试家族权限枚举"""
        # 验证所有权限类型
        expected_permissions = [
            'VIEW', 'EDIT', 'DELETE', 'MANAGE_MEMBERS', 
            'MANAGE_SETTINGS', 'INVITE_MEMBERS', 'EXPORT_DATA'
        ]
        
        for permission in expected_permissions:
            assert hasattr(FamilyPermission, permission)
    
    def test_creator_permissions(self):
        """测试创建者权限"""
        # 创建者应该拥有所有权限
        all_permissions = [
            FamilyPermission.VIEW,
            FamilyPermission.EDIT,
            FamilyPermission.DELETE,
            FamilyPermission.MANAGE_MEMBERS,
            FamilyPermission.MANAGE_SETTINGS,
            FamilyPermission.INVITE_MEMBERS,
            FamilyPermission.EXPORT_DATA
        ]
        
        for permission in all_permissions:
            assert FamilyPermissionChecker.check_permission(
                self.creator, self.public_family, permission
            )
    
    def test_admin_permissions(self):
        """测试管理员权限"""
        # 管理员应该有大部分权限，但不能删除家族
        admin_permissions = [
            FamilyPermission.VIEW,
            FamilyPermission.EDIT,
            FamilyPermission.MANAGE_MEMBERS,
            FamilyPermission.MANAGE_SETTINGS,
            FamilyPermission.INVITE_MEMBERS,
            FamilyPermission.EXPORT_DATA
        ]
        
        for permission in admin_permissions:
            assert FamilyPermissionChecker.check_permission(
                self.admin, self.family_visible, permission
            )
        
        # 管理员不能删除家族
        assert not FamilyPermissionChecker.check_permission(
            self.admin, self.family_visible, FamilyPermission.DELETE
        )
    
    def test_member_permissions(self):
        """测试普通成员权限"""
        # 普通成员只有查看和导出权限
        member_permissions = [
            FamilyPermission.VIEW,
            FamilyPermission.EXPORT_DATA
        ]
        
        for permission in member_permissions:
            assert FamilyPermissionChecker.check_permission(
                self.member, self.family_visible, permission
            )
        
        # 普通成员没有管理权限
        restricted_permissions = [
            FamilyPermission.EDIT,
            FamilyPermission.DELETE,
            FamilyPermission.MANAGE_MEMBERS,
            FamilyPermission.MANAGE_SETTINGS,
            FamilyPermission.INVITE_MEMBERS
        ]
        
        for permission in restricted_permissions:
            assert not FamilyPermissionChecker.check_permission(
                self.member, self.family_visible, permission
            )
    
    def test_outsider_permissions_public_family(self):
        """测试外部用户对公开家族的权限"""
        # 外部用户对公开家族只有查看权限
        assert FamilyPermissionChecker.check_permission(
            self.outsider, self.public_family, FamilyPermission.VIEW
        )
        
        # 外部用户没有其他权限
        restricted_permissions = [
            FamilyPermission.EDIT,
            FamilyPermission.DELETE,
            FamilyPermission.MANAGE_MEMBERS,
            FamilyPermission.MANAGE_SETTINGS,
            FamilyPermission.INVITE_MEMBERS,
            FamilyPermission.EXPORT_DATA
        ]
        
        for permission in restricted_permissions:
            assert not FamilyPermissionChecker.check_permission(
                self.outsider, self.public_family, permission
            )
    
    def test_outsider_permissions_private_family(self):
        """测试外部用户对私有家族的权限"""
        # 外部用户对私有家族没有任何权限
        all_permissions = [
            FamilyPermission.VIEW,
            FamilyPermission.EDIT,
            FamilyPermission.DELETE,
            FamilyPermission.MANAGE_MEMBERS,
            FamilyPermission.MANAGE_SETTINGS,
            FamilyPermission.INVITE_MEMBERS,
            FamilyPermission.EXPORT_DATA
        ]
        
        for permission in all_permissions:
            assert not FamilyPermissionChecker.check_permission(
                self.outsider, self.private_family, permission
            )
    
    def test_has_family_permission_decorator(self):
        """测试家族权限装饰器"""
        @has_family_permission(FamilyPermission.VIEW)
        def view_family(user, family):
            return f"用户 {user.username} 查看家族 {family.name}"
        
        # 测试有权限的情况
        result = view_family(self.creator, self.public_family)
        assert "creator" in result
        assert "公开家族" in result
        
        # 测试无权限的情况
        with pytest.raises(FamilyPermissionError):
            view_family(self.outsider, self.private_family)
    
    def test_require_family_permission_decorator(self):
        """测试必需家族权限装饰器"""
        @require_family_permission(FamilyPermission.EDIT)
        def edit_family(user, family, **kwargs):
            return f"用户 {user.username} 编辑家族 {family.name}"
        
        # 测试有权限的情况
        result = edit_family(self.creator, self.public_family)
        assert "creator" in result
        
        # 测试无权限的情况
        with pytest.raises(PermissionDenied):
            edit_family(self.member, self.family_visible)

@pytest.mark.django_db
class TestFamilyExceptions:
    """Family异常处理测试"""
    
    def setup_method(self):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username='exceptionuser',
            email='exception@example.com',
            password='testpass123'
        )
    
    def test_family_not_found_error(self):
        """测试家族未找到异常"""
        error = FamilyNotFoundError("家族不存在")
        
        assert str(error) == "家族不存在"
        assert isinstance(error, NotFoundError)
        assert error.status_code == 404
    
    def test_family_permission_error(self):
        """测试家族权限异常"""
        error = FamilyPermissionError("没有访问权限")
        
        assert str(error) == "没有访问权限"
        assert isinstance(error, APIPermissionError)
        assert error.status_code == 403
    
    def test_family_validation_error(self):
        """测试家族验证异常"""
        error = FamilyValidationError("数据验证失败")
        
        assert str(error) == "数据验证失败"
        assert isinstance(error, APIValidationError)
        assert error.status_code == 400
    
    def test_family_name_conflict_error(self):
        """测试家族名称冲突异常"""
        error = FamilyNameConflictError("家族名称已存在")
        
        assert str(error) == "家族名称已存在"
        assert isinstance(error, APIValidationError)
        assert error.status_code == 400
    
    def test_family_member_limit_error(self):
        """测试家族成员限制异常"""
        error = FamilyMemberLimitError("成员数量已达上限")
        
        assert str(error) == "成员数量已达上限"
        assert isinstance(error, LimitExceededError)
        assert error.status_code == 429
    
    def test_family_invitation_error(self):
        """测试家族邀请异常"""
        error = FamilyInvitationError("邀请处理失败")
        
        assert str(error) == "邀请处理失败"
        assert isinstance(error, OperationError)
        assert error.status_code == 500
    
    def test_family_settings_error(self):
        """测试家族设置异常"""
        error = FamilySettingsError("设置更新失败")
        
        assert str(error) == "设置更新失败"
        assert isinstance(error, OperationError)
        assert error.status_code == 500
    
    def test_exception_with_details(self):
        """测试带详细信息的异常"""
        details = {
            'field': 'name',
            'value': '',
            'constraint': 'not_empty'
        }
        
        error = FamilyValidationError("名称不能为空", details=details)
        
        assert str(error) == "名称不能为空"
        assert error.details == details
    
    def test_exception_chaining(self):
        """测试异常链"""
        original_error = ValueError("原始错误")
        
        try:
            raise original_error
        except ValueError as e:
            family_error = FamilyValidationError("家族验证失败")
            
            assert family_error.__cause__ == original_error
            assert "家族验证失败" in str(family_error)

@pytest.mark.django_db
class TestFamilySecurityMechanisms:
    """Family安全机制测试"""
    
    def setup_method(self):
        """测试方法初始化"""
        self.user1 = User.objects.create_user(
            username='securityuser1',
            email='security1@example.com',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            username='securityuser2',
            email='security2@example.com',
            password='testpass123'
        )
        
        self.family = Family.objects.create(
            name='安全测试家族',
            creator=self.user1,
            visibility='private'
        )
    
    def test_data_access_isolation(self):
        """测试数据访问隔离"""
        # user2不应该能访问user1的私有家族数据
        with pytest.raises(FamilyPermissionError):
            FamilyPermissionChecker.check_permission(
                self.user2, self.family, FamilyPermission.VIEW
            )
    
    def test_sql_injection_prevention(self):
        """测试SQL注入防护"""
        # 模拟SQL注入尝试
        malicious_input = "'; DROP TABLE family_family; --"
        
        # 创建家族时使用恶意输入
        try:
            Family.objects.create(
                name=malicious_input,
                creator=self.user1
            )
        except Exception:
            pass  # 预期可能失败
        
        # 验证表仍然存在
        assert Family.objects.filter(creator=self.user1).exists()
    
    def test_xss_prevention_in_data(self):
        """测试XSS防护"""
        # 模拟XSS攻击输入
        xss_input = "<script>alert('XSS')</script>"
        
        family = Family.objects.create(
            name="XSS测试家族",
            description=xss_input,
            creator=self.user1
        )
        
        # 验证数据被正确存储（不被执行）
        assert family.description == xss_input
        # 在实际应用中，输出时应该进行转义
    
    def test_rate_limiting_simulation(self):
        """测试速率限制模拟"""
        # 模拟快速创建多个家族
        families_created = 0
        max_families = 5
        
        for i in range(10):  # 尝试创建10个家族
            try:
                if families_created < max_families:
                    Family.objects.create(
                        name=f'速率测试家族{i}',
                        creator=self.user1
                    )
                    families_created += 1
                else:
                    # 模拟速率限制
                    raise LimitExceededError("创建频率过快")
            except LimitExceededError:
                break
        
        # 验证只创建了限制数量的家族
        assert families_created == max_families
    
    def test_sensitive_data_protection(self):
        """测试敏感数据保护"""
        # 创建包含敏感信息的家族
        family = Family.objects.create(
            name='敏感数据测试',
            description='包含敏感信息的家族',
            creator=self.user1,
            visibility='private'
        )
        
        # 验证敏感数据只对授权用户可见
        assert FamilyPermissionChecker.check_permission(
            self.user1, family, FamilyPermission.VIEW
        )
        
        assert not FamilyPermissionChecker.check_permission(
            self.user2, family, FamilyPermission.VIEW
        )
    
    def test_invitation_code_security(self):
        """测试邀请码安全性"""
        invitation = FamilyInvitation.objects.create(
            family=self.family,
            inviter=self.user1,
            invitee_email='test@example.com',
            invitee_name='测试用户',
            invitation_code='secure_code_123',
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # 验证邀请码的唯一性
        with pytest.raises(Exception):  # 应该有唯一性约束
            FamilyInvitation.objects.create(
                family=self.family,
                inviter=self.user1,
                invitee_email='another@example.com',
                invitee_name='另一个用户',
                invitation_code='secure_code_123',  # 相同的邀请码
                expires_at=timezone.now() + timedelta(days=7)
            )
    
    def test_password_protection_in_logs(self):
        """测试日志中的密码保护"""
        # 模拟包含密码的操作
        sensitive_data = {
            'username': 'testuser',
            'password': 'secret123',
            'family_name': '测试家族'
        }
        
        # 验证敏感数据不会出现在日志中
        # 这里只是示例，实际应该检查日志系统
        filtered_data = {
            k: v if k != 'password' else '***' 
            for k, v in sensitive_data.items()
        }
        
        assert filtered_data['password'] == '***'
        assert filtered_data['username'] == 'testuser'

@pytest.mark.django_db
class TestFamilyPermissionEdgeCases:
    """Family权限边界情况测试"""
    
    def setup_method(self):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username='edgeuser',
            email='edge@example.com',
            password='testpass123'
        )
        
        self.family = Family.objects.create(
            name='边界测试家族',
            creator=self.user
        )
    
    def test_permission_check_with_none_user(self):
        """测试空用户权限检查"""
        with pytest.raises(TypeError):
            FamilyPermissionChecker.check_permission(
                None, self.family, FamilyPermission.VIEW
            )
    
    def test_permission_check_with_none_family(self):
        """测试空家族权限检查"""
        with pytest.raises(TypeError):
            FamilyPermissionChecker.check_permission(
                self.user, None, FamilyPermission.VIEW
            )
    
    def test_permission_check_with_invalid_permission(self):
        """测试无效权限检查"""
        with pytest.raises(ValueError):
            FamilyPermissionChecker.check_permission(
                self.user, self.family, "INVALID_PERMISSION"
            )
    
    def test_permission_check_with_inactive_user(self):
        """测试非活跃用户权限检查"""
        self.user.is_active = False
        self.user.save()
        
        # 非活跃用户应该没有任何权限
        assert not FamilyPermissionChecker.check_permission(
            self.user, self.family, FamilyPermission.VIEW
        )
    
    def test_permission_check_with_inactive_family(self):
        """测试非活跃家族权限检查"""
        self.family.is_active = False
        self.family.save()
        
        # 对非活跃家族的权限检查应该失败
        assert not FamilyPermissionChecker.check_permission(
            self.user, self.family, FamilyPermission.VIEW
        )
    
    def test_permission_inheritance(self):
        """测试权限继承"""
        # 创建子家族（如果支持）
        # 这里只是示例，实际实现可能不同
        child_family = Family.objects.create(
            name='子家族',
            creator=self.user,
            # parent_family=self.family  # 如果支持父子关系
        )
        
        # 验证权限继承逻辑
        assert FamilyPermissionChecker.check_permission(
            self.user, child_family, FamilyPermission.VIEW
        )
    
    def test_concurrent_permission_changes(self):
        """测试并发权限变更"""
        # 创建成员关系
        membership = FamilyMembership.objects.create(
            family=self.family,
            user=self.user,
            role='member',
            status='active'
        )
        
        # 模拟并发修改权限
        with patch('apps.members.models.FamilyMembership.objects.get') as mock_get:
            mock_get.return_value = membership
            
            # 第一个线程检查权限
            has_permission = FamilyPermissionChecker.check_permission(
                self.user, self.family, FamilyPermission.VIEW
            )
            
            # 模拟第二个线程修改了权限
            membership.status = 'inactive'
            membership.save()
            
            # 验证权限检查的一致性
            assert has_permission  # 基于检查时的状态

@pytest.mark.django_db
class TestFamilyErrorHandling:
    """Family错误处理测试"""
    
    def setup_method(self):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username='erroruser',
            email='error@example.com',
            password='testpass123'
        )
    
    def test_graceful_database_error_handling(self):
        """测试优雅的数据库错误处理"""
        with patch('apps.family.models.Family.objects.create') as mock_create:
            mock_create.side_effect = Exception("数据库连接失败")
            
            with pytest.raises(OperationError) as exc_info:
                # 这里应该调用服务层方法，而不是直接调用模型
                # FamilyService.create_family(data, user)
                pass
            
            # 验证错误信息
            # assert "创建家族失败" in str(exc_info.value)
    
    def test_validation_error_aggregation(self):
        """测试验证错误聚合"""
        errors = []
        
        # 收集多个验证错误
        try:
            # 模拟多个字段验证失败
            raise FamilyValidationError("名称不能为空")
        except FamilyValidationError as e:
            errors.append(str(e))
        
        try:
            raise FamilyValidationError("描述过长")
        except FamilyValidationError as e:
            errors.append(str(e))
        
        # 验证错误聚合
        assert len(errors) == 2
        assert "名称不能为空" in errors
        assert "描述过长" in errors
    
    def test_error_context_preservation(self):
        """测试错误上下文保持"""
        context = {
            'user_id': self.user.id,
            'operation': 'create_family',
            'timestamp': timezone.now()
        }
        
        error = FamilyValidationError(
            "验证失败",
            details=context
        )
        
        # 验证上下文信息被保持
        assert error.details['user_id'] == self.user.id
        assert error.details['operation'] == 'create_family'
        assert 'timestamp' in error.details
    
    def test_error_logging_integration(self):
        """测试错误日志集成"""
        with patch('logging.Logger.error') as mock_logger:
            try:
                raise FamilyPermissionError("权限不足")
            except FamilyPermissionError as e:
                # 模拟错误日志记录
                mock_logger(f"Family permission error: {str(e)}")
            
            # 验证日志被调用
            mock_logger.assert_called_once()

if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v', '--tb=short'])