"""
Family应用模型层单元测试

测试Family应用的数据模型，包括字段验证、模型方法、关系处理、约束检查等。
遵循Django测试最佳实践。
"""

import pytest

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from ..models import Family, FamilySettings, FamilyInvitation
from apps.members.models import FamilyMembership

User = get_user_model()

@pytest.mark.django_db
class TestFamilyModel:
    """Family模型测试"""
    
    def setup_method(self, method):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone='13800138001',
            first_name='Test',
            last_name='User'
        )
        
        self.family_data = {
            'name': '测试家族',
            'description': '这是一个测试家族',
            'creator': self.user,
            'visibility': 'family',
            'allow_join': True,
            'tags': '测试,家族',
            'origin_location': '北京',
            'motto': '团结友爱'
        }
    
    def test_family_creation_success(self):
        """测试家族创建成功"""
        family = Family.objects.create(**self.family_data)
        
        assert family.name == self.family_data['name']
        assert family.description == self.family_data['description']
        assert family.creator == self.user
        assert family.visibility == 'family'
        assert family.is_active is True
        assert family.allow_join is True
        assert family.member_count == 1
        assert family.generation_count == 1
        assert family.tags == '测试,家族'
        assert family.origin_location == '北京'
        assert family.motto == '团结友爱'
        
        # 验证自动设置的字段
        assert family.created_at is not None
        assert family.updated_at is not None
        assert family.created_at <= family.updated_at
    
    def test_family_str_representation(self):
        """测试家族字符串表示"""
        family = Family.objects.create(**self.family_data)
        assert str(family) == '测试家族'
    
    def test_family_name_validation(self):
        """测试家族名称验证"""
        # 测试空名称
        with pytest.raises(ValidationError):
            family = Family(**self.family_data)
            family.name = ''
            family.full_clean()
        
        # 测试名称过长
        with pytest.raises(ValidationError):
            family = Family(**self.family_data)
            family.name = 'A' * 101  # 超过100字符
            family.full_clean()
        
        # 测试名称包含特殊字符
        family = Family(**self.family_data)
        family.name = '测试家族@#$%'
        family.full_clean()  # 应该通过
    
    def test_family_description_validation(self):
        """测试家族描述验证"""
        # 测试描述过长
        with pytest.raises(ValidationError):
            family = Family(**self.family_data)
            family.description = 'A' * 1001  # 超过1000字符
            family.full_clean()
        
        # 测试空描述
        family = Family(**self.family_data)
        family.description = ''
        family.full_clean()  # 应该通过
    
    def test_family_visibility_choices(self):
        """测试家族可见性选择"""
        valid_choices = ['public', 'family', 'private']
        
        for choice in valid_choices:
            family = Family(**self.family_data)
            family.visibility = choice
            family.full_clean()  # 应该通过
        
        # 测试无效选择
        with pytest.raises(ValidationError):
            family = Family(**self.family_data)
            family.visibility = 'invalid_choice'
            family.full_clean()
    
    def test_family_tags_handling(self):
        """测试家族标签处理"""
        family = Family.objects.create(**self.family_data)
        
        # 测试获取标签列表
        tags_list = family.get_tags_list()
        assert tags_list == ['测试', '家族']
        
        # 测试设置标签列表
        new_tags = ['新标签', '更新', '测试']
        family.set_tags_list(new_tags)
        assert family.tags == '新标签,更新,测试'
        
        # 测试空标签
        family.tags = ''
        assert family.get_tags_list() == []
        
        # 测试None标签
        family.tags = None
        assert family.get_tags_list() == []
    
    def test_family_member_count_management(self):
        """测试家族成员数量管理"""
        family = Family.objects.create(**self.family_data)
        
        # 初始成员数应该为1（创建者）
        assert family.member_count == 1
        
        # 创建第一个成员记录
        from apps.members.models import Member
        member1 = Member.objects.create(
            family_id=family.id,
            name='测试成员1',
            gender='male',
            creator_id=self.user.id
        )
        
        # 创建成员关系
        membership1 = FamilyMembership.objects.create(
            family_id=family.id,
            user_id=self.user.id,
            member_id=member1.id,
            role='admin',
            status='active'
        )
        
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            phone='13800138002'
        )
        
        # 创建第二个成员记录
        member2 = Member.objects.create(
            family_id=family.id,
            name='测试成员2',
            gender='female',
            creator_id=self.user.id
        )
        
        membership2 = FamilyMembership.objects.create(
            family_id=family.id,
            user_id=user2.id,
            member_id=member2.id,
            role='member',
            status='active'
        )
        
        # 更新成员数量
        family.update_member_count()
        assert family.member_count == 3  # 1(创建者) + 2(新增成员)
        
        # 删除一个成员
        membership2.delete()
        family.update_member_count()
        assert family.member_count == 2  # 1(创建者) + 1(剩余成员)
    
    def test_family_avatar_upload(self):
        """测试家族头像上传"""
        # 创建模拟图片文件
        avatar_file = SimpleUploadedFile(
            "avatar.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )
        
        family = Family.objects.create(
            **self.family_data,
            avatar=avatar_file
        )
        
        assert family.avatar is not None
        assert 'avatar.jpg' in family.avatar.name
    
    def test_family_cover_image_upload(self):
        """测试家族封面图片上传"""
        # 创建模拟图片文件
        cover_file = SimpleUploadedFile(
            "cover.jpg",
            b"fake_cover_content",
            content_type="image/jpeg"
        )
        
        family = Family.objects.create(
            **self.family_data,
            cover_image=cover_file
        )
        
        assert family.cover_image is not None
        assert 'cover.jpg' in family.cover_image.name
    
    def test_family_unique_name_constraint(self):
        """测试家族名称唯一性约束"""
        # 创建第一个家族
        Family.objects.create(**self.family_data)
        
        # 尝试创建同名家族
        with pytest.raises(IntegrityError):
            Family.objects.create(**self.family_data)
    
    def test_family_creator_foreign_key(self):
        """测试家族创建者外键关系"""
        family = Family.objects.create(**self.family_data)
        
        # 验证外键关系
        assert family.creator == self.user
        assert family.creator_id == self.user.id
        
        # 测试级联删除保护
        with pytest.raises(Exception):  # 应该有保护机制
            self.user.delete()
    
    def test_family_settings_property(self):
        """测试家族设置属性"""
        family = Family.objects.create(**self.family_data)
        
        # 创建家族设置
        settings = FamilySettings.objects.create(
            family=family,
            tree_layout='horizontal',
            show_photos=False
        )
        
        # 测试属性访问
        assert family.settings == settings
        assert family.settings.tree_layout == 'horizontal'
        assert family.settings.show_photos is False

@pytest.mark.django_db
class TestFamilySettingsModel:
    """FamilySettings模型测试"""
    
    def setup_method(self, method):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username='settingsuser',
            email='settings@example.com',
            password='testpass123'
        )
        
        self.family = Family.objects.create(
            name='设置测试家族',
            creator=self.user
        )
    
    def test_family_settings_creation_with_defaults(self):
        """测试家族设置创建及默认值"""
        settings = FamilySettings.objects.create(family=self.family)
        
        # 验证默认值
        assert settings.tree_layout == 'vertical'
        assert settings.show_photos is True
        assert settings.show_birth_dates is True
        assert settings.show_death_dates is True
        assert settings.show_occupation is True
        assert settings.theme == 'default'
        assert settings.font_family == 'default'
        assert settings.privacy_level == 'family'
        assert settings.require_approval is True
        assert settings.allow_public_search is False
        assert settings.enable_notifications is True
        assert settings.email_notifications is True
        assert settings.sms_notifications is False
    
    def test_family_settings_str_representation(self):
        """测试家族设置字符串表示"""
        settings = FamilySettings.objects.create(family=self.family)
        expected_str = f'{self.family.name} - 设置'
        assert str(settings) == expected_str
    
    def test_family_settings_tree_layout_choices(self):
        """测试家族设置树形布局选择"""
        valid_layouts = ['vertical', 'horizontal', 'circular', 'fan']
        
        for layout in valid_layouts:
            settings = FamilySettings(family=self.family, tree_layout=layout)
            settings.full_clean()  # 应该通过
        
        # 测试无效布局
        with pytest.raises(ValidationError):
            settings = FamilySettings(family=self.family, tree_layout='invalid')
            settings.full_clean()
    
    def test_family_settings_theme_choices(self):
        """测试家族设置主题选择"""
        valid_themes = ['default', 'classic', 'modern', 'elegant']
        
        for theme in valid_themes:
            settings = FamilySettings(family=self.family, theme=theme)
            settings.full_clean()  # 应该通过
    
    def test_family_settings_privacy_level_choices(self):
        """测试家族设置隐私级别选择"""
        valid_levels = ['public', 'family', 'private']
        
        for level in valid_levels:
            settings = FamilySettings(family=self.family, privacy_level=level)
            settings.full_clean()  # 应该通过
    
    def test_family_settings_one_to_one_relationship(self):
        """测试家族设置一对一关系"""
        settings1 = FamilySettings.objects.create(family=self.family)
        
        # 尝试为同一个家族创建第二个设置
        with pytest.raises(IntegrityError):
            FamilySettings.objects.create(family=self.family)
    
    def test_family_settings_cascade_delete(self):
        """测试家族设置级联删除"""
        settings = FamilySettings.objects.create(family=self.family)
        settings_id = settings.id
        
        # 删除家族
        self.family.delete()
        
        # 验证设置也被删除
        assert not FamilySettings.objects.filter(id=settings_id).exists()

@pytest.mark.django_db
class TestFamilyInvitationModel:
    """FamilyInvitation模型测试"""
    
    def setup_method(self, method):
        """测试方法初始化"""
        self.inviter = User.objects.create_user(
            username='inviter',
            email='inviter@example.com',
            password='testpass123'
        )
        
        self.invitee = User.objects.create_user(
            username='invitee',
            email='invitee@example.com',
            password='testpass123'
        )
        
        self.family = Family.objects.create(
            name='邀请测试家族',
            creator=self.inviter
        )
        
        self.invitation_data = {
            'family': self.family,
            'inviter': self.inviter,
            'invitee_email': 'newuser@example.com',
            'invitee_name': '新用户',
            'invitation_code': 'test_invitation_code',
            'expires_at': timezone.now() + timedelta(days=7),
            'message': '欢迎加入我们的家族'
        }
    
    def test_family_invitation_creation_success(self):
        """测试家族邀请创建成功"""
        invitation = FamilyInvitation.objects.create(**self.invitation_data)
        
        assert invitation.family == self.family
        assert invitation.inviter == self.inviter
        assert invitation.invitee_email == 'newuser@example.com'
        assert invitation.invitee_name == '新用户'
        assert invitation.status == 'pending'
        assert invitation.invitation_code == 'test_invitation_code'
        assert invitation.message == '欢迎加入我们的家族'
        assert invitation.created_at is not None
        assert invitation.expires_at > timezone.now()
    
    def test_family_invitation_str_representation(self):
        """测试家族邀请字符串表示"""
        invitation = FamilyInvitation.objects.create(**self.invitation_data)
        expected_str = f'{self.family.name} - 邀请 新用户'
        assert str(invitation) == expected_str
    
    def test_family_invitation_status_choices(self):
        """测试家族邀请状态选择"""
        valid_statuses = ['pending', 'accepted', 'rejected', 'expired']
        
        for status in valid_statuses:
            invitation = FamilyInvitation(**self.invitation_data)
            invitation.status = status
            invitation.full_clean()  # 应该通过
        
        # 测试无效状态
        with pytest.raises(ValidationError):
            invitation = FamilyInvitation(**self.invitation_data)
            invitation.status = 'invalid_status'
            invitation.full_clean()
    
    def test_family_invitation_email_validation(self):
        """测试家族邀请邮箱验证"""
        # 测试有效邮箱
        invitation = FamilyInvitation(**self.invitation_data)
        invitation.invitee_email = 'valid@example.com'
        invitation.full_clean()  # 应该通过
        
        # 测试无效邮箱
        with pytest.raises(ValidationError):
            invitation = FamilyInvitation(**self.invitation_data)
            invitation.invitee_email = 'invalid_email'
            invitation.full_clean()
    
    def test_family_invitation_phone_validation(self):
        """测试家族邀请手机号验证"""
        # 测试有效手机号
        invitation = FamilyInvitation(**self.invitation_data)
        invitation.invitee_phone = '+86-13800138000'
        invitation.full_clean()  # 应该通过
        
        # 测试无效手机号格式
        with pytest.raises(ValidationError):
            invitation = FamilyInvitation(**self.invitation_data)
            invitation.invitee_phone = '123'
            invitation.full_clean()
    
    def test_family_invitation_code_uniqueness(self):
        """测试家族邀请码唯一性"""
        # 创建第一个邀请
        FamilyInvitation.objects.create(**self.invitation_data)
        
        # 尝试创建相同邀请码的邀请
        with pytest.raises(IntegrityError):
            invitation_data2 = self.invitation_data.copy()
            invitation_data2['invitee_email'] = 'another@example.com'
            FamilyInvitation.objects.create(**invitation_data2)
    
    def test_family_invitation_is_expired_method(self):
        """测试家族邀请过期检查方法"""
        # 创建未过期的邀请
        invitation = FamilyInvitation.objects.create(**self.invitation_data)
        assert not invitation.is_expired()
        
        # 创建已过期的邀请
        expired_data = self.invitation_data.copy()
        expired_data['expires_at'] = timezone.now() - timedelta(days=1)
        expired_data['invitation_code'] = 'expired_code'
        expired_invitation = FamilyInvitation.objects.create(**expired_data)
        assert expired_invitation.is_expired()
    
    def test_family_invitation_accept_method(self):
        """测试家族邀请接受方法"""
        invitation = FamilyInvitation.objects.create(**self.invitation_data)
        
        # 接受邀请
        invitation.accept(self.invitee)
        
        assert invitation.status == 'accepted'
        assert invitation.invitee == self.invitee
        assert invitation.processed_at is not None
        
        # 验证不能重复接受
        with pytest.raises(Exception):
            invitation.accept(self.invitee)
    
    def test_family_invitation_reject_method(self):
        """测试家族邀请拒绝方法"""
        invitation = FamilyInvitation.objects.create(**self.invitation_data)
        
        # 拒绝邀请
        rejection_reason = '暂时不想加入'
        invitation.reject(self.invitee, rejection_reason)
        
        assert invitation.status == 'rejected'
        assert invitation.invitee == self.invitee
        assert invitation.rejection_reason == rejection_reason
        assert invitation.processed_at is not None
    
    def test_family_invitation_expired_status_update(self):
        """测试家族邀请过期状态更新"""
        # 创建即将过期的邀请
        near_expired_data = self.invitation_data.copy()
        near_expired_data['expires_at'] = timezone.now() + timedelta(minutes=1)
        invitation = FamilyInvitation.objects.create(**near_expired_data)
        
        # 模拟时间过去
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = timezone.now() + timedelta(hours=1)
            
            # 检查过期状态
            assert invitation.is_expired()
    
    def test_family_invitation_foreign_key_relationships(self):
        """测试家族邀请外键关系"""
        invitation = FamilyInvitation.objects.create(**self.invitation_data)
        
        # 验证外键关系
        assert invitation.family == self.family
        assert invitation.inviter == self.inviter
        
        # 测试级联删除行为
        family_id = self.family.id
        self.family.delete()
        
        # 验证邀请也被删除
        assert not FamilyInvitation.objects.filter(family_id=family_id).exists()

@pytest.mark.django_db
class TestFamilyModelConstraints:
    """Family模型约束测试"""
    
    def setup_method(self, method):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username='constraintuser',
            email='constraint@example.com',
            password='testpass123'
        )
    
    def test_family_name_length_constraint(self):
        """测试家族名称长度约束"""
        # 测试最大长度
        max_length_name = 'A' * 100
        family = Family.objects.create(
            name=max_length_name,
            creator=self.user
        )
        assert len(family.name) == 100
        
        # 测试超过最大长度
        with pytest.raises(Exception):
            Family.objects.create(
                name='A' * 101,
                creator=self.user
            )
    
    def test_family_description_length_constraint(self):
        """测试家族描述长度约束"""
        # 测试最大长度
        max_length_desc = 'A' * 1000
        family = Family.objects.create(
            name='描述长度测试',
            description=max_length_desc,
            creator=self.user
        )
        assert len(family.description) == 1000
    
    def test_family_member_count_constraint(self):
        """测试家族成员数量约束"""
        family = Family.objects.create(
            name='成员数量约束测试',
            creator=self.user
        )
        
        # 成员数量不能为负数
        with pytest.raises(Exception):
            family.member_count = -1
            family.save()
    
    def test_family_generation_count_constraint(self):
        """测试家族世代数量约束"""
        family = Family.objects.create(
            name='世代数量约束测试',
            creator=self.user
        )
        
        # 世代数量不能为负数
        with pytest.raises(Exception):
            family.generation_count = -1
            family.save()

@pytest.mark.django_db
class TestFamilyModelMethods:
    """Family模型方法测试"""
    
    def setup_method(self):
        """测试方法初始化"""
        self.user = User.objects.create_user(
            username='methoduser',
            email='method@example.com',
            password='testpass123'
        )
        
        self.family = Family.objects.create(
            name='方法测试家族',
            creator=self.user,
            tags='测试,方法,家族'
        )
    
    def test_get_tags_list_method(self):
        """测试获取标签列表方法"""
        tags_list = self.family.get_tags_list()
        assert tags_list == ['测试', '方法', '家族']
        
        # 测试空标签
        self.family.tags = ''
        assert self.family.get_tags_list() == []
        
        # 测试None标签
        self.family.tags = None
        assert self.family.get_tags_list() == []
    
    def test_set_tags_list_method(self):
        """测试设置标签列表方法"""
        new_tags = ['新标签', '更新', '测试']
        self.family.set_tags_list(new_tags)
        
        assert self.family.tags == '新标签,更新,测试'
        assert self.family.get_tags_list() == new_tags
        
        # 测试空列表
        self.family.set_tags_list([])
        assert self.family.tags == ''
    
    def test_update_member_count_method(self):
        """测试更新成员数量方法"""
        # 创建成员关系
        FamilyMembership.objects.create(
            family=self.family,
            user=self.user,
            role='admin',
            status='active'
        )
        
        user2 = User.objects.create_user(
            username='member2',
            email='member2@example.com',
            password='testpass123'
        )
        
        FamilyMembership.objects.create(
            family=self.family,
            user=user2,
            role='member',
            status='active'
        )
        
        # 更新成员数量
        self.family.update_member_count()
        assert self.family.member_count == 2
    
    def test_family_model_save_method(self):
        """测试家族模型保存方法"""
        original_updated_at = self.family.updated_at
        
        # 等待一小段时间确保时间戳不同
        import time
        time.sleep(0.01)
        
        # 更新家族
        self.family.description = '更新后的描述'
        self.family.save()
        
        # 验证updated_at字段被更新
        assert self.family.updated_at > original_updated_at

if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v', '--tb=short'])